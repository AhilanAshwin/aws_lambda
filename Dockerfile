FROM public.ecr.aws/lambda/python:3.8

ARG STAGE
ARG SQS_URL

# Install the function's dependencies using file requirements.txt
# from your project folder.
COPY requirements.txt  .
RUN  pip3 install --no-cache-dir -r requirements.txt --target "${LAMBDA_TASK_ROOT}"

# Copy function code
COPY ./app ${LAMBDA_TASK_ROOT}/app

# Set the CMD to your handler (could also be done as a parameter override outside of the Dockerfile)
CMD [ "app.main.handler" ]