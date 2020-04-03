from django.contrib import admin
from .models import Customer, Bill, Receipt, CustomerAccount, Payment

# Register your models here.
admin.site.register(Customer)
admin.site.register(CustomerAccount)
admin.site.register(Bill)
admin.site.register(Payment)
admin.site.register(Receipt)