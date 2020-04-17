from django.contrib import admin
from django.db.models import ManyToManyRel
from polymorphic.admin import StackedPolymorphicInline, PolymorphicInlineSupportMixin, PolymorphicParentModelAdmin, \
    PolymorphicChildModelAdmin

from app import models

admin.site.site_header = 'Cloud Analysis Manager Admin'
admin.site.site_title = 'Cloud Analysis Manager Admin'
admin.site.index_title = 'Cloud Analysis Manager site administration'

# Can be used to specify a different Inline class for a relation
inline_overrides = {}


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
        inlines = [type(f'{rel.__qualname__}Inline', (inline_overrides.get(rel, InlineBase),),
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


class HideModelAdmin(ModelAdminBase):

    def has_module_permission(self, request):
        # Hide this model from admin index
        return False


@admin.register(models.Scenario)
class Scenario(HideModelAdmin):
    readonly_fields = ['is_adhoc']


admin.site.register(models.AnalyticsSolution, ModelAdminBase)
admin.site.register(models.Model, HideModelAdmin)
admin.site.register(models.InputPage, HideModelAdmin)
admin.site.register(models.InputDataSet, HideModelAdmin)
admin.site.register(models.InputDataSetInputChoice, HideModelAdmin)
admin.site.register(models.EvalJob, HideModelAdmin)


class ExecutiveViewChildAdmin(PolymorphicChildModelAdmin):
    base_model = models.ExecutiveView


@admin.register(models.InputDataSetInput)
class InputDataSetInputAdmin(ExecutiveViewChildAdmin):
    class InputDataSetInputChoiceInline(admin.StackedInline):
        model = models.InputDataSetInputChoice
        extra = 0

    base_model = models.InputDataSetInput
    inlines = (InputDataSetInputChoiceInline,)


@admin.register(models.NumericInput)
class NumericInputAdmin(ExecutiveViewChildAdmin):
    base_model = models.NumericInput


@admin.register(models.SliderInput)
class SliderInputAdmin(ExecutiveViewChildAdmin):
    base_model = models.SliderInput


class InputInline(StackedPolymorphicInline):
    class InputDataSetInputInline(StackedPolymorphicInline.Child):
        model = models.InputDataSetInput
        show_change_link = True

    class NumericInputInline(StackedPolymorphicInline.Child):
        model = models.NumericInput

    class SliderInputInline(StackedPolymorphicInline.Child):
        model = models.SliderInput

    model = models.Input
    child_inlines = (
        InputDataSetInputInline,
        NumericInputInline,
        SliderInputInline,
    )


@admin.register(models.ExecutiveView)
class ExecutiveViewAdmin(PolymorphicInlineSupportMixin, admin.ModelAdmin):
    inlines = (InputInline,)


@admin.register(models.Input)
class InputAdmin(PolymorphicParentModelAdmin):
    base_mode = models.Input
    child_models = (models.InputDataSetInput, models.NumericInput, models.SliderInput)

    def has_module_permission(self, request):
        # Hide this model from admin index
        return False
