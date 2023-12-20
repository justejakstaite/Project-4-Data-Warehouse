import argparse
import boto3
import configparser
import json
import logging
import time

from botocore.exceptions import ClientError


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


def create_iam_role(iam):

    """ Create IAM role for Redshift cluster """

    try:
        dwh_role = iam.create_role(
            Path='/',
            RoleName=DWH_IAM_ROLE_NAME,
            AssumeRolePolicyDocument=json.dumps({
                'Statement': [{
                    'Action': 'sts:AssumeRole',
                    'Effect': 'Allow',
                    'Principal': {'Service': 'redshift.amazonaws.com'}
                }],
                'Version': '2012-10-17'
            })
        )
        iam.attach_role_policy(
            RoleName=DWH_IAM_ROLE_NAME,
            PolicyArn=S3_ARN_READ
        )

    except ClientError as e:
        logging.warning(e)

    role_arn = iam.get_role(RoleName=DWH_IAM_ROLE_NAME)['Role']['Arn']
    logging.info('Role {} with arn {}'.format(DWH_IAM_ROLE_NAME, role_arn))

    return role_arn


def create_redshift_cluster(redshift, role_arn):

    """ Create Redshift cluster """

    try:
        redshift.create_cluster(
            ClusterType=DWH_CLUSTER_TYPE,
            NodeType=DWH_NODE_TYPE,
            NumberOfNodes=int(DWH_NUM_NODES),
            DBName=DB_NAME,
            ClusterIdentifier=DWH_CLUSTER_IDENTIFIER,
            MasterUsername=DB_USER,
            MasterUserPassword=DB_PASSWORD,
            IamRoles=[role_arn],
        )
        logging.info('Creating cluster {}...'.format(DWH_CLUSTER_IDENTIFIER))

    except ClientError as e:
        logging.warning(e)


def delete_iam_role(iam):

    """ Delete IAM role """

    role_arn = iam.get_role(RoleName=DWH_IAM_ROLE_NAME)['Role']['Arn']
    iam.detach_role_policy(RoleName=DWH_IAM_ROLE_NAME, PolicyArn=S3_ARN_READ)
    iam.delete_role(RoleName=DWH_IAM_ROLE_NAME)
    logging.info('Deleted role {} with {}'.format(DWH_IAM_ROLE_NAME, role_arn))


def delete_redshift_cluster(redshift):

    """ Delete Redshift cluster """

    try:
        redshift.delete_cluster(
            ClusterIdentifier=DWH_CLUSTER_IDENTIFIER,
            SkipFinalClusterSnapshot=True,
        )
        logging.info('Deleted cluster {}'.format(DWH_CLUSTER_IDENTIFIER))

    except Exception as e:
        logging.error(e)


def open_tcp(ec2, vpc_id):

    """ Open TCP connection """

    try:
        vpc = ec2.Vpc(id=vpc_id)
        default_sg = list(vpc.security_groups.all())[0]
        default_sg.authorize_ingress(
            GroupName=default_sg.group_name,
            CidrIp='0.0.0.0/0',
            IpProtocol='TCP',
            FromPort=int(DB_PORT),
            ToPort=int(DB_PORT),
        )
        logging.info('Allow TCP connection')

    except ClientError as e:
        logging.warning(e)


def main(args):

    """ Main function """

    ec2, s3, iam, redshift = create_resources()

    if args.delete:
        delete_redshift_cluster(redshift)
        delete_iam_role(iam)

    else:
        role_arn = create_iam_role(iam)
        create_redshift_cluster(redshift, role_arn)

        # Continuously check the status of the Redshift cluster after creation until it becomes available
        time_step = 15
        for _ in range(int(600/time_step)):
            cluster = redshift.describe_clusters(ClusterIdentifier=DWH_CLUSTER_IDENTIFIER)['Clusters'][0]
            if cluster['ClusterStatus'] == 'available':
                break
            logging.info('Cluster status is "{}". Retrying in {} seconds.'.format(cluster['ClusterStatus'], time_step))
            time.sleep(time_step)

        # Initiate a TCP connection once the cluster creation is successful
        if cluster:
            logging.info('Cluster created at {}'.format(cluster['Endpoint']))
            open_tcp(ec2, cluster['VpcId'])
        else:
            logging.error('Could not connect to cluster')


if __name__ == '__main__':

    """ Set logging level and cli arguments """

    logging.basicConfig(level=logging.INFO)
    parser = argparse.ArgumentParser()
    parser.add_argument('--delete', dest='delete', default=False, action='store_true')
    args = parser.parse_args()
    main(args)

