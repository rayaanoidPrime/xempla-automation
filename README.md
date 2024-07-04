Certainly! Here's a comprehensive README for the project:

# MongoDB Query Logger and Analyzer

This project provides a robust logging and analysis system for MongoDB queries, utilizing AWS services for log storage, processing, and reporting.

## Table of Contents

1. [Project Overview](#project-overview)
2. [Prerequisites](#prerequisites)
3. [Installation](#installation)
4. [Configuration](#configuration)
5. [Usage](#usage)
6. [AWS Setup](#aws-setup)
7. [Monitoring and Reporting](#monitoring-and-reporting)
8. [Troubleshooting](#troubleshooting)

## Project Overview

This system allows you to:

- Automatically log MongoDB query execution times
- Store logs in AWS S3
- Process logs in real-time using AWS Lambda
- Send alerts for critical issues or slow queries via AWS SNS
- Generate daily summary reports of query performance

## Prerequisites

- Python 3.7+
- AWS account with access to S3, Lambda, SNS, and CloudWatch
- MongoDB instance
- EC2 instance (for running the main application)

## Installation

1. Clone the repository:

   ```
   git clone https://github.com/your-repo/mongodb-query-logger.git
   cd mongodb-query-logger
   ```

2. Install required Python packages:
   ```
   pip install -r requirements.txt
   ```

## Configuration

1. Update `/myapp/src/config.py` with your AWS settings:

   ```python
   AWS_REGION = 'your-aws-region'
   S3_BUCKET = 'your-log-bucket-name'
   SNS_TOPIC_ARN = 'your-sns-topic-arn'
   CLOUDWATCH_NAMESPACE = 'MyApp/Queries'
   ```

2. Update the MongoDB connection string in `/myapp/src/main.py`:
   ```python
   client = MongoClient('your-mongodb-connection-string')
   ```

## Usage

1. To use the query logger, decorate your MongoDB query functions with `@log_query`:

   ```python
   from logger import log_query

   @log_query
   def your_query_function():
       # Your MongoDB query here
       pass
   ```

2. Run the main application:
   ```
   python /myapp/src/main.py
   ```

## AWS Setup

1. Create an S3 bucket for log storage.

2. Create two Lambda functions:

   - `log_parser`: Use `/myapp/lambda/log_parser.py`
   - `daily_summary`: Use `/myapp/lambda/daily_summary.py`

3. Set up an S3 trigger on your bucket to invoke the `log_parser` Lambda function when a new object is created.

4. Create a CloudWatch Events rule to trigger the `daily_summary` Lambda function daily.

5. Create an SNS topic for alerts and reports.

6. Set up IAM roles:
   - EC2 instance role: Allow writing to S3 and CloudWatch
   - Lambda function roles: Allow reading from S3, writing to CloudWatch, and publishing to SNS

## Monitoring and Reporting

- Real-time alerts: Critical issues and slow queries will trigger SNS notifications.
- Daily summaries: A daily report will be sent via SNS, including:
  - Total log count
  - Error count
  - Warning count
  - Slow query count
  - Average and maximum query execution times

## Troubleshooting

1. Check CloudWatch Logs for Lambda function execution logs.
2. Ensure all IAM permissions are correctly set up.
3. Verify that the S3 bucket and SNS topic are in the same region as specified in your config.

---

To set up and run the project on an EC2 instance, follow these step-by-step instructions:

1. Launch an EC2 instance with Amazon Linux 2.

2. Connect to your EC2 instance via SSH.

3. Update the system and install required packages:

   ```
   sudo yum update -y
   sudo yum install -y python3 python3-pip git
   ```

4. Clone the repository:

   ```
   git clone https://github.com/your-repo/mongodb-query-logger.git
   cd mongodb-query-logger
   ```

5. Install Python requirements:

   ```
   pip3 install -r requirements.txt
   ```

6. Configure AWS CLI:

   ```
   aws configure
   ```

   Enter your AWS access key ID, secret access key, and default region.

7. Update the configuration files as described in the Configuration section above.

8. Set up a virtual environment (optional but recommended):

   ```
   python3 -m venv venv
   source venv/bin/activate
   ```

9. Run the main application:

   ```
   python /myapp/src/main.py
   ```

10. To keep the application running after you disconnect from SSH, use a tool like `screen` or set up a systemd service.

Remember to monitor your AWS usage and costs, and to secure your EC2 instance and AWS resources according to best practices.
