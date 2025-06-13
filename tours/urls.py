from django.urls import path
from . import views

urlpatterns = [
    path('', views.tour_list, name='tours'),
    path('<slug:slug>/', views.tour_detail, name='tour_detail'),
] 