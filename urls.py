
from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('inbox/', views.inbox_view, name='inbox'),
    path('outbox/', views.outbox_view, name='outbox'),
    path('compose/', views.compose_message_view, name='compose'),
    path('message/<int:message_id>/', views.view_message_view, name='view_message'),
]