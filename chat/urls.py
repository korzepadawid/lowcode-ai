from django.urls import path

from chat import views

app_name = 'chat'

urlpatterns = [
    path('threads/', views.ThreadCreateAPIView.as_view(), name='threads'),
    path('threads/<str:uuid>/messages/', views.MessageCreateAPIView.as_view(), name='messages'),
]
