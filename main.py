import json
import os
import tempfile
import boto3
from docx2pdf import convert

s3 = boto3.client('s3')

def lambda_handler(event, context):
    # Extract input parameters from the Lambda event
    source_bucket = event['Records'][0]['s3']['bucket']['name']
    source_key = event['Records'][0]['s3']['object']['key']
    
    # Define the output file name
    output_file_name = os.path.splitext(source_key)[0] + '.pdf'

    try:
        # Download the Word (DOCX) file from S3
        tmp_dir = tempfile.mkdtemp()
        tmp_docx_path = os.path.join(tmp_dir, 'input.docx')
        s3.download_file(source_bucket, source_key, tmp_docx_path)

        # Convert DOCX to PDF
        convert(tmp_docx_path)

        # Define the path to the converted PDF
        tmp_pdf_path = os.path.join(tmp_dir, 'input.pdf')

        # Upload the converted PDF to S3
        s3.upload_file(tmp_pdf_path, source_bucket, output_file_name)

        return {
            'statusCode': 200,
            'body': json.dumps('File conversion completed.')
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps(f'Error: {str(e)}')
        }
    finally:
        # Clean up temporary files
        for root, dirs, files in os.walk(tmp_dir):
            for file in files:
                os.remove(os.path.join(root, file))
        os.rmdir(tmp_dir)
