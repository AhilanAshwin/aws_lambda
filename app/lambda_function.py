from config import get_settings
settings = get_settings()


def consumer_handler(event, context):
    # NOTE: Do not change the namee of this function
    return "Success"
