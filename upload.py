import boto
from boto.s3.key import Key

AWS_ACCESS_KEY_ID = 'AKIAURRDRKYVT5XIKV6G'
AWS_SECRET_ACCESS_KEY = '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'
END_POINT = 'ap-southeast-1'                          # eg. us-east-1
S3_HOST = 's3.ap-southeast-1.amazonaws.com'                            # eg. s3.us-east-1.amazonaws.com
BUCKET_NAME = 'lp-s3-datalake-landing-dev'  

FILENAME = '20211004_20211004_podv1.csv'         # nama file di local     
x = FILENAME.split("_")
nama_folder = x[0]
nama_folder = nama_folder[:4] + '-' + nama_folder[4:]
nama_folder = nama_folder[:7] + '-' + nama_folder[7:]
UPLOADED_FILENAME = 'lp-operations/stt_status/{}/{}'.format(nama_folder,FILENAME)
# include folders in file path. If it doesn't exist, it will be created

s3 = boto.s3.connect_to_region(END_POINT,
                           aws_access_key_id=AWS_ACCESS_KEY_ID,
                           aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
                           host=S3_HOST)

bucket = s3.get_bucket(BUCKET_NAME)
k = Key(bucket)
k.key = UPLOADED_FILENAME
k.set_contents_from_filename(FILENAME)
------------------------------------------
import pandas as pd
frame = []
numberoffiles = 2

# FIRST IMPORT (CREATE RESULT DATA FRAME)
result = pd.read_csv("20211004_20211004_pod1.csv",header=0,sep=',',skipinitialspace=True)
result.drop(result.index[-1], inplace=True)
frame.append(result)

# ALL OTHER IMPORTS (MERGE TO RESULT DATA FRAME, 8TH COLUMN SUFFIXED ITERATIVELY)
for i in range(2,numberoffiles+1):    
    df = pd.read_csv("20211004_20211004_pod{}.csv".format(i),header=0,sep=',',skipinitialspace=True)
    df.drop(df.index[-1], inplace=True)
    frame.append(df)
    result = pd.concat(frame)
 

result['Booking ID'].replace(r'\\','', regex=True, inplace = True)
# result['Pcs'].str.extract('(\d+)').astype(int)
result.replace(to_replace=[r"\\t|\\n|\\r", "\t|\n|\r"], value=["",""], regex=True, inplace=True)
result.to_csv('20211004_20211004_podv1.csv',index=False)
result.tail(5)
