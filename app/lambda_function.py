# NOTE: Do not change this name
def consumer_handler(event, context):
    print(f"A message was recieved: {event}")
    print(100*"#")
    print(f"The context: {context}")
    return "Success"
