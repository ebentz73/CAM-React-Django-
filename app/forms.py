from django import forms
from django.utils import timezone
from material import Layout, Fieldset, Row

from app.models import Scenario, EvalJob, InputDataSet, Input, IntegerNodeOverride
from app.utils import run_eval_engine


class CreateEvalJobForm(forms.Form):
    evaljob_name = forms.CharField()
    scenario_name = forms.CharField()
    time_increment = forms.ChoiceField(choices=EvalJob.TIME_OPTIONS)
    time_start = forms.DateField(initial=timezone.localdate())

    def __init__(self, *args, **kwargs):
        self.instance = kwargs.pop('instance')
        super().__init__(*args, **kwargs)

        scenarios = self.instance.solution.scenarios
        self.fields['scenario'] = forms.ModelChoiceField(queryset=scenarios,
                                                         label='Scenario To Modify',
                                                         initial=scenarios.first().pk)

        widget_ids = []
        for ids_input in self.instance.ids_inputs:
            widget_id = f'input_ids_{ids_input.id}'
            choices = [(choice.ids_id, choice.ids.name) for choice in ids_input.input_choices]
            self.fields[widget_id] = forms.ChoiceField(choices=choices, label=ids_input.name)
            widget_ids.append(widget_id)

        for numeric_input in self.instance.numeric_inputs:
            widget_id = f'input_numeric_{numeric_input.id}'
            self.fields[widget_id] = forms.FloatField(label=numeric_input.name)
            widget_ids.append(widget_id)

        for slider_input in self.instance.slider_inputs:
            widget_id = f'input_slider_{slider_input.id}'
            self.fields[widget_id] = forms.FloatField(
                widget=forms.NumberInput(attrs={
                    'type': 'range',
                    'step': slider_input.step,
                    'min': slider_input.minimum,
                    'max': slider_input.maximum,
                }),
                label=slider_input.name,
            )
            widget_ids.append(widget_id)

        self.layout = Layout(
            'evaljob_name',
            Row('scenario_name', 'scenario'),
            Row('time_start', 'time_increment'),
            Fieldset(
                "Inputs",
                *widget_ids,
            )
        )

    def clean(self):
        # Get all input values from inputs
        ids_choices, node_choices = set(), {}
        for key, value in self.cleaned_data.items():
            if key.startswith('input_'):
                _, input_type, input_id = key.split('_')

                if input_type == 'ids':
                    if value in ids_choices:
                        self.add_error(key, 'Duplicate input data set.')
                    else:
                        ids_choices.add(value)

                elif input_type in ('numeric', 'slider'):
                    node_choices[input_id] = value

        self.cleaned_data.update(ids_choices=ids_choices, node_choices=node_choices)

    def save(self, **kwargs):
        # Get form data
        evaljob_name = self.cleaned_data.get('evaljob_name')
        selected_scenario = self.cleaned_data.get('scenario')
        scenario_name = self.cleaned_data.get('scenario_name')
        time_start = self.cleaned_data.get('time_start')
        time_increment = self.cleaned_data.get('time_increment')
        ids_choices = self.cleaned_data.get('ids_choices')
        node_choices = self.cleaned_data.get('node_choices')

        # Create ad hoc scenario
        scenario = Scenario.objects.create(
            solution=self.instance.solution,
            name=scenario_name,
            is_adhoc=True,
        )

        # Add input data sets to ad hoc scenario from selected scenario and
        # check that an input page only has one IDS associated with it
        seen_input_pages, scenario_input_pages = set(), set()
        for ids_id in ids_choices:
            ids = InputDataSet.objects.get(pk=ids_id)
            if ids.input_page.id not in seen_input_pages:
                ids.scenarios.add(scenario)
                seen_input_pages.add(ids.input_page.id)
            else:
                self.add_error('Multiple input data sets were given for a single input page.', None)

        for ids in selected_scenario.input_data_sets:
            scenario_input_pages.add(ids.input_page.id)
            if ids.input_page.id not in seen_input_pages:
                ids.scenarios.add(scenario)
                seen_input_pages.add(ids.input_page.id)

        # Add node overrides to ad hoc scenario
        for input_id, value in node_choices.items():
            input_ = Input.objects.get(pk=input_id)
            IntegerNodeOverride.objects.create(node=input_.node, scenario=scenario, value=value)

        if seen_input_pages == scenario_input_pages:
            # Create Eval Job
            evaljob = EvalJob.objects.create(
                solution=self.instance.solution,
                date_created=timezone.now(),
                status='Running...',
                name=evaljob_name,
                layer_time_start=time_start,
                layer_time_increment=time_increment,
                adhoc_scenario=scenario,
            )

            run_eval_engine(evaljob.id)
        else:
            self.add_error('The selected scenario and the ad hoc scenario do not have matching input pages.', None)
