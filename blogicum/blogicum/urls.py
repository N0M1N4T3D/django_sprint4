from django.urls import include, path
from django.contrib import admin
from . import views 
from django.conf.urls.static import static
from django.conf import settings


urlpatterns = [ 
    path('', include('blog.urls', namespace='blog')), 
    path('', include('pages.urls', namespace='pages')), 
    path('admin/', admin.site.urls), 
    path('auth/', include('django.contrib.auth.urls')), 
    path("auth/registration/", views.registration, name="registration"), 
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler403 = 'pages.views.custom_403_csrf'
handler404 = 'pages.views.custom_404'
handler500 = 'pages.views.custom_500'