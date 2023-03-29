from urllib.parse import unquote
from django.shortcuts import render, redirect

from django.contrib.auth.decorators import login_required,permission_required
from django.core.files.storage import FileSystemStorage
from django.contrib.auth.models import User
from django.contrib import messages 
from django.contrib.auth import authenticate, login,logout
from django.http import HttpResponse, HttpResponseNotFound
from django.core.validators import *
from django.contrib.auth.forms import UserCreationForm
from django.http import FileResponse, Http404
import hashlib

import os
#import easyocr
from pathlib import Path
import pdf2image
from .thread import *
from datetime import datetime, timezone, timedelta
from website.models import *

BASE_DIR = Path(__file__).resolve().parent.parent


@login_required(login_url='/login/')
def one_file(request,id_folder,id_file):
    document = Document.objects.get(uuid_name=id_file)
    try:
        return FileResponse(open(unquote(document.get_url()[1:]), 'rb'), content_type='application/pdf')
    except FileNotFoundError:
        return  HttpResponseNotFound("Файл не найден")
    return redirect('/')


@login_required(login_url='/login/')
def one_doc(request,id_folder,id_file):
    context = {'info':Document.objects.get(uuid_name=id_file).text }
   # document = Document.objects.get(uuid_name=id_file)
    response = render(request, 'one_doc.html', context)
    return response    

@login_required(login_url='/login/')
def one_folder(request,id_folder):
    context = {}
    a = GroupDocuments.objects.get(uuid_name=id_folder)
    try: context={'folder': a,
    'folders': [a],
    'documents': Document.objects.filter(group_uuid=id_folder)}
    except: pass
    response = render(request, 'documents.html', context)
    return response   

@permission_required('website.add_document', raise_exception=True)
def add_document(request):
    if request.method == 'POST':
        file_path =  request.FILES.get('path')
        file_name = request.POST.get('name')
        file_ext = '.' + file_name.split('.')[-1]
        file_description = request.POST.get('description')
        f = GroupDocuments.objects.get(name = request.POST.get('folder'))
        folder = f.get_uuid()
        for i in Document.objects.filter(group_uuid = folder):
            if i.name==file_name:
                    messages.error(request, 'Название файлов внутри одной папки не должны быть одинаковыми!!')
                    return redirect('/'+str(folder))
       
        f.count+=1
        file_path.name=str(str(hashlib.sha512(file_name.encode('utf-8')).hexdigest())+file_ext)
        f.save()
        document = Document(document=file_path, name = file_name,datetime = datetime.now(timezone(timedelta(hours=+3))).strftime('%Y-%m-%d %H:%M:%S'),group_folder=f, description = file_description, group_uuid =folder )
        document.save()

        t = threading.Thread(target=ParseFileThread,args=(f.name,document))
        t.start()
    return redirect('/'+str(folder))

@login_required(login_url='/login/')
def search(request):
    context = {}
    response = render(request, 'main.html', context)
    if request.method == 'POST':
        search =  request.POST.get('search')
        search_type = request.POST.get('search_type')
        print("SEARCH",search, search_type)
        if search_type=='0':
            documents = []
            for i in Document.objects.all():
                if  str(search) in str(i.name):
                    print(search, i.name)
                    documents.append(i)
            print(documents)        
            context={'documents': documents,'year':str(datetime.now(timezone(timedelta(hours=+3))).strftime('%Y')),'document': 'True'}
            response = render(request, 'main.html', context) 
            return response
        elif search_type=='1':
            documents = []
            for i in Document.objects.all():
                if  str(search) in str(i.description):
                    print(search, i.name)
                    documents.append(i)
            print(documents)        
            context={'documents': documents,'year':str(datetime.now(timezone(timedelta(hours=+3))).strftime('%Y')),'document': 'True'}
            response = render(request, 'main.html', context) 
            return response      
        elif search_type=='2':
            documents = []
            for i in Document.objects.all():
                text = ''

            print(documents)        
            context={'documents': documents,'year':str(datetime.now(timezone(timedelta(hours=+3))).strftime('%Y')),'document': 'True'}
            response = render(request, 'main.html', context) 
            return response                    


@permission_required('website.add_groupdocuments', raise_exception=True)
def add_folder(request):
    if request.method == 'POST':
        try:
            folder_name = int(request.POST.get('name'))
            folder = GroupDocuments(name=folder_name,datetime=datetime.now(timezone(timedelta(hours=+3))).strftime('%Y-%m-%d %H:%M:%S'))
            folder.save()
        except:
            messages.error(request, 'Некоректное название папки!')
    return redirect('/')    


@login_required(login_url='/login/')
def main_page(request):
    context = {}

    #print(request.COOKIES.get('url') == None)
    #if request.COOKIES.get('url') == None:
  #  if request.method == 'GET':
  #  try: 
   #     sort =  request.GET['sort']
   #     if sort == 'all':
   #         context={'documents': Document.objects.all()}
   # except: pass
    print( GroupDocuments.objects.all())
    context={'folders': GroupDocuments.objects.all(),
    'year': str(datetime.now(timezone(timedelta(hours=+3))).strftime('%Y'))}
    response = render(request, 'folders.html', context)
    return response


def login_page(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        #print(username,password)
        user = authenticate(username=username, password=password)
        print(user)
        if user is None:
            messages.add_message(request, messages.ERROR,
                                 "Неправильный логин или пароль")
            return render(request, 'login.html')
        else:
            login(request, user)
            messages.add_message(request, messages.SUCCESS,
                                 "Авторизация успешна")
            return redirect('/')
    else:
        return render(request, 'login.html')




def logout_page(request):
    logout(request)
    return redirect('/')
