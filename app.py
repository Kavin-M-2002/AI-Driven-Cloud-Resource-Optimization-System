import json
import boto3
import os
import zipfile
import tensorflow as tf
import numpy as np
import joblib

# ========== CONFIG ==========
BUCKET_NAME = "cloud-resource-forecast-models"
MODEL_ZIP_KEY = "deploy_bundle.zip"

ZIP_PATH = "/tmp/model_bundle.zip"
MODEL_DIR = "/tmp/lstm_lambda_ready"
SCALER_PATH = "/tmp/cpu_scaler.pkl"

EXPECTED_TIMESTEPS = 24
EXPECTED_FEATURES = 6

# Silence TensorFlow logs
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"

# ========== AWS CLIENT ==========
s3 = boto3.client("s3")
cloudwatch = boto3.client("cloudwatch")

model = None
scaler = None

# ========== CLOUDWATCH PUSH ==========
def push_prediction(value):
    try:
        cloudwatch.put_metric_data(
            Namespace="MLForecast",
            MetricData=[
                {
                    "MetricName": "PredictedCPU",
                    "Value": float(value),
                    "Unit": "Percent"
                }
            ]
        )
        print("Pushed PredictedCPU to CloudWatch:", value)
    except Exception as e:
        print("CloudWatch push failed:", str(e))

# ========== COLD START LOADER ==========
def prepare_artifacts():
    global model, scaler

    if model is not None and scaler is not None:
        return

    print("Cold start — loading model bundle")

    # Download bundle
    if not os.path.exists(ZIP_PATH):
        s3.download_file(BUCKET_NAME, MODEL_ZIP_KEY, ZIP_PATH)
        print("Model bundle downloaded")

    # Extract
    if not os.path.exists(MODEL_DIR) or not os.path.exists(SCALER_PATH):
        with zipfile.ZipFile(ZIP_PATH, "r") as zip_ref:
            zip_ref.extractall("/tmp")
        print("Model bundle extracted")

    # Validate files
    if not os.path.exists(MODEL_DIR):
        raise RuntimeError(f"Model folder missing: {MODEL_DIR}")

    if not os.path.exists(SCALER_PATH):
        raise RuntimeError(f"Scaler missing: {SCALER_PATH}")

    # Load artifacts
    print("Loading TensorFlow model...")
    model = tf.keras.models.load_model(MODEL_DIR, compile=False)

    print("Loading scaler...")
    scaler = joblib.load(SCALER_PATH)

    print("Artifacts loaded successfully")

# ========== HANDLER ==========
def lambda_handler(event, context):
    try:
        prepare_artifacts()

        # Parse body
        body = event.get("body")
        if isinstance(body, str):
            body = json.loads(body)

        if not body or "metrics" not in body:
            return {
                "statusCode": 400,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({"error": "Missing 'metrics'"})
            }

        # Convert input
        X = np.array(body["metrics"], dtype=np.float32)

        # ========== VALIDATION ==========
        if X.ndim != 2:
            return {
                "statusCode": 400,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({"error": "metrics must be 2D: [timesteps][features]"})
            }

        if X.shape[0] != EXPECTED_TIMESTEPS:
            return {
                "statusCode": 400,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({
                    "error": f"Expected {EXPECTED_TIMESTEPS} timesteps, got {X.shape[0]}"
                })
            }

        if X.shape[1] != EXPECTED_FEATURES:
            return {
                "statusCode": 400,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({
                    "error": f"Expected {EXPECTED_FEATURES} features, got {X.shape[1]}"
                })
            }

        # ========== SCALE ==========
        X_flat = X.reshape(-1, EXPECTED_FEATURES)
        X_scaled = scaler.transform(X_flat)
        X_scaled = X_scaled.reshape(1, EXPECTED_TIMESTEPS, EXPECTED_FEATURES)

        # ========== PREDICT ==========
        prediction = model.predict(X_scaled, verbose=0)
        pred_value = float(prediction[0][0])

        # ========== PUSH TO CLOUDWATCH ==========
        push_prediction(pred_value)

        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({
                "predicted_cpu": pred_value
            })
        }

    except Exception as e:
        print("ERROR:", str(e))
        return {
            "statusCode": 500,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"error": str(e)})
        }
