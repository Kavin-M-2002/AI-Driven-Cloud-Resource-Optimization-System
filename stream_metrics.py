import requests
import time
import numpy as np
import boto3
import psutil
from collections import deque

# ================= CONFIG =================
REGION = "us-east-1"
LAMBDA_URL = "https://63y7vjlvzzozi7nt3zckmwoura0icvjh.lambda-url.us-east-1.on.aws/"

WINDOW = 24
FEATURES = 6

LOG_FILE = "/var/log/cpu_forecast.log"

# ================= AWS CLIENT =================
cloudwatch = boto3.client("cloudwatch", region_name=REGION)

INSTANCE_ID = open("/var/lib/cloud/data/instance-id").read().strip()

# ================= BUFFER =================
buffer = deque(maxlen=WINDOW)

print("Starting real-time CPU forecasting stream...")
# ================= FUNCTIONS =================
def get_features():
    cpu = psutil.cpu_percent(interval=1)
    return [cpu] * FEATURES

def publish_prediction(value):
    cloudwatch.put_metric_data(
        Namespace="CPUForecasting",
        MetricData=[
            {
                "MetricName": "PredictedCPU",
                "Dimensions": [
                    {"Name": "InstanceId", "Value": INSTANCE_ID}
                ],
                "Value": float(value),
                "Unit": "Percent"
            }
        ]
    )

# ================= WARM-UP =================
while len(buffer) < WINDOW:
    buffer.append(get_features())

# ================= MAIN LOOP =================
while True:
    actual_cpu = psutil.cpu_percent(interval=1)
    buffer.append(get_features())

    payload = {
        "metrics": np.array(buffer).tolist()
    }

    try:
        start = time.time()
        r = requests.post(LAMBDA_URL, json=payload, timeout=10)
        latency = round((time.time() - start) * 1000, 2)

        result = r.json()
        predicted = result.get("predicted_cpu")

        # Publish predicted CPU to CloudWatch
        if predicted is not None:
            publish_prediction(predicted)

        log_line = f"{time.strftime('%Y-%m-%d %H:%M:%S')}, ActualCPU={actual_cpu}%, PredictedCPU={predicted}%, Latency=>
        print(log_line)

        with open(LOG_FILE, "a") as f:
            f.write(log_line + "\n")