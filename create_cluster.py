import boto3
import configparser

config = configparser.ConfigParser()
config.read_file(open('dwh.cfg'))

KEY = config.get('AWS', 'KEY')
SECRET = config.get('AWS', 'SECRET')

DB_NAME = config.get('CLUSTER', 'DB_NAME')
DB_USER = config.get('CLUSTER', 'DB_USER')
DB_PASSWORD = config.get('CLUSTER', 'DB_PASSWORD')
DB_PORT = config.get('CLUSTER', 'DB_PORT')

DWH_CLUSTER_TYPE = config.get('DWH', 'DWH_CLUSTER_TYPE')
DWH_NUM_NODES = config.get('DWH', 'DWH_NUM_NODES')
DWH_NODE_TYPE = config.get('DWH', 'DWH_NODE_TYPE')
DWH_CLUSTER_IDENTIFIER = config.get('DWH', 'DWH_CLUSTER_IDENTIFIER')
DWH_IAM_ROLE_NAME = config.get('DWH', 'DWH_IAM_ROLE_NAME')
DWH_REGION = config.get('DWH', 'DWH_REGION')

S3_ARN_READ = "arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess"


def create_resources():

    """ Create required AWS resources """

    ec2 = boto3.resource('ec2',
                         region_name=DWH_REGION,
                         aws_access_key_id=KEY,
                         aws_secret_access_key=SECRET
                         )

    s3 = boto3.resource('s3',
                        region_name=DWH_REGION,
                        aws_access_key_id=KEY,
                        aws_secret_access_key=SECRET
                        )

    iam = boto3.client('iam',
                       region_name=DWH_REGION,
                       aws_access_key_id=KEY,
                       aws_secret_access_key=SECRET
                       )

    redshift = boto3.client('redshift',
                            region_name=DWH_REGION,
                            aws_access_key_id=KEY,
                            aws_secret_access_key=SECRET
                            )

    return ec2, s3, iam, redshift
