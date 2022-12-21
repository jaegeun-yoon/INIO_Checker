from django.urls import path
from .views import *
from . import views

app_name = "inio"

urlpatterns = [
    path('', InioListView.as_view(), name='list'),
    path('add/', InioCreateView.as_view(), name='add'),
    path('domain_check/', views.domain_check, name='domain_check'),
    path('detail/<int:pk>/', InioDetailView.as_view(), name='detail'),
    path('update/<int:pk>/', InioUpdateView.as_view(), name='update'),
    path('delete/<int:pk>/', InioDeleteView.as_view(), name='delete'),
    path("URL/", URLClassifier, name="URLClassifier"),
    path("search/", SearchFormView.as_view(), name="search"),
    path('excel_upload/', views.excel_upload, name='excel_upload'),
    path('csv_upload/', views.csv_upload, name='csv_upload'),
    path('excel_download/', views.excel_download, name='excel_download'),
    path('csv_download/', views.csv_download, name='csv_download'),
    path('zip_download/', views.zip_download, name='zip_download'),
]