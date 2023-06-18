from django.urls import path
from . import views
urlpatterns = [
    path('', views.home),
    path('signup',views.register),
    path('activeated-account/',views.active_account),
    path('forget-password/',views.forget_password),
    path('change-password/',views.change_password)
]