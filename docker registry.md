To logout docker from ecr:

**docker logout 620584311286.dkr.ecr.us-east-1.amazonaws.com**



login docker to ecr:

**aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 620584311286.dkr.ecr.us-east-1.amazonaws.com**



building image on docker:

**docker buildx build --platform linux/amd64 --provenance=false --output=type=docker -t lstm-lambda .**



tag the image for ecr:

Purpose: To associate your local image with a specific ECR repository and version.



**docker tag lstm-lambda:latest 620584311286.dkr.ecr.us-east-1.amazonaws.com/lstm-lambda:latest** \[**#latest-** image name which will vary for every creating \& uploading images]



Key Role: Tagging creates the specific address (URI) ECR needs to identify where the image should live. 



push image to ecr:

Purpose: To upload the tagged image from your local machine to your ECR repository in the cloud.



**docker push 620584311286.dkr.ecr.us-east-1.amazonaws.com/lstm-lambda:latest**



Process: After tagging, the docker push command sends the image layers to ECR, where they are stored, encrypted, and managed. 



If we get any error while pushing (ex: 403 forbidden), try to login, then tag and push.

