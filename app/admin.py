from django.contrib import admin
from polymorphic.admin import StackedPolymorphicInline, PolymorphicInlineSupportMixin

from app import models

admin.site.site_header = 'Cloud Analysis Manager Admin'
admin.site.site_title = 'Cloud Analysis Manager Admin'
admin.site.index_title = 'Cloud Analysis Manager site administration'

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


@admin.register(models.AnalyticsSolution)
class AnalyticsSolution(ModelAdminBase, admin.ModelAdmin):
    change_form_template = 'app/change_form_update.html'

    def changeform_view(self, request, object_id, form_url='', extra_context=None):
        extra_context = {'solution_id' : object_id,
                         'view_type' : "analyticssolution"}
        return super(AnalyticsSolution,self).changeform_view(
            request, object_id, form_url, extra_context=extra_context)


@admin.register(models.ExecutiveView)
class ExecutiveView(ModelAdminBase, admin.ModelAdmin):
    change_form_template = 'app/change_form_update.html'

    def get_ip_page(self):
        ip_page = models.InputPage.objects.all().values_list('id','name')
        return ip_page

    def get_mod_scn(self):
        models1 = models.Model.objects.all().values_list('id','name')
        scenario = models.Scenario.objects.all().values_list('id', 'name')
        return (models1, scenario)

    def changeform_view(self, request, object_id, form_url='', extra_context=None):
        info = self.get_mod_scn()
        extra_context = {'models' : info[0],
        'scenarios' : info[1],
        'view_type' : "executive",
        'executive' : object_id,
        'ip_pages' : self.get_ip_page()
        }
        return super(ExecutiveView,self).changeform_view(
            request, object_id, form_url, extra_context=extra_context,
        )


@admin.register(models.EvalJob)
class EvalJob(HideModelAdmin, admin.ModelAdmin):
    change_form_template = 'app/exec_view.html'

    def changeform_view(self, request, object_id, form_url='', extra_context=None):
        return super(EvalJob,self).changeform_view(
            request, object_id, form_url, extra_context={'eval_id': object_id, 'view_type' : "evaljob"})


admin.site.register(models.Model, HideModelAdmin)
admin.site.register(models.InputPage, HideModelAdmin)
admin.site.register(models.InputDataSet, HideModelAdmin)
admin.site.register(models.InputPageDsAsc, HideModelAdmin)
admin.site.register(models.Scenario, HideModelAdmin)
admin.site.register(models.ScenarioDataSet, HideModelAdmin)
admin.site.register(models.InputChoice, HideModelAdmin)

'''
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
        return type('PolymorphicChildInline', (StackedPolymorphicInline.Child,),
                    {'show_change_link': True, 'model': model_cls})
'''


@admin.register(models.Input)
class InputAdmin(admin.ModelAdmin):
    ordering = ['-order']
    change_form_template = 'app/input_view.html'

    def has_module_permission(self, request):
        # hide this model from admin index
        return False

    def get_ip_page(self):
        ip_page = models.InputPage.objects.all().values_list('id','name')
        return ip_page

    def changeform_view(self, request, object_id, form_url='', extra_context=None):
        extra_context = {'ip_pages' : self.get_ip_page(),
                         'view_type' : "input"}
        return super(InputAdmin,self).changeform_view(
            request, object_id, form_url, extra_context=extra_context,
        )

