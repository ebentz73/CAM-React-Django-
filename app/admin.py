from django.contrib import admin
from django.db.models import ManyToManyRel

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


@admin.register(models.AnalyticsSolution)
class AnalyticsSolution(ModelAdminBase, admin.ModelAdmin):
    change_form_template = 'app/admin/change_form_update.html'
    exclude = ['file_url']

    def changeform_view(self, request, object_id=None, form_url='', extra_context=None):
        extra_context = {
            'view_type': 'analyticssolution',
            'solution_id': object_id,
        }
        return super().changeform_view(request, object_id, form_url, extra_context=extra_context)


@admin.register(models.ExecutiveView)
class ExecutiveView(ModelAdminBase, admin.ModelAdmin):
    change_form_template = 'app/admin/change_form_update.html'

    def changeform_view(self, request, object_id=None, form_url='', extra_context=None):
        extra_context = {
            'view_type': 'executive',
            'executive': object_id,
            'ip_pages': self._get_input_pages(),
        }
        return super().changeform_view(request, object_id, form_url, extra_context=extra_context)

    @staticmethod
    def _get_input_pages():
        return models.InputPage.objects.all().values_list('id', 'name')


@admin.register(models.EvalJob)
class EvalJob(HideModelAdmin, admin.ModelAdmin):
    change_form_template = 'app/admin/exec_view.html'

    def changeform_view(self, request, object_id=None, form_url='', extra_context=None):
        extra_context = {
            'view_type': 'evaljob',
            'eval_id': object_id,
        }
        return super().changeform_view(request, object_id, form_url, extra_context=extra_context)


@admin.register(models.Scenario)
class Scenario(HideModelAdmin, admin.ModelAdmin):
    readonly_fields = ['is_adhoc']


admin.site.register(models.Model, HideModelAdmin)
admin.site.register(models.InputPage, HideModelAdmin)
admin.site.register(models.InputDataSet, HideModelAdmin)
admin.site.register(models.InputDataSetInput, HideModelAdmin)
admin.site.register(models.InputDataSetInputChoice, HideModelAdmin)
admin.site.register(models.NumericInput, HideModelAdmin)
admin.site.register(models.SliderInput, HideModelAdmin)
