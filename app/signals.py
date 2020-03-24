import tempfile

from django.db.models.signals import post_save, m2m_changed
from django.dispatch import receiver

from app.models import InputDataSet, AnalyticsSolution, InputPage, Model, Scenario
from app.utils import Sqlite


@receiver(post_save, sender=AnalyticsSolution)
def update_model(sender, **kwargs):
    solution = kwargs.get('instance')

    # Download file from GCS
    with tempfile.NamedTemporaryFile() as f:
        f.write(solution.tam_file.read())

        # Open sqlite file
        with Sqlite(f.name) as cursor:
            cursor.execute('SELECT * from TruNavModel')
            for model_record in cursor.fetchall():
                model = Model.objects.create(name=model_record[2], solution=solution)
                cursor.execute('SELECT * from ModelDataPage where ModelId=? and pagetype=0', (model_record[1],))
                for data_page_record in cursor.fetchall():
                    InputPage.objects.create(name=data_page_record[3], model=Model.objects.get(id=model.id))


@receiver(m2m_changed, sender=InputDataSet.scenarios.through)
def input_data_set_scenario_changed(sender, **kwargs):
    action = kwargs.get('action')
    pk_set = kwargs.get('pk_set')
    ids = kwargs.get('instance')

    if action == 'pre_add':
        for scenario_id in pk_set:
            scenario = Scenario.objects.get(pk=scenario_id)
            for input_page_id in scenario.input_data_sets.values_list('input_page_id', flat=True):
                if ids.input_page.id == input_page_id:
                    raise Exception(
                        f"Scenario '{scenario.name}' cannot have multiple input data sets associated with Input Page '{ids.input_page.name}'.")
