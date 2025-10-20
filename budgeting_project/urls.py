from django.contrib import admin
from django.urls import path, include
from budget import views # <--- ADD THIS LINE

urlpatterns = [
    path('admin/', admin.site.urls),
    path('budget/', include('budget.urls')),
    path('accounts/', include('django.contrib.auth.urls')), # Django's built-in auth URLs
    path('accounts/register/', views.register, name='register'), # Custom registration URL
    path('', views.home, name='home'), # <--- ADD THIS LINE to map the root URL to your home view
]