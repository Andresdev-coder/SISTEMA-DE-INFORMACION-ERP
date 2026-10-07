from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Material
from .forms import MaterialForm
from django.core.paginator import Paginator
from django.db import models
from users.models import UserRole
from django.contrib import messages
from django.views.decorators.http import require_POST


def _material_permission(user):
    if user.is_superuser:
        return 2
    return UserRole.objects.filter(user_id=user).aggregate(
        max_permission=models.Max('role__materials')
    )['max_permission'] or 0

# Create your views here.
@login_required
def material_list(request):
    max_permission = _material_permission(request.user)
    
    if max_permission == 0:
        return redirect('dashboard')
    
    material_list = Material.objects.all()
    
    id_material = request.GET.get('id_material', '').strip()
    name = request.GET.get('name', '').strip()
    material_type = request.GET.get('material_type', '').strip()
    status = request.GET.get('status', '').strip()
    
    if id_material:
        material_list = material_list.filter(id_material__icontains=id_material)
    if name:
        material_list = material_list.filter(name__icontains=name)
    if material_type:
        material_list = material_list.filter(material_type__icontains=material_type)
    if status is not None and status != '':
        material_list = material_list.filter(status=status)
        
    paginator = Paginator(material_list.order_by('name'), 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'materials/material_list.html', {
        'page_obj': page_obj,
        'filters': {'id_material': id_material, 'name': name, 'material_type': material_type, 'status': status},
        'can_edit': max_permission >= 2,
    })

@login_required
def material_create(request):
    
    if _material_permission(request.user) < 2:
        return redirect('dashboard')
    form = MaterialForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        material = form.save(commit=False)
        material.created_by = request.user
        material.save()
        messages.success(request, 'Material creado correctamente.')
        return redirect('materials:materials_list')
    return render(request, 'materials/material_form.html', {'form': form, 'title': 'Nuevo material'})


@login_required
def material_edit(request, pk):
    if _material_permission(request.user) < 2:
        return redirect('dashboard')
    material = get_object_or_404(Material, pk=pk)
    form = MaterialForm(request.POST or None, instance=material)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Material actualizado correctamente.')
        return redirect('materials:materials_list')
    return render(request, 'materials/material_form.html', {'form': form, 'title': 'Editar material'})


@login_required
@require_POST
def material_delete(request, pk):
    if _material_permission(request.user) < 2:
        return redirect('dashboard')
    get_object_or_404(Material, pk=pk).delete()
    messages.success(request, 'Material eliminado correctamente.')
    return redirect('materials:materials_list')
