from rest_framework import serializers
from .models import Fee, Payment


class FeeSerializer(serializers.ModelSerializer):
    classroom_name = serializers.CharField(source="classroom.__str__", read_only=True)
    paid = serializers.SerializerMethodField()
    remaining = serializers.SerializerMethodField()

    class Meta:
        model = Fee
        fields = ["id", "classroom", "classroom_name", "title", "amount", "due_date", "paid", "remaining"]

    def _student(self):
        u = self.context["request"].user
        return u if u.role == "STUDENT" else None

    def get_paid(self, obj):
        u = self._student()
        return obj.paid_by(u) if u else None

    def get_remaining(self, obj):
        u = self._student()
        return obj.remaining_for(u) if u else None


class PaymentSerializer(serializers.ModelSerializer):
    fee_title = serializers.CharField(source="fee.title", read_only=True)

    class Meta:
        model = Payment
        fields = ["id", "fee", "fee_title", "amount", "method", "phone", "status", "reference", "created"]
        read_only_fields = ["status", "reference"]
        extra_kwargs = {"amount": {"required": False}}

    def validate(self, data):
        user = self.context["request"].user
        fee = data["fee"]
        if not fee.classroom.enrollments.filter(student=user).exists():
            raise serializers.ValidationError("Vous n'êtes pas inscrit dans la classe de ces frais.")
        remaining = fee.remaining_for(user)
        if remaining <= 0:
            raise serializers.ValidationError("Ces frais sont déjà soldés.")
        data["amount"] = data.get("amount") or remaining
        if data["amount"] <= 0 or data["amount"] > remaining:
            raise serializers.ValidationError(f"Montant invalide (reste à payer : {remaining}).")
        return data
