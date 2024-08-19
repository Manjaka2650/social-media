
from django.contrib import admin
from django.urls import path,include
from django.http import HttpResponse
from . import settings
from django.conf.urls.static import static

# from django. import include
def home(request):
    return HttpResponse("Kaiza e",request)
urlpatterns = [
    path('admin/', admin.site.urls),
    path('',include('base.urls')),
    path('api-auth/',include('rest_framework.urls')),
    path('auth/',include('rest_authtoken.urls')),
    path('message/',include('ChatApp.urls'))

]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)