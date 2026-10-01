from django.shortcuts import render, get_object_or_404
from .models import Categoria


def lista_categorias(request):
    categorias = Categoria.objects.all()
    return render(request, "categorias/lista.html", {"categorias": categorias})


def productos_por_categoria(request, categoria_id):
    categoria = get_object_or_404(Categoria, pk=categoria_id)
    productos = categoria.productos.all()
    return render(request, "categorias/detalle.html", {"categoria": categoria, "productos": productos})