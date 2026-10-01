from django.urls import path
from . import views

app_name = "categorias"
urlpatterns = [
    path("", views.lista_categorias, name="lista"),
    path("<int:categoria_id>/", views.productos_por_categoria, name="detalle"),
]