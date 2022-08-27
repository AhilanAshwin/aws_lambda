import boto3

sqs = boto3.resource('sqs')
queue = sqs.get_queue_by_name(QueueName='awslambda-fastapi-dev-sqs')

print(queue.url)
print(queue.attributes.get('DelaySeconds'))

response = queue.send_message(MessageBody='world')
print(response.get('MessageId'))
print(response.get('MD5OfMessageBody'))
