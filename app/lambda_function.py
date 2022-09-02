import json
import requests


def consumer_handler(event, context):
    # NOTE: Do not change the namee of this function
    print("HELLO!")
    print("In lambda")
    try:
        r = requests.get("https://google.com")
        return r.status_code
    except Exception as e:
        print(e)
    return "DONE"
