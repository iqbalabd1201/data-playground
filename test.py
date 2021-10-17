#Library for AWS Connection
import boto3
import sys
from awsglue.utils import getResolvedOptions
import json
import pgdb

#Library To Operate With Data
import pandas as pd
import requests
import io
from io import StringIO
import datetime as dt
import csv

# setting environment
s3 = boto3.resource(service_name='s3',region_name= 'ap-southeast-1',aws_access_key_id= '*****',aws_secret_access_key ='****/EVlI5p1nOxG')
client= boto3.client(service_name='s3',region_name= 'ap-southeast-1',aws_access_key_id= '*****',aws_secret_access_key ='*****/EVlI5p1nOxG')
print(client)
print('Connect to S3')

# #Load Data in Process_API_Elexys Folder 
bucket = 'lp-s3-datalake-landing-dev'
data_key_customer = 'lp-operations/process_api_elexys/temp/get_api_elexys000'
obj = client.get_object(Bucket=bucket,Key=data_key_customer)
df = pd.read_csv(obj['Body'],sep=';',skipinitialspace=True)
print('Loading data')
print(df)

#Define List_STT which have invalid value
list_stt =df['sttno']

#Running Main Script
frame=[]
batch = 1
iteration = 0
for stt in list_stt:
    parameter = {'q':'{}'.format(stt)}
    my_headers = {'Authorization' : 'Basic ************=='}
    r = requests.get('http://api.lionparcel.com/v3/stt/track', params = parameter, headers= my_headers)
    data = r.json() 
    ds =  data['stts'][0]
    dict_items = ds.items()
    first_seven = list(dict_items)[:7]
    dh = data['stts'][0]['history']
    main_df = pd.DataFrame.from_dict(dh, orient='columns')
    other_df = pd.DataFrame.from_dict(first_seven, orient='columns')
    other_df = other_df.transpose()
    new_header = other_df.iloc[0]
    other_df = other_df[1:] 
    other_df.columns = new_header 
    copy_df = pd.concat([main_df]*len(other_df)).sort_index()
    copy_df.reset_index(drop=True, inplace=True)
    df_nested_list = pd.concat([main_df, copy_df], axis=1).reindex(copy_df.index)
    frame.append(df_nested_list)
    result = pd.concat(frame)
    iteration = iteration + 1
    if iteration % 2 == 0 :
        csv_buffer = StringIO()
        result.to_csv(csv_buffer,index=False,sep=';')
        path = 'lp-operations/process_api_elexys/clean/'
        s3.Object(bucket, path+'stt_invalid_{}.csv'.format(batch)).put(Body=csv_buffer.getvalue())
        frame = []
        batch = batch + 1


# #Transform Data
# df = df.rename({'Ticket ID': 'ticket_id', 'From': 'cl_from', 'To': 'cl_to', 'Visibility': 'visibility', 'Category': 'category', 'STT Number': 'stt_number', 'Group': 'cl_group', 'Assigneed by': 'assigned_by', 'Priority': 'priority', 'Type': 'type', 'Created by': 'created_by', 'Created by Compi': 'created_by_compi', 'Created Date': 'created_date', 'Follow up by': 'follow_up_by', 'Follow up by Compi': 'follow_up_by_compi', 'Follow up Date': 'follow_up_date', 'Closed by': 'closed_by', 'Closed Date': 'closed_date', 'Modified by': 'modified_by', 'Modified Date': 'modified_date', 'History State': 'history_state', 'FRT': 'frt', 'AVG': 'avg', 'Sub Category': 'sub_category', 'Channel': 'channel', 'Status STT': 'status_stt', 'Solved by': 'solved_by', 'Solved Date': 'solved_date', 'Escalation By': 'escalation_by', 'Escalation Date': 'escalation_date', 'Origin': 'origin', 'Destination': 'destination', 'BKD Date': 'bkd_date', 'Status Customer': 'status_customer', 'Custom Status': 'custom_status', 'Root Cause': 'root_cause', '1st Escalation OCT By': 'first_escalation_oct_by', '1st Escalation OCT Date': 'first_escalation_oct_date', 'Last Escalation OCT By': 'last_escalation_oct_by', 'Last Escalation OCT Date': 'last_escalation_oct_date'},axis='columns')

# df['created_date'] = pd.to_datetime(df['created_date'], format="%d-%b-%Y %H:%M").dt.strftime('%Y-%m-%d %H:%M')
# df['follow_up_date'] = pd.to_datetime(df['follow_up_date'], format="%d-%b-%Y %H:%M").dt.strftime('%Y-%m-%d %H:%M')
# df['closed_date'] = pd.to_datetime(df['closed_date'], format="%d-%b-%Y %H:%M").dt.strftime('%Y-%m-%d %H:%M')
# df['modified_date'] = pd.to_datetime(df['modified_date'], format="%d-%b-%Y %H:%M").dt.strftime('%Y-%m-%d %H:%M')
# df['solved_date'] = pd.to_datetime(df['solved_date'], format="%d-%b-%Y %H:%M").dt.strftime('%Y-%m-%d %H:%M')
# df['escalation_date'] = pd.to_datetime(df['escalation_date'], format="%d-%b-%Y %H:%M").dt.strftime('%Y-%m-%d %H:%M')
# df['bkd_date'] = pd.to_datetime(df['bkd_date'], format="%d-%b-%Y %H:%M").dt.strftime('%Y-%m-%d %H:%M')
# df['first_escalation_oct_date'] = pd.to_datetime(df['first_escalation_oct_date'], format="%d-%b-%Y %H:%M").dt.strftime('%Y-%m-%d %H:%M')
# df['last_escalation_oct_date'] = pd.to_datetime(df['last_escalation_oct_date'], format="%d-%b-%Y %H:%M").dt.strftime('%Y-%m-%d %H:%M')

# df['follow_up_date'] = df['follow_up_date'].replace('NaT', '')
# df['closed_date'] = df['closed_date'].replace('NaT', '')
# df['modified_date'] = df['modified_date'].replace('NaT', '')
# df['solved_date'] = df['solved_date'].replace('NaT', '')
# df['escalation_date'] = df['escalation_date'].replace('NaT', '')
# df['bkd_date'] = df['bkd_date'].replace('NaT', '')
# df['first_escalation_oct_date'] = df['first_escalation_oct_date'].replace('NaT', '')
# df['last_escalation_oct_date'] = df['last_escalation_oct_date'].replace('NaT', '')


# csv_buffer = StringIO()
# df.to_csv(csv_buffer,index=False,sep=';')

# #Define file_name
# initial = df['created_date'].iloc[0][0:7]
# # end = df['created_date'].iloc[-1][0:10]
# file_name ='complaints_{}.csv'.format(initial) 

# #Export Data Into process folder : process_api_stt_reports 
# path = 'lp-operations/process_temp/initial_complaints/file_temp/'
# s3.Object(bucket, path+'initial_complaints.csv').put(Body=csv_buffer.getvalue())

# #Export Data Into clean folder : api_stt_report 
# date_file = (dt.datetime.now()).strftime("%Y-%m-%d")
# path = 'lp-operations/complaints_all/{}/'.format(date_file)
# s3.Object(bucket, path+file_name).put(Body=csv_buffer.getvalue())


# #get param
# args = getResolvedOptions(sys.argv, ['jobname'])

# # Getting DB credentials from Secrets Manager
# client = boto3.client("secretsmanager", region_name="ap-southeast-1")
# get_secret_value_response = client.get_secret_value(
#         SecretId="lp-sm-redshift-dev"
# )
# secret = get_secret_value_response['SecretString']
# secret = json.loads(secret)
# db_username = secret.get('username')
# db_password = secret.get('password')
# db_url = secret.get('host')
# db_db = secret.get('database')
# db_port = secret.get('port')


# #sql to call log SP
# sql_stmt= "call lp_dwh.sp_complaints('{}')".format(args['jobname']) #<--change this Procedure

# print("This sql will be run: ",sql_stmt)

# #established connection to redshift
# print ('connecting... \n')
# conn = pgdb.connect(database=db_db, host=db_url, user=db_username, password=db_password, port=db_port)
# cursor = conn.cursor()

# print ('executing query.. \n')
# cursor.execute("{}".format(sql_stmt))
# conn.commit()
# print('Complete!!')
