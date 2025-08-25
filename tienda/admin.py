from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import Producto, Comentario, Proveedor, ContactoProveedor, Compra, DetalleCompra, Carrito, ItemCarrito

class ProductoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'categoria', 'costo', 'existencia', 'proveedor')
    search_fields = ('nombre',)
    list_filter = ('categoria',)
    readonly_fields = ('imagen_preview',)

    def imagen_preview(self, obj):
        if obj.imagen:
            return f'<img src="{obj.imagen.url}" style="max-height: 100px;" />'
        return "-"
    imagen_preview.allow_tags = True
    imagen_preview.short_description = 'Vista previa'

class ComentarioAdmin(admin.ModelAdmin):
    list_display = ('producto', 'autor', 'fecha')
    search_fields = ('autor__username', 'texto')
    list_filter = ('fecha',)

class DetalleCompraInline(admin.TabularInline):
    model = DetalleCompra
    extra = 0
    readonly_fields = ('producto', 'cantidad', 'precio_unitario')
    can_delete = False

class CompraAdmin(admin.ModelAdmin):
    list_display = ('id', 'usuario', 'fecha')
    inlines = [DetalleCompraInline]
    list_filter = ('fecha', 'usuario')
    search_fields = ('usuario__username',)

class ProveedorInline(admin.StackedInline):
    model = Proveedor
    can_delete = False
    verbose_name_plural = 'Proveedores'

class UserAdmin(BaseUserAdmin):
    inlines = (ProveedorInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff')

class ContactoProveedorAdmin(admin.ModelAdmin):
    list_display = ('proveedor', 'descripcion', 'fecha_envio')
    readonly_fields = ('fecha_envio',)

admin.site.unregister(User)
admin.site.register(User, UserAdmin)
admin.site.register(Producto, ProductoAdmin)
admin.site.register(Comentario, ComentarioAdmin)
admin.site.register(Proveedor)
admin.site.register(ContactoProveedor, ContactoProveedorAdmin)
admin.site.register(Compra, CompraAdmin)
admin.site.register(Carrito)
admin.site.register(ItemCarrito)

admin.site.site_header = "Game Center - Administración"
admin.site.site_title = "Panel de Administración Game Center"
admin.site.index_title = "Bienvenido al Panel de Administración de Game Center"
