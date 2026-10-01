from django.db import models
from categorias.models import Categoria

class Producto(models.Model):
    nombre = models.CharField("nombre del producto o servicio", max_length=200)
    descripcion = models.TextField(blank=True)
    categoria = models.ForeignKey(
        Categoria, on_delete=models.SET_NULL, null=True, blank=True, related_name="productos"
    )
    fecha_publicacion = models.DateTimeField("fecha de publicación")

    def __str__(self):
        return self.nombre

    def total_respuestas(self):
        return sum(opcion.votos for opcion in self.opciones.all())

class Opcion(models.Model):
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name="opciones")
    texto_opcion = models.CharField("nivel de satisfacción", max_length=200)
    votos = models.IntegerField(default=0)

    def __str__(self):
        return self.texto_opcion