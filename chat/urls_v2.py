from django.urls import path

from chat import views

app_name = 'chatv2'

urlpatterns = [
    path('threads/', views.ThreadCreateAPIView.as_view(), name='threads'),
    path('threads/<str:uuid>/messages/', views.MessageCreateV2APIView.as_view(), name='messages'),
]
