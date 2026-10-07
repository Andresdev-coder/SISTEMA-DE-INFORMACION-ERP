from django import forms
from django.forms import modelform_factory
from .models import Partner, BusinessDocument, StockMovement, AccountingEntry

WIDGET = 'w-full rounded-lg border border-gray-300 px-3 py-2 focus:border-[#233b6e] focus:outline-none focus:ring-2 focus:ring-[#233b6e]/20'
def form_for(model, fields):
    widgets = {field.name: forms.Textarea(attrs={'class': WIDGET, 'rows': 3}) if isinstance(field, forms.CharField) and field.max_length is None else forms.Select(attrs={'class': WIDGET}) if field.choices else forms.TextInput(attrs={'class': WIDGET}) for field in model._meta.fields if field.name in fields}
    for name in fields:
        if name in ('date',):
            widgets[name] = forms.DateInput(attrs={'class': WIDGET, 'type': 'date'})
        elif name in ('quantity', 'unit_price', 'amount'):
            widgets[name] = forms.NumberInput(attrs={'class': WIDGET, 'step': '0.01', 'min': '0.01'})
        elif name == 'material':
            widgets[name] = forms.Select(attrs={'class': WIDGET})
        elif name == 'partner':
            widgets[name] = forms.Select(attrs={'class': WIDGET})
        elif name == 'active':
            widgets[name] = forms.CheckboxInput(attrs={'class': 'h-4 w-4 rounded border-gray-300 text-[#233b6e] focus:ring-[#233b6e]'})
    return modelform_factory(model, fields=fields, widgets=widgets)

PartnerForm = form_for(Partner, ['name', 'document', 'email', 'phone', 'address', 'active'])
DocumentForm = form_for(BusinessDocument, ['number', 'partner', 'material', 'quantity', 'unit_price', 'status', 'date', 'notes'])
StockMovementForm = form_for(StockMovement, ['material', 'movement_type', 'quantity', 'date', 'notes'])
AccountingForm = form_for(AccountingEntry, ['entry_type', 'description', 'amount', 'date', 'reference'])
