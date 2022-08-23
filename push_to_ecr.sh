aws ecr get-login-password --region ap-southeast-1 | docker login --username AWS --password-stdin 478403784717.dkr.ecr.ap-southeast-1.amazonaws.com && \
docker tag awslambda-fastapi:latest 478403784717.dkr.ecr.ap-southeast-1.amazonaws.com/awslambda-fastapi:latest && \
docker push 478403784717.dkr.ecr.ap-southeast-1.amazonaws.com/awslambda-fastapi:latest
