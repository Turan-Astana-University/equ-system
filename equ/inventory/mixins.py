from django.http import HttpResponseForbidden

class SuperuserRequiredMixin:
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            return HttpResponseForbidden("Доступ запрещён")
        return super().dispatch(request, *args, **kwargs)