import json
import boto3
import os
from datetime import datetime, timedelta

s3_client = boto3.client('s3')
sns_client = boto3.client('sns')
cloudwatch = boto3.client('cloudwatch')
SNS_TOPIC_ARN = os.environ['SNS_TOPIC_ARN']
BUCKET_NAME = os.environ['BUCKET_NAME']
CLOUDWATCH_NAMESPACE = os.environ['CLOUDWATCH_NAMESPACE']

def get_cloudwatch_metrics(start_time, end_time):
    response = cloudwatch.get_metric_statistics(
        Namespace=CLOUDWATCH_NAMESPACE,
        MetricName='QueryExecutionTime',
        Dimensions=[
            {
                'Name': 'FunctionName',
                'Value': 'ALL'
            },
        ],
        StartTime=start_time,
        EndTime=end_time,
        Period=86400,  # 1 day in seconds
        Statistics=['Average', 'Maximum']
    )
    
    if response['Datapoints']:
        return {
            'AverageQueryTime': response['Datapoints'][0]['Average'],
            'MaxQueryTime': response['Datapoints'][0]['Maximum']
        }
    return {'AverageQueryTime': 'N/A', 'MaxQueryTime': 'N/A'}

def lambda_handler(event, context):
    today = datetime.now().date()
    yesterday = today - timedelta(days=1)
    
    try:
        # List objects in the bucket for yesterday
        response = s3_client.list_objects_v2(
            Bucket=BUCKET_NAME,
            Prefix=f'{yesterday.strftime("%Y/%m/%d")}'
        )
        
        summary = {
            'total_logs': 0,
            'error_count': 0,
            'warning_count': 0,
            'slow_queries': 0
        }
        
        # Process each log file
        for obj in response.get('Contents', []):
            log_content = s3_client.get_object(Bucket=BUCKET_NAME, Key=obj['Key'])['Body'].read().decode('utf-8')
            
            for line in log_content.split('\n'):
                summary['total_logs'] += 1
                if 'ERROR' in line:
                    summary['error_count'] += 1
                elif 'WARNING' in line:
                    summary['warning_count'] += 1
                    if 'Slow query detected' in line:
                        summary['slow_queries'] += 1
        
        # Get CloudWatch metrics
        start_time = datetime(yesterday.year, yesterday.month, yesterday.day)
        end_time = start_time + timedelta(days=1)
        cloudwatch_metrics = get_cloudwatch_metrics(start_time, end_time)
        
        # Create summary message
        message = f"Daily Summary for {yesterday}:\n\n"
        message += f"Total logs: {summary['total_logs']}\n"
        message += f"Error count: {summary['error_count']}\n"
        message += f"Warning count: {summary['warning_count']}\n"
        message += f"Slow queries: {summary['slow_queries']}\n"
        message += f"Average query execution time: {cloudwatch_metrics['AverageQueryTime']:.2f}ms\n"
        message += f"Maximum query execution time: {cloudwatch_metrics['MaxQueryTime']:.2f}ms\n"
        
        # Send summary via SNS
        sns_client.publish(
            TopicArn=SNS_TOPIC_ARN,
            Message=message,
            Subject=f"Daily Log Summary for {yesterday}"
        )
        
        return {
            'statusCode': 200,
            'body': json.dumps('Daily summary sent successfully')
        }
    except Exception as e:
        print(e)
        return {
            'statusCode': 500,
            'body': json.dumps('Error creating daily summary')
        }