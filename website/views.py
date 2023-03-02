from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.files.storage import FileSystemStorage
from django.contrib.auth.models import User
from django.contrib import messages 
from django.http import HttpResponse
from smb.SMBConnection import SMBConnection
from django.contrib.auth.forms import UserCreationForm
from django.http import FileResponse, Http404
import json
import  urllib
from urllib.parse import unquote
import pandas as pd
import pytesseract as pt
import pdf2image
import PyPDF2
import os
from datetime import datetime, timezone, timedelta
from website.models import *

# Create your views here. :)12345



def year_folder(request,year):
    context = {}
    response = render(request, 'main.html', context)
    print(GroupDocuments.objects.filter(name=year))
    context={'documents': Document.objects.filter(group_id=year),
    'folders': GroupDocuments.objects.all(),
    'year':str(datetime.now(timezone(timedelta(hours=+3))).strftime('%Y')),
    'document': 'True',
    'current_folder': GroupDocuments.objects.get(name=year)}
    response = render(request, 'main.html', context)
    return response   


def one_file(request,year,name_file):
    context = {}
    response = render(request, 'main.html', context)
    context={'document': Document.objects.filter(group_id=year,name=name_file)}
    response = render(request, 'one_doc.html', context)
    return response       

def add_document(request):
    if request.method == 'POST':
        file_path =  request.FILES.get('path')
        
        file_name = request.POST.get('name')
        file_description = request.POST.get('description')
        folder = request.POST.get('folder')
        for i in Document.objects.filter(name = file_name):
            if i.group_id==str(folder):
                    messages.error(request, 'Название файлов внутри одной папки не должны быть одинаковыми!!')
                    return redirect('/'+folder)
        f = GroupDocuments.objects.get(name=folder)
        f.count+=1
        file_path.name=str(file_name.encode())
        print(file_path.name)
        f.save()
        document = Document(document=file_path, name = file_name,datetime = datetime.now(timezone(timedelta(hours=+3))).strftime('%Y-%m-%d %H:%M:%S'), description = file_description, group_id =folder )
        document.save()
    return redirect('/'+folder)


def search(request):
    context = {}
    response = render(request, 'main.html', context)
    if request.method == 'POST':
        search =  request.POST.get('search')
        search_type = request.POST.get('search_type')
        print("SEARCh",search, search_type)
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
                reader = PyPDF2.PdfReader(unquote(i.get_url()[1:]))
                for j in reader.pages:
                    text+=j.extract_text()
                if search in text:
                    documents.append(i)
                    break
                pages = pdf2image.convert_from_path(pdf_path=unquote(i.get_url()[1:]), dpi=200, size=(1654,2340))    
                for i in range(len(pages)):
                    content = pt.image_to_string(pages[i], lang='ru')
            print(documents)        
            context={'documents': documents,'year':str(datetime.now(timezone(timedelta(hours=+3))).strftime('%Y')),'document': 'True'}
            response = render(request, 'main.html', context) 
            return response                    

def open_file(request):
    if request.method == 'POST':
        file_id = request.POST.get('file_id')
        document = Document.objects.get(id=file_id)
        print(document.get_url())
        #print(str(document.group_id)+'/' + str(document.name))
        try:
            return FileResponse(open(unquote(document.get_url()[1:]), 'rb'), content_type='application/pdf')
        except FileNotFoundError:
            raise Http404()

            return FileResponse(open(f, 'rb'), content_type='application/pdf')
    return redirect('/')


def add_folder(request):
    if request.method == 'POST':
        folder_name = request.POST.get('name')
        folder_description = request.POST.get('description')
        folder =GroupDocuments(name = folder_name, description = folder_description,datetime = datetime.now(timezone(timedelta(hours=+3))).strftime('%Y-%m-%d %H:%M:%S'))
        folder.save()
    return redirect('/')    

def main_page(request):
    context = {}
    response = render(request, 'main.html', context)
    
    #print(request.COOKIES.get('url') == None)
    #if request.COOKIES.get('url') == None:
    response.set_cookie(key='url', value='/')

  #  if request.method == 'GET':
  #  try: 
   #     sort =  request.GET['sort']
   #     if sort == 'all':
   #         context={'documents': Document.objects.all()}
   # except: pass
   
    context={'folders': GroupDocuments.objects.all(),
    'year':str(datetime.now(timezone(timedelta(hours=+3))).strftime('%Y')),
    'document': 'False'}
    response = render(request, 'main.html', context) 
    return response


def catalogs(request):
    context = {}
    return render(request, 'main.html', context)
