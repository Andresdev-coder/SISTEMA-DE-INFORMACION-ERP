from datetime import date, timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

from materials.models import Material
from operations.models import Partner, BusinessDocument, StockMovement, AccountingEntry


class Command(BaseCommand):
    help = 'Carga datos de demostración para probar los módulos del ERP.'

    def handle(self, *args, **options):
        User = get_user_model()
        actor = User.objects.filter(is_superuser=True).first()
        today = date.today()

        customers = [
            Partner.objects.get_or_create(kind='customer', name='Comercial Andina SAS', defaults={'document': '900123456-1', 'email': 'compras@comercialandina.test', 'phone': '3005550101', 'address': 'Bogotá', 'active': True})[0],
            Partner.objects.get_or_create(kind='customer', name='Distribuciones del Norte', defaults={'document': '901234567-2', 'email': 'contacto@disnorte.test', 'phone': '3005550102', 'address': 'Medellín', 'active': True})[0],
        ]
        suppliers = [
            Partner.objects.get_or_create(kind='supplier', name='Suministros Industriales SAS', defaults={'document': '800765432-1', 'email': 'ventas@suministros.test', 'phone': '3005550201', 'address': 'Cali', 'active': True})[0],
            Partner.objects.get_or_create(kind='supplier', name='Empaques Colombia', defaults={'document': '830123456-7', 'email': 'pedidos@empaques.test', 'phone': '3005550202', 'address': 'Bogotá', 'active': True})[0],
        ]

        materials = []
        for code, name, description, unit, material_type in [
            ('DEMO-001', 'Resina industrial', 'Materia prima para producción', 'kg', 'Materia prima'),
            ('DEMO-002', 'Caja de cartón', 'Caja estándar para despacho', 'unidad', 'Empaque'),
            ('DEMO-003', 'Lámina de polietileno', 'Lámina de alta densidad', 'metro', 'Materia prima'),
        ]:
            material, _ = Material.objects.get_or_create(id_material=code, defaults={'name': name, 'description': description, 'unit': unit, 'material_type': material_type, 'status': 'Activo', 'created_by': actor})
            materials.append(material)

        document_data = [
            ('purchase', 'OC-DEMO-001', suppliers[0], materials[0], Decimal('120'), Decimal('8500'), 'Recibido', today - timedelta(days=5)),
            ('purchase', 'OC-DEMO-002', suppliers[1], materials[1], Decimal('300'), Decimal('1200'), 'Pendiente', today - timedelta(days=2)),
            ('sale', 'FV-DEMO-001', customers[0], materials[1], Decimal('80'), Decimal('2200'), 'Entregado', today - timedelta(days=3)),
            ('sale', 'FV-DEMO-002', customers[1], materials[2], Decimal('45'), Decimal('14500'), 'Aprobado', today),
        ]
        for kind, number, partner, material, quantity, unit_price, status, doc_date in document_data:
            BusinessDocument.objects.get_or_create(kind=kind, number=number, defaults={'partner': partner, 'material': material, 'quantity': quantity, 'unit_price': unit_price, 'status': status, 'date': doc_date, 'notes': 'Registro de demostración', 'created_by': actor})

        for material, movement_type, quantity, days_ago, note in [
            (materials[0], 'Entrada', Decimal('120'), 5, 'Recepción de compra de demostración'),
            (materials[1], 'Entrada', Decimal('300'), 2, 'Recepción de compra de demostración'),
            (materials[1], 'Salida', Decimal('80'), 1, 'Despacho de venta de demostración'),
            (materials[2], 'Entrada', Decimal('90'), 4, 'Inventario inicial de demostración'),
            (materials[2], 'Salida', Decimal('45'), 0, 'Despacho de venta de demostración'),
        ]:
            StockMovement.objects.get_or_create(material=material, movement_type=movement_type, quantity=quantity, date=today - timedelta(days=days_ago), notes=note, defaults={'created_by': actor})

        for entry_type, description, amount, reference, days_ago in [
            ('Ingreso', 'Venta de cajas de cartón', Decimal('176000'), 'DEMO-ING-001', 3),
            ('Ingreso', 'Venta de lámina de polietileno', Decimal('652500'), 'DEMO-ING-002', 0),
            ('Gasto', 'Compra de resina industrial', Decimal('1020000'), 'DEMO-GAS-001', 5),
            ('Gasto', 'Compra de empaques', Decimal('360000'), 'DEMO-GAS-002', 2),
        ]:
            AccountingEntry.objects.get_or_create(reference=reference, defaults={'entry_type': entry_type, 'description': description, 'amount': amount, 'date': today - timedelta(days=days_ago), 'created_by': actor})

        self.stdout.write(self.style.SUCCESS('Datos demo listos: clientes, proveedores, materiales, compras, ventas, inventario y contabilidad.'))
