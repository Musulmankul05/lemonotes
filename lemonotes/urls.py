from django.contrib import admin
from django.urls import path, include
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.conf.urls.static import static
from notes.views import NotesView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', login_required(NotesView.as_view()), name='index'),
    path("", include("notes.urls")),
    path("", include("users.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
