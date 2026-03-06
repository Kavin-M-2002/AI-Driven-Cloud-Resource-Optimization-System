# AI-Driven-Cloud-Resource-Optimization-System
An end-to-end ML-powered cloud optimization pipeline that forecasts CPU workloads and automatically scales cloud resources using AWS services and predictive analytics.

### Workflow Diagram

![Workflow Diagram](workflow_diagram.png)

#### Machine Learning Phase - 

**Primary Tools:** `VS Code` , `Google Colab`

* **Collection and Feature Engineering**
  
    + Data Collection - Collected from Kaggle (Bitbrains Dataset).
 
    + Data Preprocessing.
 
    + Normalization, Scaling, Creating Sequences

* **Model Training**

    + Used LSTM and XGBoost for Model Training.
 
    + XGBoost was used for baseline predictions.
 
    + LSTM was the primary model which used for deployment due to better performance.
 
    + LSTM model saved as a zip file along with its dependencies.

#### Cloud Deployment - 

**Services:** `AWS` , `Docker` , `Grafana`

* The saved model initially stored on S3 bucket.

* Later created a repository created in AWS **Elastic Container Registry** `[ECR]` for containerization which is done by **Docker** locally.

  ##### For login to ECR:
  
  ```bash
  aws ecr get-login-password --region <your-region> | docker login --username AWS --password-stdin <account-id and region>.amazonaws.com
  ```

   ##### Building image on Docker:
  
  ```bash
  docker buildx build --platform linux/amd64 --provenance=false --output=type=docker -t <created lambda function> .
  ```

   ##### Tagging image for ECR:
  
  ```bash
  docker tag <account-id and region>/<lambda function>:latest
  ```

   ##### Pushing image to ECR:
  
  ```bash
  docker push <account-id and region>/<lambda function>:latest
  ```

* The pushed repository will be available on `ECR` which must be deployed on the created Lambda function.

* Test it at Lambda.

* Now, create an `EC2 Instance` for real time prediction.

* After the creation of the instance, access it through Windows Powershell by logging using the security key.

    # for initiating EC2 Instance on the Windows Powershell

      ```bash
      cd <security key locating directory>
      ssh -i <security-key.pem or ppk> ec2-user@<public-ipv4-address>
      nano stream_metrics.py 
      ````
* The `stream_metrics.py` streams real-time CPU utilization metrics from the workload source (e.g., EC2) to the prediction endpoint for generating resource usage forecasts.

* Installing logging agents

  ```bash
  sudo yum install -y amazon-cloudwatch-agent
  sudo nano /opt/aws/amazon-cloudwatch-agent/bin/config.json #creating agent config
  ```

* Starting the agent

  ```bash
  sudo /opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-ctl \
  -a fetch-config \
  -m ec2 \
  -c file:/opt/aws/amazon-cloudwatch-agent/bin/config.json \
  -s
  ```
  
* For Verifying whether agent is running

  ```bash
  sudo systemctl status amazon-cloudwatch-agent
  ```

  * For creating log file in EC2

  ```bash
  sudo touch /var/log/<log-file-name>.log
  sudo chmod 666 /var/log/<log-file-name>.log
  ```

  * For Installing Grafana 

  ```bash
  sudo yum update -y
  sudo tee /etc/yum.repos.d/grafana.repo <<EOF
  [grafana]
  name=grafana
  baseurl=https://packages.grafana.com/oss/rpm
  repo_gpgcheck=1
  enabled=1
  gpgcheck=1
  gpgkey=https://packages.grafana.com/gpg.key
  sslverify=1
  sslcacert=/etc/pki/tls/certs/ca-bundle.crt
  EOF
  sudo yum install grafana -y
  ```

  * For starting and enabling Grafana service

  ```bash
  sudo systemctl start grafana-server
  sudo systemctl enable grafana-server
  sudo systemctl restart grafana-server
  ```

  * For checking the status of Grafana

  ```bash
   sudo systemctl status grafana-server
  ```

  * The Grafana will be accessed through the public IPV4 address of your EC2 Instance:
    
      ##### http://<your-public-ipv4-address>

  
* Make sure the IAM access for all using services allocated properly.
 
* Setting  `Auto Scaling Groups` from EC2 instance for increasing the instances whenever the resource usage goes beyond the predictive threshold, where the `CloudWatch Alarm` can be used for alerts.

  ##### setting ASG capacity

    ```bash
    aws autoscaling update-auto-scaling-group \
  --auto-scaling-group-name <created-asg-group-name> \
  --min-size 1 \
  --max-size 5 \
  --desired-capacity 1
    ```
