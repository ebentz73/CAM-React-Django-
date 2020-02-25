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

@admin.register(models.AnalyticsSolution)
class AnalyticsSolution(ModelAdminBase, admin.ModelAdmin):
    change_form_template = 'app/solution_view.html'

    def json_data(self,object_id):
        solution={}
        scenario = models.Scenario.objects.filter(solution=object_id).values_list('id', 'name')
        model = models.Model.objects.filter(solution=object_id).values_list('id', 'name')
        input_pg = models.InputPage.objects.filter(model=model[0]).values_list('id', 'name')
        input_ds=[]
        for i in input_pg:
            temp = models.InputDataSet.objects.filter(input_page=i[0]).values_list('id', 'name')
            input_ds.append(temp)
        solution["analytics_job_id"] = object_id
        solution["tam_model_url"] = models.AnalyticsSolution.objects.filter(id=object_id).values_list('file_url')[0][0]
        model_temp=[]
        for i in model:
            temp1 = {}
            temp1["name"]=i[1]
            temp1["input_data_sets"]=[j[1] for j in input_ds[0]]
            model_temp.append(temp1)
        solution["scenarios"]=[]

        for i in scenario:
            temp2 = {}
            temp2["name"]=i[1]
            temp2["models"]=[]
            temp2["models"].extend(model_temp)
            solution["scenarios"].append(temp2)
        return solution

    def changeform_view(self, request, object_id, form_url='', extra_context=None):
        extra_context = {}
        extra_context['json_data'] = self.json_data(object_id)
        return super(AnalyticsSolution,self).changeform_view(
            request, object_id, form_url, extra_context=extra_context,
        )


@admin.register(models.ExecutiveView)
class ExecutiveView(ModelAdminBase, admin.ModelAdmin):
    change_form_template = 'app/change_view.html'

    def get_osm_info(self):
        models1 = models.Model.objects.all().values_list('id','name')
        scenario = models.Scenario.objects.all().values_list('id', 'name')
        return (models1, scenario)

    def changeform_view(self, request, object_id, form_url='', extra_context=None):
        extra_context = {}
        info = self.get_osm_info()
        extra_context['models'] = info[0]
        extra_context['scenarios'] = info[1]
        extra_context['view_type'] = "executive"
        return super(ExecutiveView,self).changeform_view(
            request, object_id, form_url, extra_context=extra_context,
        )


'''
class ExecutiveViewAdmin(admin.ModelAdmin):
    
 
    def __new__(cls, model, admin_site):
        instance = super().__new__(cls)
        relations = cls._get_reverse_relations(model)
        inlines = [type(f'{rel.__qualname__}Inline', (inline_overrides.get(rel, InlineBase),),
                        {'model': rel, '__module__': __name__})
                   for rel in
                   relations]  # for unknown reasons, without __module__ the class would 'live' in the wrong place
        instance.inlines = inlines
        return instance

    @staticmethod
    def _get_reverse_relations(model):
        """Get all relations that have a reference to the given model."""
        return [field.related_model for field in model._meta.get_fields() if field.auto_created and not field.concrete]
'''

#admin.site.register(models.AnalyticsSolution, ModelAdminBase)
admin.site.register(models.Model, HideModelAdmin)
admin.site.register(models.InputPage, HideModelAdmin)
admin.site.register(models.InputDataSet, HideModelAdmin)
admin.site.register(models.InputPageDsAsc, HideModelAdmin)
admin.site.register(models.Scenario, HideModelAdmin)
admin.site.register(models.ScenarioDataSet, HideModelAdmin)
admin.site.register(models.EvalJob, HideModelAdmin)
#admin.site.register(models.ExecutiveView, ModelAdminBase)


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


@admin.register(models.Input)
class InputAdmin(PolymorphicInlineSupportMixin, admin.ModelAdmin):
    inlines = [InputChoiceInline]
    ordering = ['-order']
    change_form_template = 'app/input_view.html'

    def has_module_permission(self, request):
        # hide this model from admin index
        return False

    def get_osm_info(self):
        ip_page = models.InputPage.objects.all().values_list('id','name')
        return ip_page

    def changeform_view(self, request, object_id, form_url='', extra_context=None):
        extra_cont = {}
        extra_cont['ip_pages'] = self.get_osm_info()
        return super(InputAdmin,self).changeform_view(
            request, object_id, form_url, extra_context=extra_cont,
        )

