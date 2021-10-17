import boto3
import pandas as pd
import numpy as np
import datetime as dt
from datetime import timedelta
from io import StringIO


import sys
from awsglue.utils import getResolvedOptions
import boto3
import base64
from botocore.exceptions import ClientError
import json
import pgdb
# print(sys.argv)

#get param
args = getResolvedOptions(sys.argv, ['jobname','job_run_id','batchdate'])


# Getting DB credentials from Secrets Manager
client = boto3.client("secretsmanager", region_name="ap-southeast-1")
get_secret_value_response = client.get_secret_value(
        SecretId="lp-sm-redshift-dev"
)
secret = get_secret_value_response['SecretString']
secret = json.loads(secret)
db_username = secret.get('username')
db_password = secret.get('password')
db_url = secret.get('host')
db_db = secret.get('database')
db_port = secret.get('port')
# print ('usr: {}'.format(db_username))
# print ('pass: {}'.format(db_password))
# print ('host: {}'.format(db_url))
# print ('db: {}'.format(db_db))
# print ('port: {}'.format(db_port))

# setting environment
client = boto3.client('s3')
s3 = boto3.resource('s3')


#Load Data
bucket = 'lp-s3-datalake-landing-dev'
folder = "lp-operations/process_elexys"
s3_v1 = boto3.resource(service_name ='s3',
                   region_name = 'ap-southeast-1',
                   aws_access_key_id = '*******',
                   aws_secret_access_key = '*******/WxuAVsZx')
s3_bucket = s3_v1.Bucket(bucket)
files_in_s3 = [f.key.split(folder + "/")[-1] for f in s3_bucket.objects.filter(Prefix=folder).all()]
second = files_in_s3[-1]
x = second.split("/")
first = x[-1]
nama_folder = x[0]
print(first)
print(nama_folder)

file_name = first
data_key_customer = 'lp-operations/process_elexys/{}/{}'.format(nama_folder,file_name)
print(data_key_customer)
data_location_customer = 's3://{}/{}'.format(bucket, data_key_customer)
obj = client.get_object(Bucket=bucket,Key=data_key_customer)
df = pd.read_csv(obj['Body'],header=0,sep=',',skipinitialspace=True)

# No Enter or Tab space
df.replace(to_replace=[r"\\t|\\n|\\r", "\t|\n|\r"], value=["",""], regex=True, inplace=True)
print('Loading data')

#Transform

## Make new column created_at
# df['created_at'] = (dt.datetime.now() - timedelta(days=4)).strftime("%Y-%m-%d")
# first_column = df.pop('created_at')
# df.insert(0, 'created_at', first_column)
# df['created_at'] = pd.to_datetime(df.created_at)

name, rest = file_name.split('_', 1)

import datetime
s_datetime = datetime.datetime.strptime(name, '%Y%m%d')
df['created_at'] = s_datetime
first_column = df.pop('created_at')
df.insert(0, 'created_at', first_column)

## Delete last row
# df.drop(df.index[-1], inplace=True)

## Change sttdate format
df['STTDate'] = pd.to_datetime(df['STTDate'], format="%d-%b-%Y %H:%M").dt.strftime('%d/%m/%y %H.%M')
df['IsSPOD'] = pd.to_datetime(df['IsSPOD'], format="%d-%b-%Y %H:%M").dt.strftime('%d/%m/%y %H.%M')


# create new column names

new = list(map(lambda x: x.lower(), df.columns.values))
new_name = [x.replace(' ', '') for x in new]
header = [x.replace('.', '') for x in new_name]
header = list(map(lambda x: x.replace('%', ''), header))
header = list(map(lambda x: x.replace('-', ''), header))
header = list(map(lambda x: x.replace('1', ''), header))
df.columns = header

print(header)

#Export Data

date_inference = nama_folder
date_file = date_inference
path = 'lp-operations/process_temp/stt_eleysis_original/file_clean/{}/'.format(date_file)

csv_buffer = StringIO()
df.to_csv(csv_buffer,index=False,sep=';')
s3.Object(bucket, path+file_name).put(Body=csv_buffer.getvalue())

#Path2
date_file = date_inference
path2 = 'lp-operations/stt_reports/{}/'.format(date_file)

csv_buffer = StringIO()
df.to_csv(csv_buffer,index=False,sep=';')
s3.Object(bucket, path2+file_name).put(Body=csv_buffer.getvalue())
