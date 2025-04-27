from django.urls import path
from main import views


urlpatterns = [
    path('', views.home, name='home'),
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('process_urls/', views.process_urls, name='process_urls'),
    path('chat_companion/', views.chat_companion, name='chat_companion'),
    path('memory_bank/', views.ai_memory_bank, name='memory_bank'),
     path('chat/', views.chat_companion, name='chat_companion'),
      path('delete_chat_turn/', views.delete_chat_turn, name='delete_chat_turn'),

]