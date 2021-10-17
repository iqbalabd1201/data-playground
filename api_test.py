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
s3 = boto3.resource(service_name='s3',region_name= 'ap-southeast-1',aws_access_key_id= '*****',aws_secret_access_key ='******/WxuAVsZx')
# setting environment
client = boto3.client('s3')

#def function
def create_keyfile_dict():
    variables_keys = {
      "type": "service_account",
      "project_id": "data-lp",
      "private_key_id": "******",
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
                   aws_access_key_id = '*****',
                   aws_secret_access_key = '*****/WxuAVsZx'
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
db_port = secret.get('port')


#sql to call log SP
sql_stmt= "call lp_dwh.initial_corp_cust_branch('{}')".format(args['jobname']) #<--change this Procedure

print("This sql will be run: ",sql_stmt)

#established connection to redshift
print ('connecting... \n')
conn = pgdb.connect(database=db_db, host=db_url, user=db_username, password=db_password, port=db_port)
cursor = conn.cursor()

print ('executing query.. \n')
cursor.execute("{}".format(sql_stmt))
conn.commit()
print('Complete!!')
