from django import forms
from .models import Material

class MaterialForm(forms.ModelForm):
    
    class Meta:
        model = Material
        fields = ['id_material', 'name', 'description', 'unit', 'material_type', 'status']
        widgets = {
            'id_material': forms.TextInput(attrs={'class': 'w-full rounded-lg border border-gray-300 px-3 py-2 focus:border-[#233b6e] focus:outline-none focus:ring-2 focus:ring-[#233b6e]/20', 'placeholder': 'Ej. MAT-001'}),
            'name': forms.TextInput(attrs={'class': 'w-full rounded-lg border border-gray-300 px-3 py-2 focus:border-[#233b6e] focus:outline-none focus:ring-2 focus:ring-[#233b6e]/20'}),
            'description': forms.Textarea(attrs={'class': 'w-full rounded-lg border border-gray-300 px-3 py-2 focus:border-[#233b6e] focus:outline-none focus:ring-2 focus:ring-[#233b6e]/20', 'rows': 3}),
            'unit': forms.TextInput(attrs={'class': 'w-full rounded-lg border border-gray-300 px-3 py-2 focus:border-[#233b6e] focus:outline-none focus:ring-2 focus:ring-[#233b6e]/20', 'placeholder': 'Unidad, kg, litro...'}),
            'material_type': forms.TextInput(attrs={'class': 'w-full rounded-lg border border-gray-300 px-3 py-2 focus:border-[#233b6e] focus:outline-none focus:ring-2 focus:ring-[#233b6e]/20'}),
            'status': forms.Select(attrs={'class': 'w-full rounded-lg border border-gray-300 bg-white px-3 py-2 focus:border-[#233b6e] focus:outline-none focus:ring-2 focus:ring-[#233b6e]/20'}, choices=[('Activo', 'Activo'), ('Inactivo', 'Inactivo')]),
        }

    def clean_id_material(self):
        value = self.cleaned_data.get('id_material')
        if value and Material.objects.filter(id_material__iexact=value).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError('Ya existe un material con este código.')
        return value
