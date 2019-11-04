from django.shortcuts import render, redirect, render_to_response
from django.http import HttpResponseBadRequest, HttpResponse, JsonResponse
from django.views.decorators.cache import never_cache, cache_control
import MySQLdb, re, os, glob, csv, time, datetime, sched, requests, string, tabix
from math import log10, floor
from decimal import Decimal
from ratelimit.decorators import ratelimit

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def remove(directory):
    for file in os.listdir(directory):
        curpath = os.path.join(directory+'/'+file)
        file_modified = datetime.datetime.fromtimestamp(os.path.getmtime(curpath))
        if datetime.datetime.now() - file_modified > datetime.timedelta(hours=5):
            os.remove(curpath)

def round_sig(x, sig=2):
    if x>0:
        return round(x, sig-int(floor(log10(abs(x))))-1)
    else:
        return x 

def format_e(n):
    a = '%E' % n
    return a.split('E')[0].rstrip('0').rstrip('.') + 'E' + a.split('E')[1]

def missing(x):
    try:
        return float(x)
    except (ValueError, TypeError):
        return 'NA'

def not_efo(x):
    if not x:
        x = 'NULL'
    return(x)

def output_table(data):
    data = [list(x) for x in data]
    for x in data:
        if missing(x[9])=='NA':
            x[9] = 'NA'
        elif float(x[9])==0:
            x[9] = 'NA'
        else:
            x[9] = str(round_sig(float(x[9])))
        x[10] = str(format_e(round_sig(float(x[10]))))
    return data

def output_tsv(data,query,fields,ts):
    f = open(BASE_DIR+'/catalog/static/tmp/'+query.replace(" ", "_")+'_'+ts+'.tsv', 'w')
    f.write('\t'.join(fields)+'\n')
    for row in data:
        f.write('\t'.join(str(x) for x in row)+'\n')

def freader(x):
    ifile=open(x, "r")
    lines=ifile.readlines()
    tab_file=[tuple(line.strip().split("\t")) for line in lines]
    return tab_file

def efo(query):
    q=re.sub('[^a-zA-Z\d\s]', '', query).replace(" ", "+")
    punc = re.compile('[%s]' % re.escape(string.punctuation))
    efo = str(requests.get('http://www.ebi.ac.uk/spot/zooma/v2/api/services/annotate?propertyValue='+q).json())
    efo = punc.sub(' ', efo)
    efo_term = list(filter(lambda x: re.search('^EFO_',x), efo.replace("EFO ", "EFO_").split()))
    efo_terms1 = list(sorted(set(efo_term), key=efo_term.index))
    efo = str(requests.get('http://www.ebi.ac.uk/spot/zooma/v2/api/services/annotate?propertyValue='+q+'&filter=required:[gwas]').json())
    efo = punc.sub(' ', efo)
    efo_term = list(filter(lambda x: re.search('^EFO_',x), efo.replace("EFO ", "EFO_").split()))
    efo_terms2 = list(sorted(set(efo_term), key=efo_term.index))
    efo_term = efo_terms1 + efo_terms2
    efo_terms = list(sorted(set(efo_term), key=efo_term.index))
    efo_terms = [x for x in efo_terms if x!="EFO_UKB"]
    return efo_terms

def efo_mysql(efo):
    mysql = "SELECT studies.*,results.* FROM studies JOIN results ON studies.study_id=results.study_id WHERE efo LIKE '%"+"%' or efo LIKE '%".join(efo)+"%';"
    return mysql

def efo_mysql_aries(efo):
    mysql = "SELECT aries_studies.*,aries_results.* FROM aries_studies JOIN aries_results ON aries_studies.study_id=aries_results.study_id WHERE efo LIKE '%"+"%' or efo LIKE '%".join(efo)+"%';"
    return mysql

def efo_mysql_geo(efo):
    mysql = "SELECT geo_studies.*,geo_results.* FROM geo_studies JOIN geo_results ON geo_studies.study_id=geo_results.study_id WHERE efo LIKE '%"+"%' or efo LIKE '%".join(efo)+"%';"
    return mysql

def tabix_query(chrom, pos):
    results = []
    for file in glob.glob(BASE_DIR+"/catalog/data/*.vcf.gz"):
        tb = tabix.open(file)
        try:
            records = tb.querys(str(chrom)+':'+str(pos)+'-'+str(int(pos)+1))
            results += [tuple(x[8:]) for x in records]
        except:
            results += []
    return(results)

def tabix_region_query(chrom, start, end):
    results = []
    for file in glob.glob(BASE_DIR+"/catalog/data/*.vcf.gz"):
        tb = tabix.open(file)
        try:
            records = tb.querys(str(chrom)+':'+str(start)+'-'+str(end))
            results += [tuple(x[8:]) for x in records]
        except:
            results += []
    return(results)

@never_cache
def catalog_home(request):
    remove(BASE_DIR+"/catalog/static/tmp")
    query = request.GET.get("query", None)
    ts = str(time.time()).replace(".","")
    mysql_account = freader(BASE_DIR+"/catalog/mysql.txt")
    mysql_account = [x for y in mysql_account for x in y]
    fields = ['Author', 'Consortium', 'PMID', 'Date', 'Trait', 'EFO', 'Analysis', 'Source', 'Outcome', 'Exposure', 'Covariates', 'Outcome_Unit', 'Exposure_Unit', 'Array', 'Tissue', 'Further_Details', 'N', 'N_Studies', 'Categories', 'Age', 'N_Males', 'N_Females', 'N_EUR', 'N_EAS', 'N_SAS', 'N_AFR', 'N_AMR', 'N_OTH', 'CpG', 'Location', 'Chr', 'Pos', 'Gene', 'Type', 'Beta', 'SE', 'P', 'Details']
    if query:
        query = query.strip()
        db = MySQLdb.connect(host=mysql_account[0], user=mysql_account[1], password=mysql_account[2], db=mysql_account[3])
        cur = db.cursor()      
        if re.match("^cg[0-9]+", query):
            cur.execute("SELECT studies.*,results.* FROM results JOIN studies ON results.study_id=studies.study_id WHERE cpg='"+query+"'")
            data = cur.fetchall()          
            data = [x for x in data if float(x[37]) <= 1]
            data = [x[0:28]+x[29:39] for x in data]
            cur.execute("SELECT * FROM cpgs WHERE cpg='"+query+"'")
            cpg_data = cur.fetchall()
            data += tabix_query(cpg_data[0][2], cpg_data[0][3])
            data.sort(key=lambda tup: (tup[0], tup[2], float(tup[36])))
            data_html = tuple(output_table([x[0:1]+x[2:3]+x[8:10]+x[6:7]+x[16:17]+x[28:30]+x[32:33]+x[34:35]+x[36:37] for x in data]))
            output_tsv(data,query,fields,ts)
            return render(request, 'catalog/catalog_results.html', {'result':data_html, 'query':query.replace(" ", "_"), 'query_label':query, 'ts':ts})
        elif re.match("^ch\.[0-9]+\.[0-9]+", query):
            cur.execute("SELECT studies.*,results.* FROM results JOIN studies ON results.study_id=studies.study_id WHERE cpg='"+query+"'")
            data = cur.fetchall()          
            data = [x for x in data if float(x[37]) <= 1]
            data = [x[0:28]+x[29:39] for x in data]
            cur.execute("SELECT * FROM cpgs WHERE cpg='"+query+"'")
            cpg_data = cur.fetchall()
            data += tabix_query(cpg_data[0][2], cpg_data[0][3])
            data.sort(key=lambda tup: (tup[0], tup[2], float(tup[36])))
            data_html = tuple(output_table([x[0:1]+x[2:3]+x[8:10]+x[6:7]+x[16:17]+x[28:30]+x[32:33]+x[34:35]+x[36:37] for x in data]))
            output_tsv(data,query,fields,ts)
            return render(request, 'catalog/catalog_results.html', {'result':data_html, 'query':query.replace(" ", "_"), 'query_label':query, 'ts':ts})
        elif re.match("^chr[0-9]+:[0-9]+", query):
            cur.execute("SELECT studies.*,results.* FROM results JOIN studies ON results.study_id=studies.study_id WHERE chrpos='"+query+"'")
            data = cur.fetchall()          
            data = [x for x in data if float(x[37]) <= 1]
            data = [x[0:28]+x[29:39] for x in data]
            data += tabix_query(re.sub(":.*", "", query).replace("chr", ""), re.sub(".*:", "", query))
            data.sort(key=lambda tup: (tup[0], tup[2], float(tup[36])))
            data_html = tuple(output_table([x[0:1]+x[2:3]+x[8:10]+x[6:7]+x[16:17]+x[28:30]+x[32:33]+x[34:35]+x[36:37] for x in data]))
            output_tsv(data,query,fields,ts)
            return render(request, 'catalog/catalog_results.html', {'result':data_html, 'query':query.replace(" ", "_"), 'query_label':query, 'ts':ts})
        elif re.match("[0-9]+:[0-9]+-[0-9]+", query):
            region = re.split(':|-',query)
            chrom = region[0]
            start = region[1]
            end = region[2]
            if (int(end) - int(start)) <= 10000000:
                cur.execute("SELECT studies.*,results.* FROM results JOIN studies ON results.study_id=studies.study_id WHERE chr='"+chrom+"' AND pos>="+start+" AND pos<="+end)
                data = cur.fetchall()          
                data = [x[0:28]+x[29:39] for x in data]
                data += tabix_region_query(chrom, start, end)
                data = [x for x in data if float(x[36]) < 1e-4]
                data.sort(key=lambda tup: (tup[0], tup[2], float(tup[36])))
                data_html = tuple(output_table([x[0:1]+x[2:3]+x[8:10]+x[6:7]+x[16:17]+x[28:30]+x[32:33]+x[34:35]+x[36:37] for x in data]))
                output_tsv(data,query,fields,ts)
                return render(request, 'catalog/catalog_results.html', {'result':data_html, 'query':query.replace(" ", "_"), 'query_label':query, 'ts':ts})
            else:
                return render(request, 'catalog/catalog_region_error.html', {})
        elif re.match(r'(\s|^|$)'+"[A-Z0-9-]+"+r'(\s|^|$)', query):
            genes = cur.execute("SELECT gene,ensembl_id,chr,start,end FROM genes WHERE gene='"+query+"'")
            if genes > 0:
                gene = list(cur.fetchall()[0])
                chrom = gene[2]
                start = str(gene[3])
                end = str(gene[4])
                cur.execute("SELECT studies.*,results.* FROM results JOIN studies ON results.study_id=studies.study_id WHERE chr='"+chrom+"' AND pos>="+start+" AND pos<="+end)
                data = cur.fetchall()          
                data = [x[0:28]+x[29:39] for x in data]
                data += tabix_region_query(chrom, start, end)
                data = [x for x in data if float(x[36]) < 1e-4]
                data.sort(key=lambda tup: (tup[0], tup[2], float(tup[36])))
                data_html = tuple(output_table([x[0:1]+x[2:3]+x[8:10]+x[6:7]+x[16:17]+x[28:30]+x[32:33]+x[34:35]+x[36:37] for x in data]))
                output_tsv(data,query,fields,ts)
                return render(request, 'catalog/catalog_results.html', {'result':data_html, 'query':query.replace(" ", "_"), 'query_label':query, 'ts':ts})
            else:
                efo_terms = efo(query)
                efo_terms = not_efo(efo_terms)
                if efo_terms!="NULL":
                    efo_query = efo_mysql(efo_terms)
                    cur.execute(efo_query)
                    data = cur.fetchall()          
                    data = [x for x in data if float(x[37]) < 1e-7]
                    efo_query_aries = efo_mysql_aries(efo_terms)
                    cur.execute(efo_query_aries)
                    data_aries = cur.fetchall()
                    efo_query_geo = efo_mysql_geo(efo_terms)
                    cur.execute(efo_query_geo)
                    data_geo = cur.fetchall()
                    data += [x for x in data_aries if float(x[37]) < 1e-7]
                    data += [x for x in data_geo if float(x[37]) < 1e-7]
                    data = [x[0:28]+x[29:39] for x in data]
                    data.sort(key=lambda tup: (tup[0], tup[2], float(tup[36])))
                    data_html = tuple(output_table([x[0:1]+x[2:3]+x[8:10]+x[6:7]+x[16:17]+x[28:30]+x[32:33]+x[34:35]+x[36:37] for x in data]))
                    output_tsv(data,query,fields,ts)
                    return render(request, 'catalog/catalog_results.html', {'result':data_html, 'query':query.replace(" ", "_"), 'query_label':query, 'ts':ts})
                else:
                    return render(request, 'catalog/catalog_no_results.html', {'query':query})
        else:
            efo_terms = efo(query)
            efo_terms = not_efo(efo_terms)
            if efo_terms!="NULL":
                efo_query = efo_mysql(efo_terms)
                cur.execute(efo_query)
                data = cur.fetchall()
                data = [x for x in data if float(x[37]) < 1e-7]
                efo_query_aries = efo_mysql_aries(efo_terms)
                cur.execute(efo_query_aries)
                data_aries = cur.fetchall()
                efo_query_geo = efo_mysql_geo(efo_terms)
                cur.execute(efo_query_geo)
                data_geo = cur.fetchall()
                data += [x for x in data_aries if float(x[37]) < 1e-7]
                data += [x for x in data_geo if float(x[37]) < 1e-7]                
                data = [x[0:28]+x[29:39] for x in data]
                data.sort(key=lambda tup: (tup[0], tup[2], float(tup[36])))
                data_html = tuple(output_table([x[0:1]+x[2:3]+x[8:10]+x[6:7]+x[16:17]+x[28:30]+x[32:33]+x[34:35]+x[36:37] for x in data]))
                output_tsv(data,query,fields,ts)
                return render(request, 'catalog/catalog_results.html', {'result':data_html, 'query':query.replace(" ", "_"), 'query_label':query, 'ts':ts})
            else:
                return render(request, 'catalog/catalog_no_results.html', {'query':query})
    else:
        return render(request, 'catalog/catalog_home.html', {})

@never_cache
def catalog_info(request):
    remove(BASE_DIR+"/catalog/static/tmp")
    return render(request, 'catalog/catalog_about.html', {})

@never_cache
def catalog_documents(request):
    remove(BASE_DIR+"/catalog/static/tmp")
    return render(request, 'catalog/catalog_documents.html', {})

@never_cache
def catalog_download(request):
    remove(BASE_DIR+"/catalog/static/tmp")
    return render(request, 'catalog/catalog_download.html', {})

@ratelimit(key='ip', rate='1000/h', block=True)
def catalog_api(request):
    remove(BASE_DIR+"/catalog/static/tmp")
    cpgquery = request.GET.get("cpgquery", None)
    genequery = request.GET.get("genequery", None)
    regionquery = request.GET.get("regionquery", None)
    traitquery = request.GET.get("traitquery", None)
    mysql_account = freader(BASE_DIR+"/catalog/mysql.txt")
    mysql_account = [x for y in mysql_account for x in y]
    fields = ['Author', 'Consortium', 'PMID', 'Date', 'Trait', 'EFO', 'Analysis', 'Source', 'Outcome', 'Exposure', 'Covariates', 'Outcome_Unit', 'Exposure_Unit', 'Array', 'Tissue', 'Further_Details', 'N', 'N_Studies', 'Categories', 'Age', 'N_Males', 'N_Females', 'N_EUR', 'N_EAS', 'N_SAS', 'N_AFR', 'N_AMR', 'N_OTH', 'CpG', 'Location', 'Chr', 'Pos', 'Gene', 'Type', 'Beta', 'SE', 'P', 'Details']
    if cpgquery: 
        db = MySQLdb.connect(host=mysql_account[0], user=mysql_account[1], password=mysql_account[2], db=mysql_account[3])
        cur = db.cursor()      
        if re.match("^cg[0-9]+", cpgquery):
            cur.execute("SELECT studies.*,results.* FROM results JOIN studies ON results.study_id=studies.study_id WHERE cpg='"+cpgquery+"'")
            data = cur.fetchall()          
            data = [x for x in data if float(x[37]) <= 1]
            data = [x[0:28]+x[29:39] for x in data]
            cur.execute("SELECT * FROM cpgs WHERE cpg='"+cpgquery+"'")
            cpg_data = cur.fetchall()
            data += tabix_query(cpg_data[0][2], cpg_data[0][3])
            data.sort(key=lambda tup: (tup[0], tup[2], float(tup[36])))
            return JsonResponse({'results':data, 'fields':fields})
        elif re.match("^ch\.[0-9]+\.[0-9]+", cpgquery):
            cur.execute("SELECT studies.*,results.* FROM results JOIN studies ON results.study_id=studies.study_id WHERE cpg='"+cpgquery+"'")
            data = cur.fetchall()          
            data = [x for x in data if float(x[37]) <= 1]
            data = [x[0:28]+x[29:39] for x in data]
            cur.execute("SELECT * FROM cpgs WHERE cpg='"+cpgquery+"'")
            cpg_data = cur.fetchall()
            data += tabix_query(cpg_data[0][2], cpg_data[0][3])
            data.sort(key=lambda tup: (tup[0], tup[2], float(tup[36])))
            return JsonResponse({'results':data, 'fields':fields})
        elif re.match("^chr[0-9]+:[0-9]+", cpgquery):
            cur.execute("SELECT studies.*,results.* FROM results JOIN studies ON results.study_id=studies.study_id WHERE chrpos='"+cpgquery+"'")
            data = cur.fetchall()          
            data = [x for x in data if float(x[37]) <= 1]
            data = [x[0:28]+x[29:39] for x in data]
            data += tabix_query(re.sub(":.*", "", cpgquery).replace("chr", ""), re.sub(".*:", "", cpgquery))
            data.sort(key=lambda tup: (tup[0], tup[2], float(tup[36])))
            return JsonResponse({'results':data, 'fields':fields})
        else:
            return JsonResponse({})
    elif regionquery:
        db = MySQLdb.connect(host=mysql_account[0], user=mysql_account[1], password=mysql_account[2], db=mysql_account[3])
        cur = db.cursor() 
        region = re.split(':|-',regionquery)
        chrom = region[0]
        start = region[1]
        end = region[2]
        if (int(end) - int(start)) <= 10000000:
            cur.execute("SELECT studies.*,results.* FROM results JOIN studies ON results.study_id=studies.study_id WHERE chr='"+chrom+"' AND pos>="+start+" AND pos<="+end)
            data = cur.fetchall()          
            data = [x[0:28]+x[29:39] for x in data]
            data += tabix_region_query(chrom, start, end)
            data = [x for x in data if float(x[36]) < 1e-4]
            data.sort(key=lambda tup: (tup[0], tup[2], float(tup[36])))
            return JsonResponse({'results':data, 'fields':fields})
        else:
            return JsonResponse({})
    elif genequery:
        db = MySQLdb.connect(host=mysql_account[0], user=mysql_account[1], password=mysql_account[2], db=mysql_account[3])
        cur = db.cursor() 
        genes = cur.execute("SELECT gene,ensembl_id,chr,start,end FROM genes WHERE gene='"+genequery+"'")
        if genes > 0:
            gene = list(cur.fetchall()[0])
            chrom = gene[2]
            start = str(gene[3])
            end = str(gene[4])
            cur.execute("SELECT studies.*,results.* FROM results JOIN studies ON results.study_id=studies.study_id WHERE chr='"+chrom+"' AND pos>="+start+" AND pos<="+end)
            data = cur.fetchall()          
            data = [x[0:28]+x[29:39] for x in data]
            data += tabix_region_query(chrom, start, end)
            data = [x for x in data if float(x[36]) < 1e-4]
            data.sort(key=lambda tup: (tup[0], tup[2], float(tup[36])))
            return JsonResponse({'results':data, 'fields':fields})
        else:
            return JsonResponse({})
    elif traitquery:
        db = MySQLdb.connect(host=mysql_account[0], user=mysql_account[1], password=mysql_account[2], db=mysql_account[3])
        cur = db.cursor() 
        efo_terms = efo(traitquery)
        efo_terms = not_efo(efo_terms)
        if efo_terms!="NULL":
            efo_query = efo_mysql(efo_terms)
            cur.execute(efo_query)
            data = cur.fetchall()          
            data = [x for x in data if float(x[37]) < 1e-7]
            efo_query_aries = efo_mysql_aries(efo_terms)
            cur.execute(efo_query_aries)
            data_aries = cur.fetchall()
            efo_query_geo = efo_mysql_geo(efo_terms)
            cur.execute(efo_query_geo)
            data_geo = cur.fetchall()
            data += [x for x in data_aries if float(x[37]) < 1e-7]            
            data += [x for x in data_geo if float(x[37]) < 1e-7]
            data = [x[0:28]+x[29:39] for x in data]
            data.sort(key=lambda tup: (tup[0], tup[2], float(tup[36])))
            return JsonResponse({'results':data, 'fields':fields})
        else:
            return JsonResponse({})
    else:
        return JsonResponse({})
