#Library for AWS Connection
import boto3
import sys
from awsglue.utils import getResolvedOptions
import json
import pgdb

#Library To Operate With Data
import pandas as pd
from io import StringIO
import datetime as dt


# setting environment
s3 = boto3.resource(service_name='s3',region_name= 'ap-southeast-1',aws_access_key_id= 'AKIAURRDRKYVT5XIKV6G',aws_secret_access_key ='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')
client = boto3.client('s3')
print(client)
print('Connect to S3')

#Load Data
bucket = 'lp-s3-datalake-landing-dev'
folder = "lp-operations/stt_status"
s3_v1 = boto3.resource(service_name ='s3',
                   region_name = 'ap-southeast-1',
                   aws_access_key_id = 'AKIAURRDRKYVT5XIKV6G',
                   aws_secret_access_key = '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')
s3_bucket = s3_v1.Bucket(bucket)
files_in_s3 = [f.key.split(folder + "/")[-1] for f in s3_bucket.objects.filter(Prefix=folder).all()]
second = files_in_s3[-1]
x = second.split("/")
first = x[-1]
nama_folder = x[0]
print(first)
print(nama_folder)

file_name = first
data_key_customer = 'lp-operations/stt_status/{}/{}'.format(nama_folder,file_name)
print(data_key_customer)
data_location_customer = 's3://{}/{}'.format(bucket, data_key_customer)
obj = client.get_object(Bucket=bucket,Key=data_key_customer)
df = pd.read_csv(obj['Body'],header=0,sep=',',skipinitialspace=True)

print(df)

#Transform

name, rest = file_name.split('_', 1)

import datetime
s_datetime = datetime.datetime.strptime(name, '%Y%m%d')
df['created_at'] = s_datetime
first_column = df.pop('created_at')
df.insert(0, 'created_at', first_column)

## Delete last row
df.drop(df.index[-1], inplace=True)

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



df.drop(df.columns.difference(['created_at','sttdate','sttno','product','commodity','laststatus','isspod','origin','destination','fwdareaorigin','fwdareadest']), 1, inplace=True)

df = df[['created_at','sttdate','sttno','product','commodity','laststatus','isspod','origin','destination','fwdareaorigin','fwdareadest']]
print(df.columns.values)
 

#Export Data

date_inference = nama_folder
date_file = date_inference
path = 'lp-operations/file_clean/POD_stt_reports/file_temp/'

csv_buffer = StringIO()
df.to_csv(csv_buffer,index=False,sep=';')
s3.Object(bucket, path+file_name).put(Body=csv_buffer.getvalue())

#get param
args = getResolvedOptions(sys.argv, ['jobname'])

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


#sql to call log SP
sql_stmt= "call lp_dwh.pod_stt_reports('{}')".format(args['jobname']) #<--change this Procedure

print("This sql will be run: ",sql_stmt)

#established connection to redshift
print ('connecting... \n')
conn = pgdb.connect(database=db_db, host=db_url, user=db_username, password=db_password, port=db_port)
cursor = conn.cursor()

print ('executing query.. \n')
cursor.execute("{}".format(sql_stmt))
conn.commit()
print('Complete!!')
