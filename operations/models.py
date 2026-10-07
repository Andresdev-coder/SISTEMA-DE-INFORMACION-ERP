from django.conf import settings
from django.db import models
from django.db.models import Sum
from materials.models import Material


class Partner(models.Model):
    CUSTOMER = 'customer'
    SUPPLIER = 'supplier'
    KIND_CHOICES = [(CUSTOMER, 'Cliente'), (SUPPLIER, 'Proveedor')]
    kind = models.CharField(max_length=12, choices=KIND_CHOICES, db_index=True)
    name = models.CharField(max_length=120, verbose_name='Nombre / razón social')
    document = models.CharField(max_length=30, blank=True, verbose_name='NIT / documento')
    email = models.EmailField(blank=True, verbose_name='Correo electrónico')
    phone = models.CharField(max_length=30, blank=True, verbose_name='Teléfono')
    address = models.CharField(max_length=200, blank=True, verbose_name='Dirección')
    active = models.BooleanField(default=True, verbose_name='Activo')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Cliente o proveedor'

    def __str__(self):
        return self.name


class BusinessDocument(models.Model):
    PURCHASE = 'purchase'
    SALE = 'sale'
    KIND_CHOICES = [(PURCHASE, 'Compra'), (SALE, 'Venta')]
    STATUS_CHOICES = [('Pendiente', 'Pendiente'), ('Aprobado', 'Aprobado'), ('Recibido', 'Recibido'), ('Entregado', 'Entregado'), ('Cancelado', 'Cancelado')]
    kind = models.CharField(max_length=10, choices=KIND_CHOICES, db_index=True)
    number = models.CharField(max_length=30, blank=True, verbose_name='Número')
    partner = models.ForeignKey(Partner, on_delete=models.PROTECT, verbose_name='Cliente / proveedor')
    material = models.ForeignKey(Material, on_delete=models.PROTECT, verbose_name='Material')
    quantity = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='Cantidad')
    unit_price = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='Precio unitario')
    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default='Pendiente')
    date = models.DateField(verbose_name='Fecha')
    notes = models.CharField(max_length=250, blank=True, verbose_name='Observaciones')
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date', '-pk']
        verbose_name = 'Compra o venta'

    @property
    def total(self):
        return self.quantity * self.unit_price

    def __str__(self):
        return self.number or f'{self.get_kind_display()} #{self.pk}'


class StockMovement(models.Model):
    TYPES = [('Entrada', 'Entrada'), ('Salida', 'Salida'), ('Ajuste', 'Ajuste')]
    material = models.ForeignKey(Material, on_delete=models.PROTECT, verbose_name='Material')
    movement_type = models.CharField(max_length=10, choices=TYPES, verbose_name='Movimiento')
    quantity = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='Cantidad')
    date = models.DateField(verbose_name='Fecha')
    notes = models.CharField(max_length=250, blank=True, verbose_name='Observaciones')
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date', '-pk']
        verbose_name = 'Movimiento de inventario'

    @property
    def signed_quantity(self):
        return -self.quantity if self.movement_type == 'Salida' else self.quantity


class AccountingEntry(models.Model):
    TYPES = [('Ingreso', 'Ingreso'), ('Gasto', 'Gasto')]
    entry_type = models.CharField(max_length=10, choices=TYPES, verbose_name='Tipo')
    description = models.CharField(max_length=160, verbose_name='Descripción')
    amount = models.DecimalField(max_digits=14, decimal_places=2, verbose_name='Valor (COP)')
    date = models.DateField(verbose_name='Fecha')
    reference = models.CharField(max_length=40, blank=True, verbose_name='Referencia')
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date', '-pk']
        verbose_name = 'Movimiento contable'

    def __str__(self):
        return self.description
