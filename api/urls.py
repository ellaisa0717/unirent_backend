from django.urls import path
from . import views

urlpatterns = [
    path('items/', views.item_list),       
    path('register/', views.register_user),
    path('login/', views.login_user),
    path('profile/', views.user_profile),
    path('checkout/', views.checkout),
    path('my-rentals/', views.my_rentals),
]