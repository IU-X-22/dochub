from urllib.parse import unquote
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from django.db.models import Q
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank
from django.views.decorators.clickjacking import xframe_options_sameorigin
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseNotFound
from django.http import FileResponse
import hashlib
import psutil
import threading
import logging
from faker import Faker
from website.thread import add_image
import os
from pathlib import Path
from .thread import ParseFileThread
from datetime import datetime, timezone, timedelta
from website.models import Document, GroupDocuments

BASE_DIR = Path(__file__).resolve().parent.parent
logger = logging.getLogger(__name__)
 # ***.all().only('name'm'value') динамически подгружает остальные
 #***.all().valuse('name') {'val': 1} быстрее, но не подгружает остальные

@permission_required('website.view_document', raise_exception=True)
def file_in_browser_open(request, id_folder, id_file):
    try:
        document = Document.objects.get(uuid_name=id_file)
        assert str(document.group_uuid.uuid_name) == str(id_folder), "возможен перебор директорий!"
        logger.warning("пользователь "+request.user.username+" открыл файл "+document.name)
        return FileResponse(open(unquote(document.get_url()[1:]), 'rb'),
                                content_type='application/pdf')
    except Exception as ex:
        logger.warning("пользователь "+request.user.username+" попытался открыл файл :"+str(id_folder)+'/'+str(id_file) + " "+str(ex) + " возможен перебор директорий!")
        return redirect('/')


@xframe_options_sameorigin
@permission_required('website.edit_document', raise_exception=True)
def one_file(request, id_folder, id_file):
    try:
        document = Document.objects.get(uuid_name=id_file)
        folder = document.group_uuid
        assert str(folder.uuid_name) == str(id_folder), "возможен перебор директорий!"
        context = {
        'folder': folder,
        'document': document,
        'doc_url': '/'+str(folder.uuid_name)+'/'+str(document.uuid_name)
        }
        logger.warning("пользователь "+request.user.username+" открыл страницу с файлом \""+str(document.name)+ "\" в папке "+str(folder.name))
        response = render(request, 'one_file.html', context)
        return response
    except Exception as ex:
        logger.warning("пользователь "+request.user.username+" попытался открыл файл, \""+str(id_folder)+'/'+str(id_file) + "\" "+str(ex) + " возможен перебор директорий!")
        return redirect('/')


@permission_required('website.edit_document', raise_exception=True)
def edit_file_text(request,id_folder, id_file):
    if request.method == 'POST':
        try:
            document = Document.objects.get(uuid_name=id_file)
            folder = document.group_uuid
            assert str(folder.uuid_name) == str(id_folder), "возможен перебор директорий!"
            document.text = str(request.POST.get('text'))
            document.is_moderated = True
            logger.warning("пользователь "+request.user.username+" изменил содержание файла "+document.name)
            document.save()
            return redirect('/'+str(id_folder)+'/'+str(id_file)+'/info')
        except Exception as ex:
            logger.warning("пользователь "+request.user.username+" попытался открыл файл, \""+str(id_folder)+'/'+str(id_file) + "\" "+str(ex) + " возможен перебор директорий!")
            return redirect('/')
    else:
         logger.warning("пользователь "+ request.user.username+" зашел на страницу редактирования документа \""+str(id_folder)+'/'+str(id_file) + "\" без полезной нагрузки! Возможен перебор директорий!")
         return redirect('/'+str(id_folder)+'/'+str(id_file))
        
@login_required(login_url='/login/')
@permission_required('website.view_document', raise_exception=True)
def one_folder(request, id_folder):
    context = {}
    try:
        folder = GroupDocuments.objects.get(uuid_name=id_folder)
        context = {
            'folder': folder,
            'folders': [folder],
            'documents':Document.objects.filter(group_uuid=id_folder)
        }
    except Exception as ex:
        logger.warning("пользователь "+request.user.username+" попытался открыл папку, \""+str(id_folder) + "\" "+str(ex) + " возможен перебор директорий!")
        return redirect('/')

    if request.method == "GET":
        sort= request.GET.get('sortby') #request.GET['sortby']
        if str(sort)=='toname':
            context.update({ 'documents': Document.objects.filter(group_uuid=id_folder).order_by('name')})
        elif str(sort)=='fromname':
            context.update({ 'documents': Document.objects.filter(group_uuid=id_folder).order_by('name')[::-1]})    
        elif  str(sort)=='fromtime':
            context.update({ 'documents': Document.objects.filter(group_uuid=id_folder).order_by('-datetime')})
        elif  str(sort)=='totime':
            context.update({ 'documents': Document.objects.filter(group_uuid=id_folder).order_by('-datetime')[::-1]})
        else: context.update({ 'documents': Document.objects.filter(group_uuid=id_folder)})
    else : 
        context.update({Document.objects.filter(group_uuid=id_folder)})
    logger.warning("пользователь "+request.user.username+ " зашел в папку "+folder.name)
    response = render(request, 'documents.html', context)
    return response


@permission_required('website.add_document', raise_exception=True)
def add_document(request): 
    try:
        if request.method == 'POST':
            file_path = request.FILES.get('path')
            file_name = request.POST.get('name')
            file_ext = '.pdf'
            file_description = request.POST.get('description')
            is_recognise = request.POST.get('recognise')
            folder=GroupDocuments.objects.get(name=request.POST.get('folder'))
            folder.count+=1
            folder.save()
            file_path.name = str(
                    hashlib.sha256(file_name.encode('utf-8')).hexdigest()) +file_ext 
            document = Document(document=file_path, name=file_name,
                                    datetime=datetime.now(timezone(timedelta(hours=+3))
                                                        ).strftime(
                                                            '%Y-%m-%d %H:%M:%S'), description=file_description,
                                    group_uuid=folder)
            document.save()
            logger.warning("пользователь "+request.user.username+" загрузил документ "+file_name)
            if is_recognise:
                add_image(document)
            else: document.is_readed = True    
            return redirect('/'+str(folder.get_uuid()))
        else:
            logger.warning("пользователь "+request.user.username+" зашел на страницу добавления документа без полезной нагрузки! Возможен перебор директорий!")
            return redirect('/')
    except Exception as ex:
        logger.warning("пользователь "+request.user.username+" ошибка добавления документа "+str(ex))
        return redirect('/')
    
@permission_required('website.delete_document', raise_exception=True)
def delete_document(request,id_folder,id_file): 
    try:
        document = Document.objects.get(uuid_name=id_file)
        folder = document.group_uuid
        assert str(folder.uuid_name) == str(id_folder), "возможен перебор директорий!"
        folder.count-=1
        folder.save()
        logger.warning("пользователь "+request.user.username+" удалил документ "+document.name)
        document.document.delete()
        document.delete()
        return redirect('/'+str(id_folder))
    except Exception as ex:
        logger.warning("пользователь "+request.user.username+" попытался удалить файл, \""+str(id_folder)+'/'+str(id_file) + "\" "+str(ex) + " возможен перебор директорий!")
        return redirect('/')
   

@permission_required('website.add_groupdocuments', raise_exception=True)
def add_folder(request):
    if request.method == 'POST':
        try:
            folder_name = int(request.POST.get('name'))
            folder = GroupDocuments(name=folder_name, datetime=datetime.now(
                timezone(timedelta(hours=+3))).strftime('%Y-%m-%d %H:%M:%S'))
            folder.save()
            logger.warning("пользователь "+request.user.username+" создал папку "+folder_name)
        except Exception as ex:
            logger.warning("пользователь "+request.user.username+" ошибка при создании попки "+str(ex))
    else:
        logger.warning("пользователь "+request.user.username+" зашел на страницу создания папки без полезной нагрузки! Возможен перебор директорий!")
    return redirect('/')

@permission_required('website.view_document', raise_exception=True)
def search_query(request):
    context = {
        'folders': GroupDocuments.objects.all(),
        'year': str(datetime.now(timezone(timedelta(hours=+3))).strftime('%Y'))}
    if request.method == "POST":
        query = request.POST.get('search')
        if str(query) == '':
            logger.warning("пользователь "+request.user.username+" осуществил пустой поиск! Возможна атака!")
            return redirect('/')
        else:
            search_query = SearchQuery(query)
            search_vector = SearchVector("name","text","description")
            context.update({'documents' :  Document.objects.annotate(search=search_vector,rank=SearchRank(search_vector,search_query)).filter(search=search_query).order_by('-rank')
})
    logger.warning("пользователь "+request.user.username+" осуществил поиск: "+str(query))
    response = render(request, 'documents.html', context)
    return response
        

@login_required(login_url='/login/')
@permission_required('website.view_document', raise_exception=True)
def main_page(request):
    context = {
        'folders': [],
        'year': str(datetime.now(timezone(timedelta(hours=+3))).strftime('%Y'))}
    if request.method == "GET":
        sort= request.GET.get('sortby') #request.GET['sortby']
        if str(sort)=='toname':
            context.update({'folders' : GroupDocuments.objects.all().order_by('name')})
        elif str(sort)=='fromname':
            context.update({'folders' : GroupDocuments.objects.all().order_by('name')[::-1]})    
        elif str(sort)=='totime':
            context.update({'folders' : GroupDocuments.objects.all().order_by('-datetime')})
        elif str(sort)=='fromtime':
            context.update({'folders' : GroupDocuments.objects.all().order_by('-datetime')[::-1]})    
        else: context.update({'folders' :  GroupDocuments.objects.all()}) 
    else : 
       context.update({'folders' :  GroupDocuments.objects.all()})    
    response = render(request, 'folders.html', context)
    return response

def login_page(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)
        if user is None:
            logger.warning("неудачный вход : "+username+" "+password)
            messages.add_message(request, messages.ERROR,
                                 "Неправильный логин или пароль")
            return render(request, 'login.html')
        else:
            login(request, user)
            logger.warning("пользователь " + username+" вошел в систему")
            messages.add_message(request, messages.SUCCESS,
                                 "Авторизация успешна")
            return redirect('/')
    else:
        return render(request, 'login.html')

def logout_page(request):
    logger.warning("пользователь "+request.user.username+" вышел из аккаунта")
    logout(request)
    return redirect('/')
