import json
import boto3
import io
import zipfile
import mimetypes

from botocore.client import Config
def lambda_handler(event, context):
    sns = boto3.resource('sns')
    topic = sns.Topic('arn:aws:sns:us-east-1:201054198317:deployPortfolioTopic')
    try:
        s3 = boto3.resource('s3', config=Config(signature_version='s3v4'))
        
        portfolio_bucket = s3.Bucket('portfolio.bogdanodulinski.net')
        build_bucket = s3.Bucket('portfoliobuild.bogdanodulinski.net')
        
        portfolio_zip = io.BytesIO()
        build_bucket.download_fileobj('portfoliobuild.zip', portfolio_zip)
        
        with zipfile.ZipFile(portfolio_zip) as myzip:
            for nm in myzip.namelist():
                obj = myzip.open(nm)
                portfolio_bucket.upload_fileobj(obj, nm, ExtraArgs={'ContentType': mimetypes.guess_type(nm)[0]})
                portfolio_bucket.Object(nm).Acl().put(ACL='public-read')
            
            topic.publish(Subject='Portfolio Deployment Successful', Message='Portfolio deployed successfully.')
    except:
            topic.publish(Subject='Portfolio Deployment Failed', Message='Portfolio did not deploy.')
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }
