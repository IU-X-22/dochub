from urllib.parse import unquote
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from django.contrib.postgres.search import (
    SearchVector, SearchQuery, SearchRank)
from django.views.decorators.clickjacking import xframe_options_sameorigin
from django.contrib.auth import authenticate, login, logout
from django.http import FileResponse
from website.thread import add_image
import hashlib
import logging
from pathlib import Path
from datetime import datetime, timezone, timedelta
from website.models import Document, GroupDocuments

BASE_DIR = Path(__file__).resolve().parent.parent
logger = logging.getLogger(__name__)
# ***.all().only('name'm'value') динамически подгружает остальные
# ***.all().valuse('name') {'val': 1} быстрее, но не подгружает остальные


@login_required(login_url='/login/')
@xframe_options_sameorigin
@permission_required('website.view_document', raise_exception=True)
def file_in_browser_open(request, id_folder, id_file):
    try:
        document = Document.objects.get(uuid_name=id_file)
        check_bruteforce = str(document.group_uuid.uuid_name) == str(id_folder)
        assert check_bruteforce, "возможен перебор директорий!"
        logger.warning(
            f"пользователь {request.user.username} " +
            f"открыл файл {document.name}")
        return FileResponse(
            open(unquote(document.get_url()[1:]), 'rb'),
            content_type='application/pdf')
    except Exception as ex:
        logger.warning(
            f"пользователь {request.user.username} " +
            f"попытался открыть файл : {id_folder}/{id_file} {ex}" +
            " возможен перебор директорий!")
        return redirect('/')


@login_required(login_url='/login/')
@permission_required('website.edit_document', raise_exception=True)
def one_file(request, id_folder, id_file):
    try:
        document = Document.objects.get(uuid_name=id_file)
        folder = document.group_uuid
        check_bruteforce = str(folder.uuid_name) == str(id_folder)
        assert check_bruteforce, "возможен перебор директорий!"
        context = {
            'folder': folder,
            'document': document,
            'doc_url': '/'+str(folder.uuid_name)+'/'+str(document.uuid_name)
        }
        logger.warning(
            f"пользователь {request.user.username} " +
            f"открыл страницу с файлом \"{document.name}\"" +
            f"в папке {folder.name}")
        response = render(request, 'one_file.html', context)
        return response
    except Exception as ex:
        logger.warning(
            f"пользователь {request.user.username} " +
            f"попытался открыть файл : {id_folder}/{id_file} {ex} " +
            "возможен перебор директорий!")
        return redirect('/')


@login_required(login_url='/login/')
@permission_required('website.edit_document', raise_exception=True)
def edit_file_text(request, id_folder, id_file):
    if request.method == 'POST':
        try:
            document = Document.objects.get(uuid_name=id_file)
            folder = document.group_uuid
            check_bruteforce = str(folder.uuid_name) == str(id_folder)
            assert check_bruteforce, "возможен перебор директорий!"
            document.text = str(request.POST.get('text'))
            document.is_moderated = True
            logger.warning(
                f"пользователь {request.user.username} изменил" +
                f"содержание файла {document.name})")
            document.save()
            return redirect('/'+str(id_folder)+'/'+str(id_file)+'/info')
        except Exception as ex:
            logger.warning(
                f"пользователь {request.user.username} попытался" +
                f"открыл файл \"{id_folder}/{id_file}\" {ex}" +
                "возможен перебор директорий!")
            return redirect('/')
    else:
        logger.warning(
            f"пользователь {request.user.username} зашел на страницу " +
            f"редактирования документа \"{id_folder}/{id_file}\" " +
            "без полезной нагрузки! Возможен перебор директорий!")
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
            'documents': Document.objects.filter(group_uuid=id_folder)
        }
    except Exception as ex:
        logger.warning(
            f"пользователь {request.user.username} попытался открыть папку " +
            f"\"{id_folder}\" {ex} возможен перебор директорий!")
        return redirect('/')

    if request.method == "GET":
        sort = request.GET.get('sortby')  # request.GET['sortby']
        docs = Document.objects.filter(group_uuid=id_folder)
        if str(sort) == 'toname':
            context.update(
                {'documents': docs.order_by('name')})
        elif str(sort) == 'fromname':
            context.update(
                {'documents': docs.order_by('name')[::-1]})
        elif str(sort) == 'fromtime':
            context.update(
                {'documents': docs.order_by('-datetime')})
        elif str(sort) == 'totime':
            context.update(
                {'documents': docs.order_by('-datetime')[::-1]})
        else:
            context.update(
                {'documents': docs})
    else:
        context.update({Document.objects.filter(group_uuid=id_folder)})
    logger.warning(
        f"пользователь {request.user.username} зашел в папку {folder.name}")
    response = render(request, 'documents.html', context)
    return response


@login_required(login_url='/login/')
@permission_required('website.add_document', raise_exception=True)
def add_document(request):
    try:
        if request.method == 'POST':
            file_path = request.FILES.get('path')
            file_name = request.POST.get('name')
            file_ext = '.pdf'
            file_description = request.POST.get('description')
            is_recognise = request.POST.get('recognise')
            folder = GroupDocuments.objects.get(
                name=request.POST.get('folder'))
            folder.count += 1
            folder.save()
            file_name_hash = hashlib.sha256(file_name.encode('utf-8'))
            file_path.name = str(file_name_hash.hexdigest()) + file_ext
            document = Document(document=file_path, name=file_name,
                                datetime=datetime.now(
                                    timezone(timedelta(hours=+3))).strftime(
                                        '%Y-%m-%d %H:%M:%S'),
                                description=file_description,
                                group_uuid=folder)
            document.save()
            logger.warning(
                f"пользователь {request.user.username}" +
                f"загрузил документ {file_name}")
            if is_recognise:
                add_image(document)
            else:
                document.is_readed = True
            return redirect('/'+str(folder.get_uuid()))
        else:
            logger.warning(
                f"пользователь {request.user.username}" +
                "зашел на страницу добавления документа " +
                "без полезной нагрузки! Возможен перебор директорий!")
            return redirect('/')
    except Exception as ex:
        logger.warning(
            f"пользователь {request.user.username} " +
            f"ошибка добавления документа {ex}")
        return redirect('/')


@login_required(login_url='/login/')
@permission_required('website.delete_document', raise_exception=True)
def delete_document(request, id_folder, id_file):
    try:
        document = Document.objects.get(uuid_name=id_file)
        folder = document.group_uuid
        check_bruteforce = str(folder.uuid_name) == str(id_folder)
        assert check_bruteforce, "возможен перебор директорий!"
        folder.count -= 1
        folder.save()
        logger.warning(
            f"пользователь {request.user.username} " +
            f"удалил документ {document.name}")
        document.document.delete()
        document.delete()
        return redirect('/'+str(id_folder))
    except Exception as ex:
        logger.warning(
            f"пользователь {request.user.username} " +
            f"попытался удалить файл, \"{id_folder}/{id_file}\"" +
            f"{ex} возможен перебор директорий!")
        return redirect('/')


@login_required(login_url='/login/')
@permission_required('website.add_groupdocuments', raise_exception=True)
def add_folder(request):
    if request.method == 'POST':
        try:
            folder_name = int(request.POST.get('name'))
            folder = GroupDocuments(name=folder_name, datetime=datetime.now(
                timezone(timedelta(hours=+3))).strftime('%Y-%m-%d %H:%M:%S'))
            folder.save()
            logger.warning(
                f"пользователь {request.user.username} " +
                f"создал папку {folder_name}")
        except Exception as ex:
            logger.warning(
                f"пользователь {request.user.username} " +
                f"ошибка при создании папки {ex}")
    else:
        logger.warning(
            f"пользователь {request.user.username} " +
            "зашел на страницу создания папки без полезной нагрузки! " +
            "Возможен перебор директорий!")
    return redirect('/')


@login_required(login_url='/login/')
@permission_required('website.view_document', raise_exception=True)
def search_query(request):
    context = {
        'folders': GroupDocuments.objects.all(),
        'year': str(
            datetime.now(timezone(timedelta(hours=+3))).strftime('%Y'))}
    if request.method == "POST":
        query = request.POST.get('search')
        if str(query) == '':
            logger.warning(
                f"пользователь {request.user.username} " +
                "осуществил пустой поиск! Возможна атака!")
            return redirect('/')
        else:
            search_query = SearchQuery(query)
            search_vector = SearchVector("name", "text", "description")
            search_annotation = (
                Document.objects.annotate(
                    search=search_vector,
                    rank=SearchRank(search_vector, search_query)))
            context.update({'documents': search_annotation.filter(
                search=search_query).order_by('-rank')})
    logger.warning(
        f"пользователь {request.user.username} " +
        f"осуществил поиск: {query}")
    response = render(request, 'documents.html', context)
    return response


@login_required(login_url='/login/')
@permission_required('website.view_document', raise_exception=True)
def main_page(request):
    context = {
        'folders': [],
        'year': str(
            datetime.now(timezone(timedelta(hours=+3))).strftime('%Y'))}
    if request.method == "GET":
        sort = request.GET.get('sortby')  # request.GET['sortby']
        folders = GroupDocuments.objects.all()
        if str(sort) == 'toname':
            context.update({'folders': folders.order_by('name')})
        elif str(sort) == 'fromname':
            context.update({'folders': folders.order_by('name')[::-1]})
        elif str(sort) == 'totime':
            context.update({'folders': folders.order_by('-datetime')})
        elif str(sort) == 'fromtime':
            context.update({'folders': folders.order_by('-datetime')[::-1]})
        else:
            context.update({'folders': folders})
    else:
        context.update({'folders':  GroupDocuments.objects.all()})
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
    logger.warning(
        f"пользователь {request.user.username} вышел из аккаунта")
    logout(request)
    return redirect('/')
