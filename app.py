import sys


def handler(event, context):
    print(event)
    print(100*"#")
    print(context)
    return "Hello from AWS lambda using Python" + sys.version + "!"
