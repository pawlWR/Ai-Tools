from django.urls import path
from . import views
urlpatterns = [
    # path('test', views.test, name='test'),
    path('test2', views.test2, name='test2'),
    path('test_check', views.test_check, name='test_check'),
]
