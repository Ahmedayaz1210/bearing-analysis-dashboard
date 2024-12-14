from django.urls import path
from . import views

app_name = 'analysis'

urlpatterns = [
    # connects dashboard view to the root URL
    path('', views.dashboard, name='dashboard'),
]