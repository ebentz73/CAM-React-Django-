from django.contrib import admin
from django.db.models import ManyToManyRel
from django.urls import resolve
from polymorphic.admin import StackedPolymorphicInline, PolymorphicInlineSupportMixin, PolymorphicParentModelAdmin, \
    PolymorphicChildModelAdmin

from app import models

admin.site.site_header = 'Cloud Analysis Manager Admin'
admin.site.site_title = 'Cloud Analysis Manager Admin'
admin.site.index_title = 'Cloud Analysis Manager site administration'


class InlineBase(admin.StackedInline):
    extra = 0
    show_change_link = True
    can_delete = False

    def has_change_permission(self, request, obj=None):
        # Make all inlines read-only
        return False


class ModelAdminBase(admin.ModelAdmin):

    def __new__(cls, model, admin_site):
        instance = super().__new__(cls)
        relations = cls._get_reverse_relations(model)
        inlines = [type(f'{rel.__qualname__}Inline', (InlineBase,),
                        {'model': rel, '__module__': __name__})
                   for rel in
                   relations]  # For unknown reasons, without __module__ the class would 'live' in the wrong place
        instance.inlines = inlines
        return instance

    @staticmethod
    def _get_reverse_relations(model):
        """Get all relations that have a reference to the given model."""
        return [field.through if isinstance(field, ManyToManyRel) else field.related_model
                for field in model._meta.get_fields()
                if field.auto_created and not field.concrete]


class HideModelBase(admin.ModelAdmin):
    def has_module_permission(self, request):
        # Hide this model from admin index
        return False


class HideModelAdmin(ModelAdminBase, HideModelBase):
    ...


@admin.register(models.Scenario)
class ScenarioAdmin(HideModelAdmin):
    readonly_fields = ['is_adhoc']


class InputInline(StackedPolymorphicInline):
    model = models.Input

    @property
    def child_inlines(self):
        """Get all input inline classes."""
        return [self._get_polymorphic_child(relation.related_model)
                for relation in self.model._meta.fields_map.values()]

    @staticmethod
    def _get_polymorphic_child(model_cls):
        """Create and return the base inline class for a polymorphic child."""
        class PolymorphicChildInline(StackedPolymorphicInline.Child):
            model = model_cls
            show_change_link = True

            def formfield_for_foreignkey(self, db_field, request, **kwargs):
                qs = super().formfield_for_foreignkey(db_field, request, **kwargs)
                if db_field.name == 'node':
                    solution = self.get_parent_object_from_request(request).solution
                    qs.queryset = qs.queryset.filter(model__solution=solution)
                return qs

            def get_parent_object_from_request(self, request):
                """Returns the parent object from the request or None.

                Note that this only works for Inlines, because the `parent_model`
                is not available in the regular admin.ModelAdmin as an attribute.
                """
                resolved = resolve(request.path_info)
                if resolved.kwargs:
                    return self.parent_model.objects.get(pk=resolved.kwargs['object_id'])
                return None

        return PolymorphicChildInline


class InputChildAdmin(PolymorphicChildModelAdmin, ModelAdminBase):
    base_model = models.Input


@admin.register(models.Input)
class InputAdmin(PolymorphicParentModelAdmin, HideModelBase):
    base_model = models.Input

    @property
    def child_models(self):
        """Get all child models."""
        return [relation.related_model for relation in self.model._meta.related_objects]


@admin.register(models.ExecutiveView)
class ExecutiveViewAdmin(PolymorphicInlineSupportMixin, admin.ModelAdmin):
    inlines = (InputInline,)


admin.site.register(models.AnalyticsSolution, ModelAdminBase)
admin.site.register(models.Model, HideModelAdmin)
admin.site.register(models.InputPage, HideModelAdmin)
admin.site.register(models.InputDataSet, HideModelAdmin)
admin.site.register(models.InputDataSetInputChoice, HideModelAdmin)
admin.site.register(models.EvalJob, HideModelAdmin)

admin.site.register(models.InputDataSetInput, InputChildAdmin)
admin.site.register(models.NumericInput, InputChildAdmin)
admin.site.register(models.SliderInput, InputChildAdmin)
