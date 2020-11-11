import boto3
import botocore.client
from instagram.settings import AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_REGION_NAME, AWS_BUCKET_NAME, EXPIRES_DEFAULT
from .models import *
from datetime import datetime

import os, sys, threading


class ProgressPercentage(object):

    def __init__(self, filename):
        self._filename = filename
        self._size = float(os.path.getsize(filename))
        self._seen_so_far = 0
        self._lock = threading.Lock()

    def __call__(self, bytes_amount):
        # To simplify, assume this is hooked up to a single filename
        with self._lock:
            self._seen_so_far += bytes_amount
            percentage = (self._seen_so_far / self._size) * 100
            sys.stdout.write(
                "\r%s  %s / %s  (%.2f%%)" % (
                    self._filename, self._seen_so_far, self._size,
                    percentage))
            sys.stdout.flush()

s3 = boto3.client('s3',
                  aws_access_key_id=AWS_ACCESS_KEY_ID,
                  aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
                  config=botocore.client.Config(signature_version='s3v4'),
                  region_name=AWS_REGION_NAME,
                  )

def get_url_get_oject(object_name, bucket_name=AWS_BUCKET_NAME, expires=EXPIRES_DEFAULT):
    response = s3.generate_presigned_url('get_object',
                                        Params={'Bucket': bucket_name,
                                                'Key': object_name},
                                        ExpiresIn=expires)
    return response

def get_url_put_oject(object_name, bucket_name=AWS_BUCKET_NAME, expires=EXPIRES_DEFAULT):
    response = s3.generate_presigned_url('put_object',
                                        Params={'Bucket': bucket_name,
                                                'Key': object_name},
                                        ExpiresIn=expires)
    return response
    
def get_url(object_name, method, bucket_name=AWS_BUCKET_NAME, expires=EXPIRES_DEFAULT):
    response = s3.generate_presigned_url(method,
                                        Params={'Bucket': bucket_name,
                                                'Key': object_name},
                                        ExpiresIn=expires)
    return response

def put_document(req_object):
    try:
        querys = check_url_valid(req_object['querys'])
        if querys == None:
            return "Access denied", 403
    except:
        return "Error", 401
    
    try:
        student = Students.objects.get(vk_id = querys['vk_user_id'])
        if student.proforg > 0 and 'students_login' in req_object.keys():
            student = Students.objects.get(login = req_object['students_login'])

        now = str(datetime.now()).split()
        date = now[0] + '-' + now[1].split('.')[0]

        documents_name = student.login_eng + '_' + date + '_' +  req_object['file_name']
        get_url = s3.generate_presigned_url('get_object',
                                            Params={'Bucket': AWS_BUCKET_NAME,
                                                    'Key': documents_name},
                                            ExpiresIn=EXPIRES_DEFAULT)

        new_document = Students_documents(student = student, name = documents_name, url = get_url)
        new_document.save()

        put_url = s3.generate_presigned_url('put_object',
                                            Params={'Bucket': AWS_BUCKET_NAME,
                                                    'Key': documents_name},
                                            ExpiresIn=EXPIRES_DEFAULT)
        data={
            'get_url':get_url,
            'put_url':put_url,
            'name':documents_name,
            'date':str(date),
        }
        return data, 200
    except:
        return "Bad request", 400

    # print(put_document({
    #     "querys":"?vk_access_token_settings=notify&vk_app_id=7446946&vk_are_notifications_enabled=0&vk_is_app_user=1&vk_is_favorite=0&vk_language=ru&vk_platform=mobile_android&vk_ref=other&vk_user_id=159317010&sign=qGsNIs0RNS4yUnHogNVeRmggBv0NkkTxNf3B1gRedno",
    #     "file_name":"test2.png",
    # }))

def get_users_documents(req_object):
    try:
        querys = check_url_valid(req_object['querys'])
        if querys == None:
            return "Access denied", 403
    except:
        return "Error", 401
    
    try:
        student = Students.objects.get(vk_id = querys['vk_user_id'])
        if student.proforg > 0 and 'students_login' in req_object.keys():
            student = Students.objects.get(login = req_object['students_login'])
            
        documents = Students_documents.objects.filter(student=student, is_delete=False)
        data = []
        for i in documents:
            try:
                s3.get_object(Bucket=AWS_BUCKET_NAME, Key=i.name)
                data.append({
                    'name':i.name,
                    'url':i.url,
                    'date':str(i.date),
                })
            except:
                i.delete()
        return data, 200
    except:
        return "Bad request", 400

    # print(get_users_documents({
    #     "querys":"?vk_access_token_settings=notify&vk_app_id=7446946&vk_are_notifications_enabled=0&vk_is_app_user=1&vk_is_favorite=0&vk_language=ru&vk_platform=mobile_android&vk_ref=other&vk_user_id=159317010&sign=qGsNIs0RNS4yUnHogNVeRmggBv0NkkTxNf3B1gRedno",
    #     # "file_name":"test_obj",
    # }))

def get_local_users_documents(user):
    try:
        documents = Students_documents.objects.filter(student=user, is_delete=False)
        data = []
        for i in documents:
            try:
                get_url = s3.generate_presigned_url('get_object',
                                            Params={'Bucket': AWS_BUCKET_NAME,
                                                    'Key': i.name},
                                            ExpiresIn=EXPIRES_DEFAULT)
                
                documents_categories = []
                for j in i.categories.all():
                    documents_categories.append(j.category)

                data.append({
                    'name':i.name,
                    'docs_type':i.docs_type,
                    'categories':documents_categories,
                    'url':get_url,
                    'date':str(i.date),
                })
            except:
                i.delete()
        return data
    except:
        return 0

def delete_document(req_object):
    document = Students_documents.objects.get(name = req_object['name'])
    
    student = Students.objects.get(vk_id = querys['vk_user_id'])
    if student.proforg == 0 and document.student != student:
        student = Students.objects.get(login = req_object['students_login'])
        return "Access denied", 403
        
    try:
        s3.delete_object(
            Bucket=AWS_BUCKET_NAME,
            Key=document.name)
    except:
        pass

    document.delete()