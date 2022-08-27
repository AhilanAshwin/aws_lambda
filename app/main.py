import boto3
from mangum import Mangum

from fastapi import FastAPI
from app.config import get_settings

settings = get_settings()

root_path = "/" if settings.STAGE == 'local' else f"/{settings.STAGE}/"
app = FastAPI(title=settings.PROJECT_NAME, root_path=root_path,
              description="An API Service created to blast promotional messages to prospective clients using Whats App.")
handler = Mangum(app)


@ app.get("/", status_code=200)
def get_index():
    return {'title': 'Hello World', 'author': "Ahilan Ashwin", 'version': "0.1.1"}


@ app.get('/ping', status_code=200)
def healthcheck():
    return {'status': "Success"}


if __name__ == '__main__':
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8080,
                log_level="debug", reload=True)
