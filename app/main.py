from fastapi import FastAPI
from mangum import Mangum

from fastapi_events.middleware import EventHandlerASGIMiddleware
from fastapi_events.handlers.aws import SQSForwardHandler

app = FastAPI(title="Whats App Blaster API", root_path="/dev/")
app.add_middleware(EventHandlerASGIMiddleware,
                   handlers=[SQSForwardHandler(queue_url="awslambda-fastapi-dev-sqs",
                                               region_name="ap-southeast-1")])
handler = Mangum(app)


@ app.get("/", status_code=200)
def get_index():
    return {'title': 'Hello World', 'author': "Ahilan Ashwin", 'version': "0.1.1"}


@ app.get('/ping', status_code=200)
def healthcheck():
    return {'status': "Success"}


if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=80, log_level="debug")
