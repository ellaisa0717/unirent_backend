from django.urls import path
from . import views
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path('items/', views.item_list),       
    path('register/', views.register_user),
    path('profile/', views.user_profile),
    path('checkout/', views.checkout),
    path('my-rentals/', views.my_rentals),
    path('update-profile/', views.update_profile),
    path('return-item/', views.return_item),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('my-rentals/<int:rental_id>/', views.delete_rental_record),
]