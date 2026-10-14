from django.contrib import admin

from .models import FeeStructure, Installment, Payment


class InstallmentInline(admin.TabularInline):
    model = Installment
    extra = 1


@admin.register(FeeStructure)
class FeeStructureAdmin(admin.ModelAdmin):
    list_display = ("title", "academic_year", "is_active")
    inlines = [InstallmentInline]


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ("reference", "student", "amount", "provider", "status", "created_at")
    list_filter = ("status", "provider")
    search_fields = ("reference", "student__username", "phone_number")
