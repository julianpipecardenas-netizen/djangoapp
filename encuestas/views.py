import os
import requests
import markdown
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import F
from django.http import HttpResponseRedirect
from django.urls import reverse
from .models import Producto, Opcion

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

MICROSERVICIOS = {
    "python": "https://microservicio-cafe.onrender.com",
    "java": "https://microservicio-java.onrender.com",
    "node": "https://microservicio-node.onrender.com",
    "php": "https://microservicio-php.onrender.com",
}

URL_LECTURA_PRINCIPAL = "https://microservicio-cafe.onrender.com/comentarios"
URL_LECTURA_RESPALDO = "https://microservicio-node-respaldo.onrender.com/comentarios"


def index(request):
    lista_productos = Producto.objects.order_by("-fecha_publicacion")
    return render(request, "encuestas/index.html", {"lista_productos": lista_productos})


def detail(request, producto_id):
    producto = get_object_or_404(Producto, pk=producto_id)
    return render(request, "encuestas/detail.html", {"producto": producto})


def vote(request, producto_id, opcion_id):
    producto = get_object_or_404(Producto, pk=producto_id)
    opcion = get_object_or_404(Opcion, pk=opcion_id, producto=producto)
    opcion.votos = F("votos") + 1
    opcion.save()
    return HttpResponseRedirect(reverse("encuestas:results", args=(producto.id,)))


def results(request, producto_id):
    producto = get_object_or_404(Producto, pk=producto_id)
    return render(request, "encuestas/results.html", {"producto": producto})


def comentarios_clientes(request):
    try:
        respuesta = requests.get(URL_LECTURA_PRINCIPAL, timeout=8)
        respuesta.raise_for_status()
        comentarios = respuesta.json()
        fuente = "principal (Python)"
    except (requests.exceptions.RequestException, ValueError):
        try:
            respuesta = requests.get(URL_LECTURA_RESPALDO, timeout=8)
            respuesta.raise_for_status()
            comentarios = respuesta.json()
            fuente = "respaldo (Node.js)"
        except (requests.exceptions.RequestException, ValueError):
            comentarios = []
            fuente = "ninguna fuente disponible"

    return render(request, "encuestas/comentarios.html", {"comentarios": comentarios, "fuente": fuente})


def agregar_comentario(request):
    lenguaje = request.GET.get("lenguaje", "java")
    if request.method == "POST":
        lenguaje = request.POST.get("lenguaje", lenguaje)
        url = f"{MICROSERVICIOS[lenguaje]}/comentarios"
        datos = {
            "nombre_cliente": request.POST.get("nombre_cliente"),
            "comentario": request.POST.get("comentario"),
            "calificacion": request.POST.get("calificacion"),
        }
        try:
            requests.post(url, json=datos, timeout=15)
        except requests.exceptions.RequestException:
            pass
        return redirect("encuestas:comentarios")
    return render(request, "encuestas/agregar_comentario.html", {"lenguaje": lenguaje})


def editar_comentario(request, comentario_id):
    lenguaje = request.GET.get("lenguaje", "java")
    if request.method == "POST":
        if "cancelar" in request.POST:
            return redirect("encuestas:comentarios")
        lenguaje = request.POST.get("lenguaje", lenguaje)
        url = f"{MICROSERVICIOS[lenguaje]}/comentarios/{comentario_id}"
        datos = {
            "nombre_cliente": request.POST.get("nombre_cliente"),
            "comentario": request.POST.get("comentario"),
            "calificacion": request.POST.get("calificacion"),
        }
        try:
            requests.put(url, json=datos, timeout=15)
        except requests.exceptions.RequestException:
            pass
        return redirect("encuestas:comentarios")

    try:
        r = requests.get(URL_LECTURA_PRINCIPAL, timeout=10)
        todos = r.json()
        comentario = next((c for c in todos if c["id"] == comentario_id), None)
    except requests.exceptions.RequestException:
        comentario = None
    return render(request, "encuestas/editar_comentario.html", {"comentario": comentario, "lenguaje": lenguaje})


def eliminar_comentario(request, comentario_id):
    lenguaje = request.GET.get("lenguaje", "java")
    if request.method == "POST":
        if "cancelar" in request.POST:
            return redirect("encuestas:comentarios")
        lenguaje = request.POST.get("lenguaje", lenguaje)
        url = f"{MICROSERVICIOS[lenguaje]}/comentarios/{comentario_id}"
        try:
            requests.delete(url, timeout=15)
        except requests.exceptions.RequestException:
            pass
        return redirect("encuestas:comentarios")
    return render(request, "encuestas/eliminar_comentario.html", {"comentario_id": comentario_id, "lenguaje": lenguaje})


def microservicios(request):
    return render(request, "encuestas/microservicios.html")


def preguntar_ia(request):
    respuesta_ia = None
    if request.method == "POST":
        pregunta = request.POST.get("pregunta")

        lineas_productos = []
        for p in Producto.objects.select_related("categoria").all():
            opciones_texto = ", ".join(
                f"{o.texto_opcion}: {o.votos} votos" for o in p.opciones.all()
            )
            categoria_nombre = p.categoria.nombre if p.categoria else "Sin categoría"
            lineas_productos.append(f"- {p.nombre} (Categoría: {categoria_nombre}) -> {opciones_texto}")
        texto_productos = "\n".join(lineas_productos) or "No hay productos registrados."

        try:
            r_comentarios = requests.get(URL_LECTURA_PRINCIPAL, timeout=10)
            lista_comentarios = r_comentarios.json()
        except requests.exceptions.RequestException:
            lista_comentarios = []

        lineas_comentarios = [
            f"- {c.get('nombre_cliente')}: \"{c.get('comentario')}\" (Calificación: {c.get('calificacion')}/5)"
            for c in lista_comentarios
        ]
        texto_comentarios = "\n".join(lineas_comentarios) or "No hay comentarios registrados."

        contexto = (
            "Eres un asistente de una cafetería que ayuda a interpretar resultados "
            "de una encuesta de satisfacción de productos y servicios. Responde solo "
            "sobre temas relacionados con esta cafetería: productos, categorías, votos "
            "de satisfacción y comentarios de clientes. Usa ÚNICAMENTE la información "
            "que se te da a continuación para responder; si la pregunta pide un filtro, "
            "conteo o listado, calcúlalo tú mismo a partir de estos datos.\n\n"
            f"PRODUCTOS Y SUS VOTOS:\n{texto_productos}\n\n"
            f"COMENTARIOS DE CLIENTES:\n{texto_comentarios}\n\n"
            f"Pregunta del usuario: {pregunta}"
        )

        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.5-flash-lite:generateContent?key={GEMINI_API_KEY}"
        payload = {"contents": [{"parts": [{"text": contexto}]}]}

        try:
            r = requests.post(url, json=payload, timeout=15)
            data = r.json()
            texto_bruto = data["candidates"][0]["content"]["parts"][0]["text"]
            respuesta_ia = markdown.markdown(texto_bruto)
        except (requests.exceptions.RequestException, KeyError, IndexError):
            respuesta_ia = "No se pudo obtener respuesta de la IA en este momento."

    return render(request, "encuestas/preguntar_ia.html", {"respuesta_ia": respuesta_ia})
