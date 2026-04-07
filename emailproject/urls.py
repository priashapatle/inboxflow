from django.contrib import admin
from django.urls import path
from emailapp import views

urlpatterns = [
    path('admin/', admin.site.urls),

    path('', views.send_mail_page, name='send'),
    path('history/', views.history),
    path('dashboard/', views.dashboard),
    path('contacts/', views.contacts),

    path('login/', views.user_login, name='login'),
    path('register/', views.register),
    path('logout/', views.logout_view),
]