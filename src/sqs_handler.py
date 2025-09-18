import boto3
import json
import logging
from config import settings

logger = logging.getLogger(__name__)

class SQSHandler:
    def __init__(self):
        # For local development, use a mock SQS or localstack
        self.sqs = boto3.client('sqs', region_name='us-east-1')
        self.queue_url = None
        
    def create_queue(self, queue_name):
        try:
            response = self.sqs.create_queue(
                QueueName=queue_name,
                Attributes={
                    'FifoQueue': 'true',
                    'ContentBasedDeduplication': 'true'
                }
            )
            self.queue_url = response['QueueUrl']
            logger.info(f"Created queue: {self.queue_url}")
        except Exception as e:
            logger.error(f"Error creating queue: {e}")
            # Fallback to in-memory queue
            self.queue_url = None
            self.messages = []
            
    def send_message(self, message_body):
    # Convert any timestamp objects to strings
        if 'timestamp' in message_body and hasattr(message_body['timestamp'], 'isoformat'):
            message_body['timestamp'] = message_body['timestamp'].isoformat()
    
        if self.queue_url:
            try:
                response = self.sqs.send_message(
                    QueueUrl=self.queue_url,
                    MessageBody=json.dumps(message_body),
                    MessageGroupId='anomaly-detection'
                )
                return response
            except Exception as e:
                logger.error(f"Error sending message: {e}")
                return None
        else:
            # Fallback to in-memory queue
            self.messages.append(message_body)
            return {'MessageId': 'local-' + str(len(self.messages))}
            
    def receive_messages(self, max_messages=10):
        if self.queue_url:
            try:
                response = self.sqs.receive_message(
                    QueueUrl=self.queue_url,
                    MaxNumberOfMessages=max_messages,
                    VisibilityTimeout=settings.SQS_VISIBILITY_TIMEOUT
                )
                return response.get('Messages', [])
            except Exception as e:
                logger.error(f"Error receiving messages: {e}")
                return []
        else:
            # Return messages from in-memory queue
            messages = self.messages[:max_messages]
            self.messages = self.messages[max_messages:]
            return [{'Body': json.dumps(msg), 'ReceiptHandle': 'local'} for msg in messages]
            
    def delete_message(self, message):
        if self.queue_url and 'ReceiptHandle' in message:
            try:
                self.sqs.delete_message(
                    QueueUrl=self.queue_url,
                    ReceiptHandle=message['ReceiptHandle']
                )
            except Exception as e:
                logger.error(f"Error deleting message: {e}")