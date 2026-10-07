from django.contrib import admin
from .models import Partner, BusinessDocument, StockMovement, AccountingEntry

admin.site.register(Partner)
admin.site.register(BusinessDocument)
admin.site.register(StockMovement)
admin.site.register(AccountingEntry)
