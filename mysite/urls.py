from django.contrib import admin
from django.urls import include, path
from django.views.generic import RedirectView

urlpatterns = [
    path("", RedirectView.as_view(pattern_name="encuestas:index")),
    path("encuestas/", include("encuestas.urls")),
    path("categorias/", include("categorias.urls")),
    path("admin/", admin.site.urls),
]