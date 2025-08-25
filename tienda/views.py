# views.py
from django.shortcuts import render, get_object_or_404, redirect
from .models import Producto, Comentario, Proveedor, ContactoProveedor, Compra, DetalleCompra, Carrito, ItemCarrito
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.db import transaction
from django.http import HttpResponseForbidden
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login

def inicio(request):
    productos_destacados = Producto.objects.all()[:6]
    return render(request, 'inicio.html', {
        'productos_destacados': productos_destacados,
        'empresa_info': "Game Center es una tienda líder especializada en accesorios y mobiliario para videojuegos. Nuestra misión es brindar productos de calidad a gamers de todo el mundo."
    })

def catalogo_productos(request):
    productos = Producto.objects.all()
    filtro = request.GET.get('categoria')
    if filtro:
        productos = productos.filter(categoria=filtro)
    return render(request, 'catalogo.html', {
        'productos': productos,
        'categorias': Producto._meta.get_field('categoria').choices
    })

def detalle_producto(request, producto_id):
    producto = get_object_or_404(Producto, pk=producto_id)
    comentarios = Comentario.objects.filter(producto=producto).order_by('-fecha')
    return render(request, 'detalle.html', {'producto': producto, 'comentarios': comentarios})

@login_required
def agregar_comentario(request, producto_id):
    producto = get_object_or_404(Producto, pk=producto_id)
    if request.method == 'POST':
        texto = request.POST['texto']
        Comentario.objects.create(producto=producto, autor=request.user, texto=texto)
        messages.success(request, "Comentario agregado exitosamente.")
        return redirect('detalle_producto', producto_id=producto.id)
    return render(request, 'agregar_comentario.html', {'producto': producto})

@login_required
def editar_comentario(request, comentario_id):
    comentario = get_object_or_404(Comentario, pk=comentario_id)
    if comentario.autor != request.user:
        return HttpResponseForbidden("No tienes permiso para editar este comentario")
    if request.method == 'POST':
        texto = request.POST['texto']
        comentario.texto = texto
        comentario.save()
        messages.success(request, "Comentario actualizado.")
        return redirect('detalle_producto', producto_id=comentario.producto.id)
    return render(request, 'editar_comentario.html', {'comentario': comentario})

@login_required
def eliminar_comentario(request, comentario_id):
    comentario = get_object_or_404(Comentario, pk=comentario_id)
    if comentario.autor != request.user:
        return HttpResponseForbidden("No tienes permiso para eliminar este comentario")
    producto_id = comentario.producto.id
    comentario.delete()
    messages.success(request, "Comentario eliminado.")
    return redirect('detalle_producto', producto_id=producto_id)

@login_required
def contacto_proveedores(request):
    try:
        proveedor = request.user.proveedor
    except Proveedor.DoesNotExist:
        messages.error(request, "No estás registrado como proveedor.")
        return redirect('inicio')

    if request.method == 'POST':
        descripcion = request.POST.get('descripcion', '')
        archivo = request.FILES.get('archivo', None)
        if archivo and descripcion:
            contacto = ContactoProveedor.objects.create(proveedor=proveedor, descripcion=descripcion, archivo=archivo)
            messages.success(request, "Información enviada correctamente.")
            return render(request, 'contacto_exito.html', {'archivo': contacto.archivo.name})
        else:
            messages.error(request, "Por favor completa todos los campos y adjunta un archivo.")
    return render(request, 'contacto.html', {'proveedor': proveedor})

def registro(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Registro exitoso. ¡Bienvenido a Game Center!')
            return redirect('inicio')
    else:
        form = UserCreationForm()
    return render(request, 'registration/registro.html', {'form': form})

@login_required
def agregar_al_carrito(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)
    cantidad = int(request.POST.get('cantidad', 1))
    carrito, _ = Carrito.objects.get_or_create(usuario=request.user)

    item, creado = ItemCarrito.objects.get_or_create(
        carrito=carrito,
        producto=producto,
        defaults={'cantidad': cantidad}
    )

    if not creado:
        item.cantidad += cantidad
        item.save()

    messages.success(request, f'Se agregaron {cantidad} unidad(es) de {producto.nombre} al carrito.')
    return redirect('ver_carrito')


@login_required
def ver_carrito(request):
    carrito, creado = Carrito.objects.get_or_create(usuario=request.user)
    items = ItemCarrito.objects.filter(carrito=carrito)

    total = sum(item.producto.costo * item.cantidad for item in items)

    return render(request, 'carrito.html', {
        'items': items,
        'total': total
    })


@login_required
@transaction.atomic
def finalizar_compra(request):
    carrito_obj = Carrito.objects.filter(usuario=request.user).first()
    if not carrito_obj or not ItemCarrito.objects.filter(carrito=carrito_obj).exists():
        messages.error(request, "Tu carrito está vacío.")
        return redirect('catalogo_productos')

    compra = Compra.objects.create(usuario=request.user)

    items = ItemCarrito.objects.filter(carrito=carrito_obj)
    for item in items:
        producto = item.producto
        cantidad = item.cantidad
        if producto.existencia < cantidad:
            messages.error(request, f"No hay suficiente existencia para {producto.nombre}.")
            transaction.set_rollback(True)
            return redirect('ver_carrito')
        producto.existencia -= cantidad
        producto.save()
        DetalleCompra.objects.create(compra=compra, producto=producto, cantidad=cantidad, precio_unitario=producto.costo)

    items.delete()
    return render(request, 'gracias.html')

@login_required
def historial_compras(request):
    compras = Compra.objects.filter(usuario=request.user).order_by('-fecha')
    return render(request, 'historial.html', {'compras': compras})

@login_required
def editar_cantidad_carrito(request, item_id):
    if request.method == 'POST':
        item = get_object_or_404(ItemCarrito, id=item_id, carrito__usuario=request.user)
        cantidad_nueva = int(request.POST.get('cantidad', 1))
        if cantidad_nueva > 0 and cantidad_nueva <= item.producto.existencia:
            item.cantidad = cantidad_nueva
            item.save()
            messages.success(request, f'Cantidad actualizada para {item.producto.nombre}.')
        else:
            messages.error(request, 'Cantidad inválida o mayor a la existencia.')
    return redirect('ver_carrito')

@login_required
def eliminar_item_carrito(request, item_id):
    if request.method == 'POST':
        item = get_object_or_404(ItemCarrito, id=item_id, carrito__usuario=request.user)
        item.delete()
        messages.success(request, f'{item.producto.nombre} eliminado del carrito.')
    return redirect('ver_carrito')