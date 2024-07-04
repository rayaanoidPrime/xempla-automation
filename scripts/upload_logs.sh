#!/bin/bash

LOG_FILE="/var/log/myapp.log"
S3_BUCKET="my-application-logs"
TIMESTAMP=$(date +"%Y-%m-%d-%H-%M-%S")

mv $LOG_FILE ${LOG_FILE}.${TIMESTAMP}
gzip ${LOG_FILE}.${TIMESTAMP}
aws s3 cp ${LOG_FILE}.${TIMESTAMP}.gz s3://${S3_BUCKET}/
touch $LOG_FILE
find /var/log -name "myapp.log.*" -mtime +7 -exec rm {} \;