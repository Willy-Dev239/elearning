from django.contrib import admin
from unfold.admin import ModelAdmin
from unfold.decorators import display

from .models import Fee, Payment


@admin.register(Fee)
class FeeAdmin(ModelAdmin):
    list_display = ("title", "classroom", "amount", "due_date")
    list_filter = ("classroom",)
    search_fields = ("title",)


@admin.register(Payment)
class PaymentAdmin(ModelAdmin):
    list_display = ("reference", "student", "fee", "amount", "method", "status_label", "created")
    list_filter = ("status", "method")
    search_fields = ("reference", "student__username", "student__last_name")
    readonly_fields = ("reference", "created")

    @display(description="Statut", label={"Payé": "success", "Échoué": "danger"})
    def status_label(self, obj):
        return obj.get_status_display()
