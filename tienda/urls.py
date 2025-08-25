from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.inicio, name='inicio'),
    path('productos/', views.catalogo_productos, name='catalogo_productos'),
    path('producto/<int:producto_id>/', views.detalle_producto, name='detalle_producto'),
    path('producto/<int:producto_id>/agregar_al_carrito/', views.agregar_al_carrito, name='agregar_al_carrito'),
    path('comentario/<int:producto_id>/', views.agregar_comentario, name='agregar_comentario'),
    path('comentario/editar/<int:comentario_id>/', views.editar_comentario, name='editar_comentario'),
    path('comentario/eliminar/<int:comentario_id>/', views.eliminar_comentario, name='eliminar_comentario'),
    path('contacto/', views.contacto_proveedores, name='contacto_proveedores'),
    path('registro/', views.registro, name='registro'),
    path('carrito/agregar/<int:producto_id>/', views.agregar_al_carrito, name='agregar_al_carrito'),
    path('carrito/', views.ver_carrito, name='ver_carrito'), 
    path('carrito/finalizar/', views.finalizar_compra, name='finalizar_compra'),
    path('historial/', views.historial_compras, name='historial_compras'),
    path('accounts/login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(next_page='inicio'), name='logout'),
    path('accounts/registro/', views.registro, name='registro'),
    path('logout/', auth_views.LogoutView.as_view(next_page='inicio'), name='logout'),
    path('carrito/editar/<int:item_id>/', views.editar_cantidad_carrito, name='editar_cantidad_carrito'),
    path('carrito/eliminar/<int:item_id>/', views.eliminar_item_carrito, name='eliminar_item_carrito'),
]
