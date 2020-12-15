from django.forms.models import model_to_dict


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


class NestedViewSetMixin:
    # Slightly modified from `rest_framework_nested.viewsets.NestedViewSetMixin`.

    def get_queryset(self):
        """
        Filter the `QuerySet` based on its parents as defined in the
        `serializer_class.parent_lookup_kwargs`.
        """
        queryset = super().get_queryset()
        serializer_class = self.get_serializer_class()
        if hasattr(serializer_class, 'parent_lookup_kwargs') and hasattr(self, 'kwargs') and self.kwargs:
            orm_filters = {}
            for query_param, field_name in serializer_class.parent_lookup_kwargs.items():
                # Use Google's design pattern to handle searches across all sub-collections
                # https://cloud.google.com/apis/design/design_patterns#list_sub-collections
                if self.kwargs[query_param] != '-':
                    orm_filters[field_name] = self.kwargs[query_param]
            return queryset.filter(**orm_filters)
        return queryset
