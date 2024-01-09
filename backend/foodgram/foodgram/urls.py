from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from users.views import AuthViewSet

router = DefaultRouter()
router.register('', AuthViewSet, basename='users')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/users/', include(router.urls)),
    path('api/', include('api.urls')),
    path('api/auth/', include('djoser.urls.authtoken')),
]

# write static
from django.conf import settings
from django.conf.urls.static import static

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
