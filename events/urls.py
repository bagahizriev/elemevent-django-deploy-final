from django.urls import path, re_path
from . import views

urlpatterns = [
    path('<slug:slug>/', views.event_detail, name='event_detail'),
] 