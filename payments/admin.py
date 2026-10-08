from django.contrib import admin
from .models import Fee, Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ("reference", "student", "fee", "amount", "method", "status", "created")
    list_filter = ("status", "method")


admin.site.register(Fee)
