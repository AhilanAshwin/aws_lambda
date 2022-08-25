# Lambda consumer handler for events
def consumer_handler(event, context):
    print("A message was recieved: {event}")
    return "Success"
