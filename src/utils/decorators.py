import time
import functools
import logging
import boto3
import logging_parser

cloudwatch = boto3.client('cloudwatch')
logger = logging_parser.setup_logger()

def trace(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            execution_time = (time.time() - start_time) * 1000  # Convert to ms
            
            cloudwatch.put_metric_data(
                Namespace='XemplaWatch',
                MetricData=[{
                    'MetricName': f'{func.__name__}_ExecutionTime',
                    'Value': execution_time,
                    'Unit': 'Milliseconds'
                }]
            )
            
            logging.info(f"Function {func.__name__} executed in {execution_time:.2f}ms")
            return result
        except Exception as e:
            logging.error(f"Error in {func.__name__}: {str(e)}")
            
            cloudwatch.put_metric_data(
                Namespace='XemplaWatch',
                MetricData=[{
                    'MetricName': 'ErrorCount',
                    'Value': 1,
                    'Unit': 'Count'
                }]
            )
            raise
    return wrapper