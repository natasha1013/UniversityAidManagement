from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    
    path('admin/', admin.site.urls),
    path('', include('users.urls')),
    path('', include('programs.urls')),    
    path('feedbacks/', include('feedbacks.urls')),
    path('chats/', include('chats.urls')),
    path('programs/', include('programs.urls')),
    path('notifications/', include('notifications.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)