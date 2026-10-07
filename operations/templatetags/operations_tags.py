from django import template

register = template.Library()

@register.filter
def field_value(record, field_name):
    value = record
    for part in field_name.split('.'):
        value = getattr(value, part, '')
        if callable(value):
            value = value()
    if isinstance(value, bool):
        return 'Activo' if value else 'Inactivo'
    return value if value not in (None, '') else '—'
