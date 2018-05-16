import boto3
from botocore.exceptions import ClientError
import os
import datetime
import io
import time
import numpy as np

def downloadFromS3(url):
    try:
        segments = url.rpartition('/')
        filename = segments[2]
        segments=segments[0].rpartition('/')
        backetname = segments[2]
        bucket=s3_client.Bucket(backetname)
        localfilename = os.path.join(localStoragePath,filename)
        bucket.download_file(filename, localfilename)
        return localfilename
    except ClientError as e:
        print("Error downloading file",e)
        res = e.response
        outMessage = {'command': 'errorMessage', 'data': res}
        socketIO.emit('errorMessage', outMessage)
        return None


def uploadToS3(url,data):
    try:
        segments = url.rpartition('/')
        filename = segments[2]
        segments=segments[0].rpartition('/')
        backetname = segments[2]
        bucket=s3_client.Bucket(backetname)
        # print("uploading to bucket ",backetname, " file: ", filename)
        bucket.upload_fileobj(data,filename)
        # bucket.download_file(filename, localfilename)
        # return localfilename
    except ClientError as e:
        print("Error downloading file",e)
        res = e.response
        outMessage = {'command': 'errorMessage', 'data': res}
        socketIO.emit('errorMessage', outMessage)
        return None



key=os.getenv('AWS_ACCESS_KEY_ID',"")
secret=os.getenv('AWS_SECRET_ACCESS_KEY',"")
s3EndpointUrl=os.getenv('S3_ENDPOINT_URL',"")
localStoragePath=os.getenv('LOCAL_STORAGE_PATH','./localStoragePath')
operation=os.getenv('OPERATION',"upload")
size=int(os.getenv('SIZE',"1024"))
iterations=int(os.getenv('ITERATIONS',"10"))
if not os.path.exists(localStoragePath):
    os.makedirs(localStoragePath)
if s3EndpointUrl:
    s3_client_session = boto3.session.Session(
        aws_access_key_id=key,
        aws_secret_access_key=secret,
    )
    s3_client = s3_client_session.resource(
        service_name='s3',
        endpoint_url=s3EndpointUrl
        )
    print('s3 init to ',s3EndpointUrl)
else:
    print('s3 not init')

# start = datetime.datetime.now()
# downloadFromS3('http://10.32.10.24:9000/test1/sort-arrow-sprite.png')
# end = datetime.datetime.now()
# diff = end - start
# print("download time: ",diff.total_seconds())
filename=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
print("filename:",filename)
dataSize=size
if operation=="download":
    a = "a" * dataSize
    a=a.encode('utf-8')
    data = io.BytesIO()
    data.write(a)
    data.seek(0)
    uploadToS3(s3EndpointUrl+'/test1/'+filename,data)

print(operation,":", dataSize, "bytes for",iterations,"times")
times=[]
for c in list(range(iterations)):
    a = "a" * dataSize
    a=a.encode('utf-8')
    data = io.BytesIO()
    
    data.write(a)
    data.seek(0)
    # start = datetime.datetime.now()
    start = time.perf_counter()
    if operation=="upload":
        uploadToS3(s3EndpointUrl+'/test1/'+filename,data)
    else:
        downloadFromS3(s3EndpointUrl+'/test1/'+filename)
    # end = datetime.datetime.now()
    end = time.perf_counter()
    diff = end - start
    print("upload time: ",diff)
    times.append(diff)

a = np.array(times)
for percentile in [50,90,99]:
    p = np.percentile(a, percentile) # return 50th percentile, e.g median.
    print("percentile",percentile,":",p)


# to run as pod
# kubectl run s3try -i -t --rm --image=hkube/s3try:v1.0.0 --restart=Never --env S3_ENDPOINT_URL=http://10.32.10.24:9000 --env AWS_ACCESS_KEY_ID=agambstorage --env AWS_SECRET_ACCESS_KEY=234eqndbpuCkGtH85KSyK/xAv3xuqdOpM3fKOLYlrSerpdKoG1FYy3kh6ArceL+yDwTvQOgs47xYO/ktnNzEeg== --env SIZE=100 --env OPERATION=upload
# as docker
# docker run --rm -it -e S3_ENDPOINT_URL=http://10.32.10.24:9000 -e AWS_ACCESS_KEY_ID=agambstorage -e AWS_SECRET_ACCESS_KEY=234eqndbpuCkGtH85KSyK/xAv3xuqdOpM3fKOLYlrSerpdKoG1FYy3kh6ArceL+yDwTvQOgs47xYO/ktnNzEeg== -e SIZE=100 -e OPERATION=upload  hkube/s3try:v1.0.0