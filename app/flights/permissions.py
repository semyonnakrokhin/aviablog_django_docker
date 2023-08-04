from django.core.exceptions import PermissionDenied
from django.http import Http404


class IsOwnerPermissionMixin:

    def has_permission(self):
        return self.get_passenger() == self.request.user

    def dispatch(self, request, *args, **kwargs):
        if not self.has_permission():
            raise Http404()

        return super().dispatch(request, *args, **kwargs)