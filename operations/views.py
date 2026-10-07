from datetime import date
from decimal import Decimal
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db import models
from django.db.models import Q, Sum
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST
from users.models import UserRole
from materials.models import Material
from .forms import PartnerForm, DocumentForm, StockMovementForm, AccountingForm
from .models import Partner, BusinessDocument, StockMovement, AccountingEntry

MODULES = {
    'customers': {'title': 'Clientes', 'permission': 'customers', 'model': Partner, 'kind': 'customer', 'form': PartnerForm, 'columns': [('name', 'Nombre'), ('document', 'Documento'), ('email', 'Correo'), ('phone', 'Teléfono'), ('active', 'Estado')], 'search': ['name', 'document', 'email']},
    'suppliers': {'title': 'Proveedores', 'permission': 'suppliers', 'model': Partner, 'kind': 'supplier', 'form': PartnerForm, 'columns': [('name', 'Nombre'), ('document', 'Documento'), ('email', 'Correo'), ('phone', 'Teléfono'), ('active', 'Estado')], 'search': ['name', 'document', 'email']},
    'purchases': {'title': 'Compras', 'permission': 'purchases', 'model': BusinessDocument, 'kind': 'purchase', 'form': DocumentForm, 'columns': [('number', 'Número'), ('partner', 'Proveedor'), ('material', 'Material'), ('quantity', 'Cantidad'), ('total', 'Total'), ('status', 'Estado'), ('date', 'Fecha')], 'search': ['number', 'partner__name', 'material__name']},
    'sales': {'title': 'Ventas', 'permission': 'sales', 'model': BusinessDocument, 'kind': 'sale', 'form': DocumentForm, 'columns': [('number', 'Número'), ('partner', 'Cliente'), ('material', 'Material'), ('quantity', 'Cantidad'), ('total', 'Total'), ('status', 'Estado'), ('date', 'Fecha')], 'search': ['number', 'partner__name', 'material__name']},
    'inventory': {'title': 'Inventario', 'permission': 'inventory', 'model': StockMovement, 'form': StockMovementForm, 'columns': [('material', 'Material'), ('movement_type', 'Movimiento'), ('quantity', 'Cantidad'), ('date', 'Fecha'), ('notes', 'Observaciones')], 'search': ['material__name', 'notes']},
    'accounting': {'title': 'Contabilidad', 'permission': 'accounting', 'model': AccountingEntry, 'form': AccountingForm, 'columns': [('entry_type', 'Tipo'), ('description', 'Descripción'), ('amount', 'Valor'), ('date', 'Fecha'), ('reference', 'Referencia')], 'search': ['description', 'reference']},
}

def permission_for(user, module):
    if user.is_superuser:
        return 2
    return UserRole.objects.filter(user_id=user).aggregate(value=models.Max(f'role__{module}'))['value'] or 0

def get_module(user, slug, write=False):
    config = MODULES.get(slug)
    if not config or permission_for(user, config['permission']) < (2 if write else 1):
        return None
    return config

def scoped_queryset(config):
    queryset = config['model'].objects.all()
    if 'kind' in config:
        queryset = queryset.filter(kind=config['kind'])
    return queryset

@login_required
def module_list(request, slug):
    config = get_module(request.user, slug)
    if not config:
        return redirect('dashboard')
    queryset = scoped_queryset(config)
    search = request.GET.get('q', '').strip()
    if search:
        query = Q()
        for field in config['search']:
            query |= Q(**{f'{field}__icontains': search})
        queryset = queryset.filter(query)
    page = Paginator(queryset, 10).get_page(request.GET.get('page'))
    return render(request, 'operations/module_list.html', {
        'slug': slug, 'config': config, 'page_obj': page, 'search': search,
        'can_edit': permission_for(request.user, config['permission']) >= 2,
    })

@login_required
def module_create(request, slug):
    config = get_module(request.user, slug, write=True)
    if not config:
        return redirect('dashboard')
    form = config['form'](request.POST or None)
    if slug in ('purchases', 'sales'):
        form.fields['partner'].queryset = Partner.objects.filter(kind='supplier' if slug == 'purchases' else 'customer', active=True)
    if request.method == 'POST' and form.is_valid():
        record = form.save(commit=False)
        if 'kind' in config:
            record.kind = config['kind']
        record.created_by = request.user
        record.save()
        messages.success(request, f"{config['title'][:-1] if config['title'].endswith('s') else config['title']} creado correctamente.")
        return redirect('operations:list', slug=slug)
    return render(request, 'operations/module_form.html', {'slug': slug, 'config': config, 'form': form, 'title': f"Nuevo registro de {config['title'].lower()}"})

@login_required
def module_edit(request, slug, pk):
    config = get_module(request.user, slug, write=True)
    if not config:
        return redirect('dashboard')
    record = get_object_or_404(scoped_queryset(config), pk=pk)
    form = config['form'](request.POST or None, instance=record)
    if slug in ('purchases', 'sales'):
        form.fields['partner'].queryset = Partner.objects.filter(kind='supplier' if slug == 'purchases' else 'customer', active=True)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Registro actualizado correctamente.')
        return redirect('operations:list', slug=slug)
    return render(request, 'operations/module_form.html', {'slug': slug, 'config': config, 'form': form, 'title': f"Editar {config['title'].lower()}"})

@login_required
@require_POST
def module_delete(request, slug, pk):
    config = get_module(request.user, slug, write=True)
    if not config:
        return redirect('dashboard')
    get_object_or_404(scoped_queryset(config), pk=pk).delete()
    messages.success(request, 'Registro eliminado correctamente.')
    return redirect('operations:list', slug=slug)

@login_required
def reports(request):
    if permission_for(request.user, 'reporting') < 1:
        return redirect('dashboard')
    today = date.today()
    return render(request, 'operations/reports.html', {
        'customers': Partner.objects.filter(kind='customer').count(),
        'suppliers': Partner.objects.filter(kind='supplier').count(),
        'materials': Material.objects.count(),
        'stock': StockMovement.objects.aggregate(total=Sum(models.Case(models.When(movement_type='Salida', then=-models.F('quantity')), default=models.F('quantity'), output_field=models.DecimalField())) )['total'] or Decimal('0'),
        'purchases': BusinessDocument.objects.filter(kind='purchase', date__year=today.year, date__month=today.month).aggregate(total=Sum(models.F('quantity') * models.F('unit_price')))['total'] or Decimal('0'),
        'sales': BusinessDocument.objects.filter(kind='sale', date__year=today.year, date__month=today.month).aggregate(total=Sum(models.F('quantity') * models.F('unit_price')))['total'] or Decimal('0'),
        'income': AccountingEntry.objects.filter(entry_type='Ingreso', date__year=today.year, date__month=today.month).aggregate(total=Sum('amount'))['total'] or Decimal('0'),
        'expenses': AccountingEntry.objects.filter(entry_type='Gasto', date__year=today.year, date__month=today.month).aggregate(total=Sum('amount'))['total'] or Decimal('0'),
        'recent_sales': BusinessDocument.objects.filter(kind='sale').select_related('partner', 'material')[:5],
        'month': today.strftime('%B %Y'),
    })
