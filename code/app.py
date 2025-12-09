import boto3
s3 = boto3.client('s3')


def lambda_handler(event, context):
    obj = s3.get_object(Bucket='sourcefiles-us-west-2-854105048', Key='object1')
    contents = obj["Body"].read()

    return {"result": contents}
