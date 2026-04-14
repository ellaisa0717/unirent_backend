from django.urls import path
from . import views

urlpatterns = [
    path('items/', views.item_list),       
    path('register/', views.register_user), 
]