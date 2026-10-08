"""Classes d'administration de base : ajoutent le mode « Voir » (lecture seule via ?_view=1)."""
from unfold.admin import ModelAdmin as _ModelAdmin
from unfold.admin import TabularInline as _TabularInline


class _ViewMode:
    @staticmethod
    def _viewing(request):
        return request.method == "GET" and "_view" in request.GET

    def has_change_permission(self, request, obj=None):
        if obj is not None and self._viewing(request):
            return False
        return super().has_change_permission(request, obj)

    def has_delete_permission(self, request, obj=None):
        if obj is not None and self._viewing(request):
            return False
        return super().has_delete_permission(request, obj)

    def has_add_permission(self, request, *args, **kwargs):
        if self._viewing(request):
            return False
        return super().has_add_permission(request, *args, **kwargs)


class ModelAdmin(_ViewMode, _ModelAdmin):
    pass


class TabularInline(_ViewMode, _TabularInline):
    pass
