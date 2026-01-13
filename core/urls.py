# core/urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),

    # include accounts urls with explicit namespace
    path('accounts/', include(('accounts.urls', 'accounts'), namespace='accounts')),


    # include academic_core urls (app namespace already defined inside)
    path('', include(('academic_core.urls', 'academic_core'), namespace='academic_core')),
    

]

# serve media & static in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
