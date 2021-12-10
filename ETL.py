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


------------------------------------------------------------------------------------------------------------------

import boto3
import gspread
import pandas as pd
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google.oauth2 import service_account
import json 
from io import StringIO
from oauth2client.service_account import ServiceAccountCredentials
from awsglue.utils import getResolvedOptions
import sys
import pgdb

# setting environment
s3 = boto3.resource(service_name='s3',region_name= 'ap-southeast-1',aws_access_key_id= 'AKIAURRDRKYVT5XIKV6G',aws_secret_access_key ='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')
# setting environment
client = boto3.client('s3')

#def function
def create_keyfile_dict():
    variables_keys = {
      "type": "service_account",
      "project_id": "data-lp",
      "private_key_id": "f0adb41dd1f7590aa52f4c7e4554bf1119831584",
      "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQC/vGIykFVzAEkI\nwNKvBbIBWFSh3UG+zuNG3VENNCoFvOh7E0gsW9oOaQIDU5hl1wZKTU5vSrXe/JwH\n4g9hl8TDhmKmb93eOScFOOoy3PAr1pbJRMfvaNXiFFP1YKucBVIABJ5XXq5U3ulJ\nQzeR/1XB8iCGE4IleKZm/wDjO50R7Zb6zFvXfcOhawhcBdK59qfK9+sA+iubT1Sq\nQSljpveLVEcxL+EwkAKnf1xuQLIWXnO/pTs4Xnfb3fg/rw9yjZps+0Sy/GV+3NlP\nw44MMeTVLD7ECGl884+1SSgph3K2K+QJt2IB8RwGnNQHwR0XnEsZNdCctoa/ndaI\nTzCYTswDAgMBAAECggEACNZZUv9NZkmNvuDe/8DWyDJsDtyF2pI/7io77CHgC0z+\nYiiCBm64CZCpeRccn8UIvdqmUiwytHPBiqjOu1l6xjr8HQkW7taE3TwW/1Uo9LxP\n+Dg6sZGMGimEXSZMLUV0LBq1DviG4dPhvhtiWlEB1jifayPxtwxtObNoimYFrVJz\npXoyO5L5mXzFSD+K4VmVRYTpOgTeLQ7VqqI0x21r1cOY6bEUdLC78f2R1hV7GemL\nMGGyVqAEU72O/wuVskrXO8LJ8nV2V7ZN3+CguyN/EdsmrFgWu5EE5ipQBJ0WRgCd\nRphsv2Sw+m1aro+gjr1iypVGjdg6ptU0kChMZBaq4QKBgQDsiWy18PSVwk+dFiU9\nWk8eY5pbGiXN/ikdg6l6WFJLs4rXt2gGy8zmgkrFkAwUoMZFqQaEAcngBY0e4EFC\nPpBUyoOEtcGZSzDgaWiq2L70yhc5Z65AgR9Nsv4yRORQ++Qj+3Vq5sFRCpK34Qlk\nmZCYoE0ueZpkBHlBPTjubr1j+wKBgQDPgz2o6hshoN6d3eeM4Ss9xTIp5b+AMqy8\neoFcE8nqAU5D6xApAQ1o3fGm4wJmQQ015EKd38RPprI/pHqQa3ulPNKuw5f0Rgks\n3TdMMngeM6/JAWEwE0wqzNq8lJi3leAw5WCWVnImBhF5U41dNtxj4kZiBzBu+NpH\n4uKSPwExmQKBgQCNSUDgJH9T/O7lG9c+oHTl6ATJKgMu2gPhF0XiSGNPyHzEgU7n\n0FAh1+2luHce0zHbZiz4KMFWyLoUmUshsJExtI1+dbqgQCN/yDa25iSZvyTEK0QQ\nT5BNLv9bM39VSEBrpcXrBs6uA6zDnO2pY3jVUdsISaaI24s6BsG82fTShQKBgFuF\n7ecXQdomIqmMGrlHApRe6g4Sl9DKCOekPHPJApAj/Un1Xg5HuYtcAF3z17YT0OjJ\nARyyedoLkqiBOdGCpmktl1qfR+DkFt3jv6TqyZHAiDJmWmAi0sA50+vCukyWXOgT\n8vK7s+LTYFebo0jOjou7XAGWXCVFurhj+Dw6b6NZAoGBAIjoAC0hNjIS0t5Zg5eA\nDOkOk2nUTsaDhucqGFVlIDLc8ej22mzBQ8adm4/BH3Dd+7Me0vpW4VasDnl5k3xs\n1CoTHdwNLjuLRptfbKMu6FRLHm3KODVbsuiIF6KOPhfh83CSO+IAQiO/0CMzwdlW\nFXbsY9Bbp/8++18rRw+0bBRd\n-----END PRIVATE KEY-----\n",
      "client_email": "data-lp@data-lp.iam.gserviceaccount.com",
      "client_id": "108914504203936374698",
      "auth_uri": "https://accounts.google.com/o/oauth2/auth",
      "token_uri": "https://oauth2.googleapis.com/token",
      "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
      "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/data-lp%40data-lp.iam.gserviceaccount.com"
        }
    return variables_keys   
    
#Define Scope
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

#Add Credentials to The Account
creds = None
# creds = service_account.Credentials.from_service_account_file('sample.json', scopes=SCOPES)
creds = ServiceAccountCredentials.from_json_keyfile_dict(create_keyfile_dict(), SCOPES)
gs = gspread.authorize(creds)

# Define Spreadsheet ID
SAMPLE_SPREADSHEET_ID ='1oykv6LSep-RQcG759Dh-L6Lt0C4exIPLG3s0g8R6tgI'
service = build('sheets', 'v4', credentials=creds)

# Call the Sheets API
sheet = service.spreadsheets()
result = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID, range="Customer Branch!A1:J50000").execute()
values = result.get('values',[])
data = pd.DataFrame((values))
data.columns = data.iloc[0]

data = data.iloc[1:].reset_index(drop=True)
data.set_index('CUSTOMER_BRANCH_CODE')
data = data.drop(['NO.'], axis=1)
result_df = data.drop_duplicates()
print(result_df.head())


from io import StringIO # python3; python2: BytesIO 
import boto3

bucket = 'lp-s3-datalake-landing-dev' # already created on S3
csv_buffer = StringIO()
result_df.to_csv(csv_buffer,index=False,sep=';')
s3_resource = boto3.resource(service_name ='s3',
                   region_name = 'ap-southeast-1',
                   aws_access_key_id = 'AKIAURRDRKYVT5XIKV6G',
                   aws_secret_access_key = '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'
                   )
s3_resource.Object(bucket, 'lp-operations/initial_manual/initial_customer_corporate/cust_branch_code_data_test.csv').put(Body=csv_buffer.getvalue())


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

-----------------------------------------------------------------------------------------------------
import pandas as pd
from geopy.distance import geodesic


data = {'list_lat_long':["-6.3001207,106.7391286", "-6.13998825,106.8251083", "-6.1336418,106.742922",
                        "-6.184188333333333, 106.77797166666666"]}
  
# Create DataFrame
df = pd.DataFrame(data)


# import module
from geopy.geocoders import Nominatim

# initialize Nominatim API
geolocator = Nominatim(user_agent="geoapiExercises")

# print(df)
origin = (30.172705, 31.526725)
distance_list=[]
city_list=[]
state_list=[]
country_list=[]
code_list=[]
zipcode_list=[]

for i in df['list_lat_long']:
                # location = geolocator.reverse(Latitude+","+Longitude)
                location = geolocator.reverse(i)

                address = location.raw['address']

                # traverse the data
                city = address.get('city', '')
                state = address.get('state', '')
                country = address.get('country', '')
                code = address.get('country_code')
                zipcode = address.get('postcode')
                distance = geodesic(origin, i).kilometers
#                 print('City : ', city_name)
#                 print('State : ', state)
#                 print('Country : ', country)
#                 print('Zip Code : ', zipcode)
                city_list.append(city)
                state_list.append(state)
                country_list.append(country)
                code_list.append(code)
                zipcode_list.append(zipcode)
                distance_list.append(distance)
df['city']=city_list
df['state']=state_list
df['country']=country_list
df['code']=code_list
df['zipcode']=zipcode_list
df['ditance']=distance_list
print(df)

