from django.views.generic.edit import CreateView, UpdateView, DeleteView, FormView
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from .models import Inio, Category
from .forms import SearchForm, UploadFileForm
from django.conf import settings

# Database
from django.db.models import Q
from django.db import connection

# Utils
import time
from datetime import datetime
from io import BytesIO as IO
import pandas as pd
import requests
import zipfile
import xlsxwriter
import csv
import os, os.path
from requests.exceptions import ConnectTimeout

class InioListView(LoginRequiredMixin, ListView):
    model = Inio
    context_object_name = 'inio'
    paginate_by = 20

    def dispatch(self, request, *args, **kwargs):
        object_list = Inio.objects.all()
        categories = Category.objects.all()
        return render(request, 'inio/inio_list.html', {'object_list': object_list, 'categories': categories})


class InioCreateView(LoginRequiredMixin, CreateView):
    model = Inio
    fields = ['category', 'domain', 'description', 'status']
    success_url = reverse_lazy('inio:list')
    template_name_suffix = '_create'

    def form_valid(self, form):
        if self.request.method == 'POST':
            form.instance.owner_id = self.request.user.id

            if form.is_valid():
                instance = form.save(commit=False)

                if not instance.domain:
                    return self.render_to_response({'form': form})

                instance.status = False
                instance.save()

                return HttpResponseRedirect('/')


class InioDetailView(LoginRequiredMixin, DetailView):
    model = Inio

    def checker_detail(request, id):
        object = get_object_or_404(Inio, id=id)
        return render(request, 'inio/inio_detail.html', {'object': object})


class InioUpdateView(LoginRequiredMixin, UpdateView):
    model = Inio
    fields = ['category', 'domain', 'description', 'status']
    template_name_suffix = '_update'

    def form_valid(self, form):
        print("form_valid")
        if self.request.method == 'POST':
            form.instance.owner_id = self.request.user.id

            if form.is_valid():
                instance = form.save(commit=False)

                if not instance.domain:
                    return self.render_to_response({'form': form})

                object_list = Inio.objects.all()

                instance.save()

                return redirect('inio:list')
            else:
                return self.render_to_response({'form': form})


class InioDeleteView(LoginRequiredMixin, DeleteView):
    model = Inio
    success_url = reverse_lazy('inio:list')


class SearchFormView(FormView):
    form_class = SearchForm

    def form_valid(self, form):
        # sql query string 테스트
        KeyWord = "%s" % self.request.POST['search_keyword']
        Inio_list = Inio.objects.filter(
            Q(domain__icontains=KeyWord))

        print("Search Keyword : ", Inio_list)

        context = {}
        context['form'] = form
        context['search_word'] = KeyWord
        context['Inio_list'] = Inio_list
        return render(self.request, 'inio/search_result.html', context)


def URLClassifier(request):
    if request.method == 'POST':
        category = str(request.POST['category'])
        categories = Category.objects.all()

        if (not category) or (category == "0"):
            object_list = Inio.objects.all()
            return render(request, 'inio/inio_list.html', {'object_list': object_list, 'categories': categories})

        object_list = Inio.objects.filter(category__exact=category)
        return render(request, 'inio/inio_list.html', {'object_list': object_list, 'categories': categories})


@login_required
def domain_check(request):
    if request.POST:
        select_url = request.POST.getlist('select_url')
        url_list = Inio.objects.filter(pk__in=select_url)

        for url in url_list:
            try:
                res = requests.get(url.domain, timeout=1)
            except ConnectTimeout:
                continue
            except:
                continue
            print(url.domain, url.status, res.status_code)
            if res.status_code == 200 or res.status_code == 302:
                url.status = True
            url.save()

    object_list = Inio.objects.all()
    categories = Category.objects.all()
    return render(request, 'inio/inio_list.html', {'object_list': object_list, 'categories': categories})

@login_required
def excel_download(request):
    object_list = Inio.objects.all()
    df = pd.DataFrame.from_records(object_list.values())

    # remove id
    df = df.drop(columns=["id"])

    # timezone
    for col in df.select_dtypes(['datetimetz']).columns:
        df[col] = df[col].dt.tz_localize(None)

    excel_file = IO()

    xlwriter = pd.ExcelWriter(excel_file, mode="w+", engine="xlsxwriter")
    df.to_excel(xlwriter, header=True, index=False, sheet_name="Domain List")
    xlwriter.save()
    excel_file.seek(0)

    response = HttpResponse(excel_file.read(),
                            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                            charset="utf-8")
    response['Content-Disposition'] = 'attachment; filename=DomainList_' + str(time.time()) + '.xlsx'
    return response


@login_required
def csv_download(request):
    object_list = Inio.objects.all()
    df = pd.DataFrame.from_records(object_list.values())

    # remove id
    df = df.drop(columns=["id"])

    # timezone
    for col in df.select_dtypes(['datetimetz']).columns:
        df[col] = df[col].dt.tz_localize(None)

    response = HttpResponse(content_type='text/csv', charset="utf-8")
    response['Content-Disposition'] = 'attachment; filename=DomainList_' + str(time.time()) + '.csv'

    df.to_csv(path_or_buf=response, header=True, index=False)
    return response


@login_required
def zip_download(request):
    object_list = Inio.objects.all()
    df = pd.DataFrame.from_records(object_list.values())

    # remove id
    df = df.drop(columns=["id"])

    # timezone
    for col in df.select_dtypes(['datetimetz']).columns:
        df[col] = df[col].dt.tz_localize(None)

    zipname = IO()

    with zipfile.ZipFile(zipname, "w", zipfile.ZIP_DEFLATED) as zf:
        with zf.open("Domain_List.xlsx", "w") as buffer:
            with pd.ExcelWriter(buffer) as writer:
                df.to_excel(writer, header=True, index=False, sheet_name="in, io domain lists")

    response = HttpResponse(zipname.getvalue(), content_type='application/x-zip-compressed', charset="utf-8")
    response['Content-Disposition'] = 'attachment; filename=DomainList_' + str(time.time()) + '.zip'

    return response


@login_required
def excel_upload(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()

            filename = request.FILES['file']

            df = pd.read_excel(filename, engine="openpyxl")
            df = pd.DataFrame(df, columns=['domain'])
            df = df.fillna('')

            try:
                for domain in df['domain']:

                    if not domain == '':
                        Inio(category=Category(id=7), domain=domain).save() # category : etc
                    else:
                        pass
            except:
                return render(request, 'inio/inio_error.html')

            os.remove(os.path.join(settings.MEDIA_ROOT, str(filename)))

            return HttpResponseRedirect('/')
    else:
        form = UploadFileForm()
        return render(request, 'inio/inio_upload.html', {'form': form})


@login_required
def csv_upload(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()

            filename = request.FILES['file']
            file_path = os.path.join(settings.MEDIA_ROOT, str(filename))

            df = pd.read_csv(file_path, encoding='utf-8')
            df = pd.DataFrame(df, columns=['domain'])
            df = df.fillna('')

            try:
                for domain in df['domain']:
                    domain = domain.strip()
                    domain_ext = domain.split('.')

                    # in, io domain filtering
                    if ('in' in domain_ext[-1]) or ('io' in domain_ext[-1]):
                        try:
                            protocol = domain.split('://')

                            if (protocol[0] == 'https') or (protocol[0] == 'http') :
                                psss
                            else:
                                domain = "https://" + domain

                            Inio(category=Category(id=7), domain=domain).save() # category : etc
                        except:
                            pass
                    else:
                        pass
            except:
                return render(request, 'inio/inio_error.html')

            os.remove(os.path.join(settings.MEDIA_ROOT, str(filename)))

            return HttpResponseRedirect('/')
    else:
        form = UploadFileForm()
        return render(request, 'inio/inio_upload.html', {'form': form})