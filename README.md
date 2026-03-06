# AI-Driven-Cloud-Resource-Optimization-System
An end-to-end ML-powered cloud optimization pipeline that forecasts CPU workloads and automatically scales cloud resources using AWS services and predictive analytics.

### Workflow Diagram

![Workflow Diagram](workflow_diagram.png)

* **Collection and Feature Engineering Phase**
  
    + Data Collection - Collected from Kaggle (Bitbrains Dataset).
 
    + Data Preprocessing.
 
    + Normalization, Scaling, Creating Sequences

* **Model Training Phase**

    + Used LSTM and XGBoost for Model Training.
 
    + XGBoost was used for baseline predictions.
 
    + LSTM was the primary model which used for deployment due to better performance.
 
    + LSTM model saved as a bundle along with its dependencies. !(deploy_bundle.zip)
