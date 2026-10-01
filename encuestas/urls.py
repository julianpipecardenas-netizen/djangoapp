from django.urls import path
from . import views

app_name = "encuestas"
urlpatterns = [
    path("", views.index, name="index"),
    path("comentarios/", views.comentarios_clientes, name="comentarios"),
    path("comentarios/nuevo/", views.agregar_comentario, name="agregar_comentario"),
    path("comentarios/<int:comentario_id>/editar/", views.editar_comentario, name="editar_comentario"),
    path("comentarios/<int:comentario_id>/eliminar/", views.eliminar_comentario, name="eliminar_comentario"),
    path("microservicios/", views.microservicios, name="microservicios"),
    path("preguntar-ia/", views.preguntar_ia, name="preguntar_ia"),
    path("<int:producto_id>/", views.detail, name="detail"),
    path("<int:producto_id>/results/", views.results, name="results"),
    path("<int:producto_id>/vote/<int:opcion_id>/", views.vote, name="vote"),
]