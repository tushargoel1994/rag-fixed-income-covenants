import boto3
import json
from datetime import datetime

s3_client = boto3.client('s3')

def lambda_handler(event, context):
    bucket_name = event.get('bucket_name')
    input_prefix = event.get('input_prefix', 'input_files/')
    output_prefix = event.get('output_prefix', 'output/')
    
    # List all files in input folder
    response = s3_client.list_objects_v2(
        Bucket=bucket_name,
        Prefix=input_prefix
    )
    
    # Extract file names
    file_names = [obj['Key'] for obj in response.get('Contents', [])]
    
    # Create output content
    output_content = '\n'.join(file_names)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_key = f"{output_prefix}file_list_{timestamp}.txt"
    
    # Upload to S3
    s3_client.put_object(
        Bucket=bucket_name,
        Key=output_key,
        Body=output_content.encode('utf-8')
    )
    
    return {
        'statusCode': 200,
        'body': json.dumps({
            'message': 'Success',
            'files_found': len(file_names),
            'output_file': output_key
        })
    }