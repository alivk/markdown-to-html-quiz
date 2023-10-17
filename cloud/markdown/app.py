import boto3
import markdown
import json
from jinja2 import Environment, PackageLoader, select_autoescape
import os

YOUR_DESTINATION_BUCKET = os.environ['YOUR_DESTINATION_BUCKET']

s3_client = boto3.client('s3')
WRAPPER_RENDER = True

def render_test(file_name: str, markdown_content: str) -> str:
    extensions = ["tables", "addon.extensions.checkbox", "addon.extensions.radio", "addon.extensions.textbox"]
    html = markdown.markdown(markdown_content, extensions=extensions, output_format="html5")
    env = Environment(loader=PackageLoader('addon', 'static'), autoescape=select_autoescape(['html', 'xml']))
    javascript = env.get_template('app.js').render()
    test_html = env.get_template('base.html').render(content=html, javascript=javascript)
    if WRAPPER_RENDER:
        test_html = env.get_template('wrapper.html').render(content=test_html)
    return test_html

def lambda_handler(event, context):
    print(json.dumps(event, indent=4, default=str))
    for record in event['Records']:
        bucket = record['s3']['bucket']['name']
        key = record['s3']['object']['key']

        if key.endswith('.md'):
            response = s3_client.get_object(Bucket=bucket, Key=key)
            markdown_content = response['Body'].read().decode('utf-8')
            
            html_content = render_test(key, markdown_content)
            dest_key = key.replace('.md', '.html')
            
            s3_client.put_object(Body=html_content, Bucket=YOUR_DESTINATION_BUCKET, Key=dest_key)

    return {
        'statusCode': 200,
        'body': 'Processing done.'
    }
