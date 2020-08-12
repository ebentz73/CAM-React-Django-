from django.contrib.auth import get_permission_codename
from django.forms.models import model_to_dict
from guardian.shortcuts import get_objects_for_user


class ModelDiffMixin:
    """A model mixin that tracks model fields' values and provide some useful
    api to know what fields have been changed.

    Note: In concurrent environments where multiple requests can manipulate the
    same model instance at the same time, this is not a suitable approach.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__initial = self._dict

    @property
    def diff(self):
        d1 = self.__initial
        d2 = self._dict
        return {k: (v, d2[k]) for k, v in d1.items() if v != d2[k]}

    @property
    def has_changed(self):
        return bool(self.diff)

    @property
    def changed_fields(self):
        return self.diff.keys()

    def get_field_diff(self, field_name):
        """Returns a diff for field if it's changed and None otherwise."""
        return self.diff.get(field_name, None)

    def save(self, *args, **kwargs):
        """Saves model and set initial state."""
        super().save(*args, **kwargs)
        self.__initial = self._dict

    @property
    def _dict(self):
        return model_to_dict(self, fields=[field.name for field in self._meta.fields])


class PermissionMixin:
    def get_permission_codename(self, action):
        return self._get_permission_codename(action, self.model)

    def _get_permission_codename(self, action, model):
        opts = model._meta
        codename = get_permission_codename(action, opts)
        return '{}.{}'.format(opts.app_label, codename)

    def has_permission(self, request, obj, action):
        # We want all users to access list view but with a limited queryset
        # meanwhile only being able to access their model in change view
        perm = self.get_permission_codename(action)
        return request.user.has_perm(perm, obj) if obj is not None else True

    def has_view_permission(self, request, obj=None):
        return self.has_permission(request, obj, 'view')

    def has_change_permission(self, request, obj=None):
        return self.has_permission(request, obj, 'change')

    def has_delete_permission(self, request, obj=None):
        return self.has_permission(request, obj, 'delete')

    def has_module_permission(self, request):
        return True

    def get_queryset(self, request):
        perm = self.get_permission_codename('view')
        return get_objects_for_user(request.user, perm, self.model, accept_global_perms=False)

    def formfield_for_foreignkey(self, db_field, request=None, **kwargs):
        formfield = super().formfield_for_foreignkey(db_field, request=request, **kwargs)
        perm = self._get_permission_codename('change', db_field.related_model)
        formfield.queryset = get_objects_for_user(request.user, perm, formfield.queryset)
        return formfield
