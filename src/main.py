import json
import boto3
import requests
from urllib.parse import unquote_plus

# Redmineの設定
REDMINE_URL = 'https://your-redmine-instance.com'
API_KEY = 'your_redmine_api_key'
PROJECT_ID = 1  # プロジェクトID
TRACKER_ID = 1  # トラッカーID, 例: Bug

s3 = boto3.client('s3')

def lambda_handler(event, context):
    # S3イベントからファイル名を取得
    bucket_name = event['Records'][0]['s3']['bucket']['name']
    object_key = unquote_plus(event['Records'][0]['s3']['object']['key'])

    # S3からメールの内容を取得
    response = s3.get_object(Bucket=bucket_name, Key=object_key)
    mail_content = response['Body'].read().decode('utf-8')
    
    # メールの内容からチケットの詳細を抽出（簡単化のため、ここでは全文を本文として使用）
    subject = "New Ticket from Email"
    description = mail_content

    # Redmineのチケット作成APIを呼び出す
    url = f"{REDMINE_URL}/issues.json"
    headers = {
        "Content-Type": "application/json",
        "X-Redmine-API-Key": API_KEY
    }
    payload = {
        "issue": {
            "project_id": PROJECT_ID,
            "tracker_id": TRACKER_ID,
            "subject": subject,
            "description": description
        }
    }
    response = requests.post(url, headers=headers, data=json.dumps(payload))
    
    if response.status_code == 201:
        return {'statusCode': 200, 'body': json.dumps('Ticket created successfully')}
    else:
        return {'statusCode': response.status_code, 'body': json.dumps('Failed to create ticket')}
