import json
import boto3
import os

s3_client = boto3.client('s3')
sns_client = boto3.client('sns')
SNS_TOPIC_ARN = os.environ['SNS_TOPIC_ARN']

def lambda_handler(event, context):
    # Get the object from the event
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = event['Records'][0]['s3']['object']['key']
    
    try:
        response = s3_client.get_object(Bucket=bucket, Key=key)
        log_content = response['Body'].read().decode('utf-8')
        
        # Parse log content
        critical_issues = []
        for line in log_content.split('\n'):
            if 'ERROR' in line or 'CRITICAL' in line:
                critical_issues.append(line)
            elif 'WARNING' in line and 'took more than 5 seconds' in line:
                critical_issues.append(line)
        
        # If critical issues found, send SNS notification
        if critical_issues:
            message = "Critical issues found in logs:\n\n" + "\n".join(critical_issues)
            sns_client.publish(
                TopicArn=SNS_TOPIC_ARN,
                Message=message,
                Subject="Critical Issues in Application Logs"
            )
        
        return {
            'statusCode': 200,
            'body': json.dumps('Log parsing completed successfully')
        }
    except Exception as e:
        print(e)
        return {
            'statusCode': 500,
            'body': json.dumps('Error parsing logs')
        }