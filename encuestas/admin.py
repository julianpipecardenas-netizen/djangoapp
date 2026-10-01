from django.contrib import admin
from .models import Producto, Opcion

class OpcionInline(admin.TabularInline):
    model = Opcion
    extra = 3

class ProductoAdmin(admin.ModelAdmin):
    fields = ["categoria", "nombre", "descripcion", "fecha_publicacion"]
    inlines = [OpcionInline]
    list_display = ["nombre", "categoria", "total_respuestas"]

admin.site.register(Producto, ProductoAdmin)