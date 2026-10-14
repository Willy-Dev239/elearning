import re

from rest_framework import serializers

from .models import FeeStructure, Installment, Payment


class InstallmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Installment
        fields = ("id", "fee", "label", "amount", "due_date", "order")


class FeeStructureSerializer(serializers.ModelSerializer):
    installments = InstallmentSerializer(many=True, read_only=True)
    total_amount = serializers.SerializerMethodField()

    class Meta:
        model = FeeStructure
        fields = (
            "id", "title", "academic_year", "description", "is_active",
            "total_amount", "installments",
        )

    def get_total_amount(self, obj) -> str:
        return str(sum(i.amount for i in obj.installments.all()))


class PaymentSerializer(serializers.ModelSerializer):
    target = serializers.SerializerMethodField()
    student_name = serializers.CharField(source="student.get_full_name", read_only=True)

    class Meta:
        model = Payment
        fields = (
            "id", "student", "student_name", "installment", "course", "target", "amount",
            "provider", "phone_number", "reference", "provider_transaction_id",
            "status", "created_at", "paid_at",
        )
        read_only_fields = (
            "student", "amount", "reference", "provider_transaction_id",
            "status", "created_at", "paid_at",
        )

    def get_target(self, obj) -> str:
        if obj.installment_id:
            return f"Scolarité — {obj.installment.label}"
        return f"Module — {obj.course.code}"

    def validate_phone_number(self, value):
        digits = re.sub(r"\D", "", value)
        if digits.startswith("257") and len(digits) == 11:
            digits = digits[3:]
        if len(digits) != 8:
            raise serializers.ValidationError("Numéro invalide (8 chiffres, indicatif +257 optionnel).")
        return f"+257{digits}"

    def validate(self, attrs):
        installment = attrs.get("installment")
        course = attrs.get("course")
        if bool(installment) == bool(course):
            raise serializers.ValidationError(
                "Indiquez soit 'installment' (tranche de scolarité), soit 'course' (module payant)."
            )
        user = self.context["request"].user
        if installment:
            if not installment.fee.is_active:
                raise serializers.ValidationError("Ces frais ne sont plus actifs.")
            attrs["amount"] = installment.amount
            already = Payment.objects.filter(
                student=user, installment=installment, status=Payment.Status.SUCCESS
            ).exists()
        else:
            if not course.is_paid:
                raise serializers.ValidationError("Ce cours est gratuit.")
            if not course.is_published:
                raise serializers.ValidationError("Ce cours n'est pas disponible.")
            attrs["amount"] = course.price
            already = Payment.objects.filter(
                student=user, course=course, status=Payment.Status.SUCCESS
            ).exists()
        if already:
            raise serializers.ValidationError("Ce paiement a déjà été effectué.")
        return attrs


class WebhookSerializer(serializers.Serializer):
    reference = serializers.CharField()
    status = serializers.ChoiceField(choices=[Payment.Status.SUCCESS, Payment.Status.FAILED])
    transaction_id = serializers.CharField(required=False, allow_blank=True, default="")
