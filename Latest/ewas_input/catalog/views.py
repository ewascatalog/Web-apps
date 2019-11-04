from django.shortcuts import render, redirect, render_to_response
from django.http import HttpResponseBadRequest, HttpResponse
from django.template import RequestContext
from django.views.decorators.cache import never_cache, cache_control
from django.contrib.auth.decorators import login_required
from django.db import connection, transaction
from django.core.exceptions import ValidationError
from .forms import StudyForm, AnalysisForm, ParticipantsForm, ResultsForm, UploadFileForm
from .models import Study, Analysis, Participants, Results
# import django_excel as excel
import re, csv, codecs, os, mysql.connector
from io import TextIOWrapper
from django.core.files.base import ContentFile

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def catalog_home(request):
    return render(request, 'catalog/catalog_home.html', {})

def catalog_info(request):
    return render(request, 'catalog/catalog_info.html', {})

@login_required(login_url='/login/')
@never_cache
def catalog_study(request):
    if request.method == "POST":
        form = StudyForm(request.POST)
        if form.is_valid():
            study = form.save(commit=False)
            study.user = request.user.get_username()
            if study.analysis == "":
                pk = re.sub('[^a-zA-Z\d\s]', '', study.pmid+" "+study.trait.lower()).replace(" ", "_")
            else:
                pk = re.sub('[^a-zA-Z\d\s]', '', study.pmid+" "+study.trait.lower()+" "+study.analysis.lower()).replace(" ", "_")
            study.id = pk
            study.save()
            return redirect('catalog_analysis', pk=study.id)
    else:
        form = StudyForm()
    return render(request, 'catalog/input/catalog_study.html', {'form': form})

@login_required(login_url='/login/')
@never_cache
def catalog_analysis(request, pk):
    if request.method == "POST":
        form = AnalysisForm(request.POST)
        if form.is_valid():
            analysis = form.save(commit=False)
            analysis.id = pk
            analysis.save()
            return redirect('catalog_participants', pk=pk)
    else:
        form = AnalysisForm()
    return render(request, 'catalog/input/catalog_analysis.html', {'form': form})

@login_required(login_url='/login/')
@never_cache
def catalog_participants(request, pk):
    if request.method == "POST":
        form = ParticipantsForm(request.POST)
        if form.is_valid():
            participants = form.save(commit=False)
            participants.id = pk
            participants.save()
            return redirect('catalog_results', pk=pk)
    else:
        form = ParticipantsForm()
    return render(request, 'catalog/input/catalog_participants.html', {'form': form})

@login_required
@never_cache
def catalog_results(request, pk):
    if request.method == "POST":
        form = ResultsForm(request.POST)
        if form.is_valid():
            results = form.save(commit=False)
            results.study_id = pk
            results.save()
            return redirect('catalog_results', pk=pk)
    else:
        form = ResultsForm()
    return render(request, 'catalog/input/catalog_results.html', {'form': form})

@login_required(login_url='/login/')
@never_cache
def catalog_import(request, pk):
    if request.method == "POST":
        mysql_account = freader(BASE_DIR+"/catalog/mysql.txt")
        mysql_account = [x for y in mysql_account for x in y]
        form = UploadFileForm(request.POST,request.FILES)
        limit = 10 * 1024 * 1024
        if request.FILES['file'].size < limit:
            if form.is_valid():
                connection = mysql.connector.connect(host=mysql_account[0], user=mysql_account[1], password=mysql_account[2], db=mysql_account[3])
                if request.FILES['file'].name.endswith('.tsv') or request.FILES['file'].name.endswith('.txt'):
                    f = TextIOWrapper(request.FILES['file'].file, encoding='ascii', errors='replace')
                    data = csv.reader(f, delimiter="\t")
                    data = [tuple(x) for x in data]
                    data = [x + (pk,) for x in data]
                    data = data[1:]
                    sql_insert = """ INSERT INTO results (cpg, beta, se, p, i2, p_het, details, study_id) VALUES (%s,%s,%s,%s,%s,%s,%s,%s) """
                    cursor = connection.cursor(prepared=True)
                    sql_input = cursor.executemany(sql_insert, data)
                    connection.commit()
                    return render(request,'catalog/catalog_info.html')
                elif request.FILES['file'].name.endswith('.csv'):
                    f = TextIOWrapper(request.FILES['file'].file, encoding='ascii', errors='replace')
                    data = csv.reader(f)
                    data = [tuple(x) for x in data]
                    data = [x + (pk,) for x in data]
                    data = data[1:]
                    sql_insert = """ INSERT INTO results (cpg, beta, se, p, i2, p_het, details, study_id) VALUES (%s,%s,%s,%s,%s,%s,%s,%s) """
                    cursor = connection.cursor(prepared=True)
                    sql_input = cursor.executemany(sql_insert, data)
                    connection.commit()
                    return render(request,'catalog/catalog_info.html')
                else:
                    return render(request,'catalog/input/catalog_error.html')
            else:
                return HttpResponseBadRequest()
        else:
            return render(request, 'catalog/input/catalog_import.html', {'form': form})
    else:
        form = UploadFileForm()
    return render(request, 'catalog/input/catalog_import.html', {'form': form})

def page_not_found(request):
    response = render_to_response('404.html', {}, context_instance=RequestContext(request))
    response.status_code = 404
    return response

def error(request):
    response = render_to_response('500.html', {}, context_instance=RequestContext(request))
    response.status_code = 500
    return response
    
#def catalog_import(request, pk):
#    if request.method == "POST":
#        form = UploadFileForm(request.POST,request.FILES)
#        limit = 1 * 1024 * 1024
#        if request.FILES['file'].size > limit:
#            folder = "tmp/"
#            uploaded_filename = request.FILES['file'].name
#            extension = os.path.splitext(uploaded_filename)[1]
#            full_filename = os.path.join(BASE_DIR, folder, pk+extension)
#            fout = open(full_filename, 'wb+')
#            file_content = ContentFile(request.FILES['file'].read())
#            for chunk in file_content.chunks():
#                fout.write(chunk)
#            fout.close()
#            return render(request,'catalog/catalog_info.html')
#        else:
#            if form.is_valid():
#                if request.FILES['file'].name.endswith('.csv'):
#                    f = TextIOWrapper(request.FILES['file'].file, encoding='ascii', errors='replace')
#                    data = csv.reader(f)
#                    next(data)
#                    for row in data:
#                        Results.objects.get_or_create(
#                            cpg=row[0],
#                            beta=row[1],
#                            se=row[2],
#                            p=row[3],
#                            i2=row[4],
#                            p_het=row[5],
#                            details=row[6],
#                            study_id=pk
#                        )
#                else: 
#                    results = request.FILES['file']
#                    results.save_to_database(model=Results, mapdicts=['cpg', 'beta', 'se', 'p', 'i2', 'p_het', 'details', 'study_id'])    
#                    cursor = connection.cursor()
#                    cursor.execute("UPDATE results SET study_id = REPLACE(study_id, 'pmid_trait_analysis','"+pk+"')")
#                return render(request,'catalog/catalog_info.html')
#            else:
#                return HttpResponseBadRequest()
#    else:
#        form = UploadFileForm()
#    return render(request, 'catalog/input/catalog_import.html', {'form': form})
