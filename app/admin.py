from django.contrib import admin
from polymorphic.admin import StackedPolymorphicInline, PolymorphicInlineSupportMixin

from app import models

admin.site.site_header = 'Cloud Analysis Manager Admin'
admin.site.site_title = 'Cloud Analysis Manager Admin'
admin.site.index_title = 'Cloud Analysis Manager site administration'

# model cls -> inline cls
# Changes what inline class is used for a model
inline_overrides = {}


class InlineBase(admin.StackedInline):
    # TODO: Can I unexclude 'name' when a new entry is being added?
    extra = 0
    show_change_link = True
    can_delete = False
    # exclude = ['name']

    def has_change_permission(self, request, obj=None):
        # make all inlines read-only
        return False


class ModelAdminBase(admin.ModelAdmin):

    def __new__(cls, model, admin_site):
        instance = super().__new__(cls)
        relations = cls._get_reverse_relations(model)
        inlines = [type(f'{rel.__qualname__}Inline', (inline_overrides.get(rel, InlineBase),), {'model': rel, '__module__': __name__})
                   for rel in relations]  # for unknown reasons, without __module__ the class would 'live' in the wrong place
        instance.inlines = inlines
        return instance

    @staticmethod
    def _get_reverse_relations(model):
        """Get all relations that have a reference to the given model."""
        return [field.related_model for field in model._meta.get_fields() if field.auto_created and not field.concrete]


class HideModelAdmin(ModelAdminBase):

    def has_module_permission(self, request):
        # hide this model from admin index
        return False


admin.site.register(models.EvalJob, ModelAdminBase)
admin.site.register(models.Model, HideModelAdmin)
admin.site.register(models.InputPage, HideModelAdmin)
admin.site.register(models.Node, HideModelAdmin)
admin.site.register(models.InputDataSet, HideModelAdmin)
admin.site.register(models.InputDataSetNode, HideModelAdmin)
admin.site.register(models.Scenario, HideModelAdmin)
admin.site.register(models.ScenarioDataSet, HideModelAdmin)
admin.site.register(models.ExecutiveView, ModelAdminBase)


class InputChoiceInline(StackedPolymorphicInline):
    model = models.InputChoice

    @property
    def child_inlines(self):
        """Get all the input choice inline classes."""
        return [self._get_polymorphic_child(relation.related_model)
                for relation in models.InputChoice._meta.fields_map.values()]

    @staticmethod
    def _get_polymorphic_child(model_cls):
        """Create and return the base inline class for a polymorphic child."""
        return type('PolymorphicChildInline', (StackedPolymorphicInline.Child,), {'show_change_link': True, 'model': model_cls})


@admin.register(models.Input)
class InputAdmin(PolymorphicInlineSupportMixin, admin.ModelAdmin):
    inlines = [InputChoiceInline]
    ordering = ['-order']

    def has_module_permission(self, request):
        # hide this model from admin index
        return False
