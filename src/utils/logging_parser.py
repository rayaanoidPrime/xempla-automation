import logging
import boto3
import time
import functools
from botocore.exceptions import ClientError
from config import S3_BUCKET, LOG_FILE_PATH, AWS_REGION, CLOUDWATCH_NAMESPACE

class S3Handler(logging.Handler):
    def __init__(self, bucket):
        super().__init__()
        self.bucket = bucket
        self.s3_client = boto3.client('s3', region_name=AWS_REGION)

    def emit(self, record):
        log_entry = self.format(record)
        try:
            self.s3_client.put_object(Bucket=self.bucket, Key=LOG_FILE_PATH, Body=log_entry)
        except ClientError as e:
            print(f"Error uploading log to S3: {e}")

def setup_logger():
    logger = logging.getLogger('XemplaLogger')
    logger.setLevel(logging.INFO)

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # File handler
    file_handler = logging.FileHandler(LOG_FILE_PATH)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # S3 handler
    s3_handler = S3Handler(S3_BUCKET)
    s3_handler.setFormatter(formatter)
    logger.addHandler(s3_handler)

    return logger

logger = setup_logger()
cloudwatch = boto3.client('cloudwatch', region_name=AWS_REGION)

def log_query(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            end_time = time.time()
            execution_time = (end_time - start_time) * 1000  # Convert to milliseconds

            logger.info(f"Query {func.__name__} executed in {execution_time:.2f}ms")

            # Send execution time to CloudWatch
            cloudwatch.put_metric_data(
                Namespace=CLOUDWATCH_NAMESPACE,
                MetricData=[
                    {
                        'MetricName': 'QueryExecutionTime',
                        'Dimensions': [
                            {
                                'Name': 'FunctionName',
                                'Value': func.__name__
                            },
                        ],
                        'Value': execution_time,
                        'Unit': 'Milliseconds'
                    },
                ]
            )

            if execution_time > 5000:  # If query takes more than 5 seconds
                logger.warning(f"Slow query detected: {func.__name__} took {execution_time:.2f}ms to execute")

            return result
        except Exception as e:
            logger.error(f"Error in query {func.__name__}: {str(e)}")
            raise

    return wrapper