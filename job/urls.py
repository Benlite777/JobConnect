from django.contrib import admin
from django.urls import path, include
import debug_toolbar  # Assuming you have django-debug-toolbar installed

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('jobapp.urls')),  # Example for jobapp URLs
    path('', include('account.urls')),  # Example for account URLs
    path('__debug__/', include(debug_toolbar.urls)),
    
]
