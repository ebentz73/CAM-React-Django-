import os
import tempfile

from django.db.models.signals import post_save, m2m_changed
from django.dispatch import receiver

from app.models import InputDataSet, AnalyticsSolution, InputPage, Model, Scenario, Node
from app.utils import Sqlite


@receiver(post_save, sender=AnalyticsSolution)
def update_model(sender, **kwargs):
    solution = kwargs.get('instance')

    if 'tam_file' in solution.changed_fields:
        # Download tam model file from GCS and save what we need out of it
        f, filename = tempfile.mkstemp()
        try:
            os.write(f, solution.tam_file.read())
            os.close(f)

            # Open sqlite file
            with Sqlite(filename) as cursor:
                cursor.execute('select * from TruNavModel')
                for model_record in cursor.fetchall():
                    model_id = model_record[1]
                    model_name = model_record[2]
                    model, _ = Model.objects.update_or_create(solution=solution, tam_id=model_id,
                                                              defaults={'name': model_name})

                    # Save all input pages
                    cursor.execute('select * from ModelDataPage where ModelId=? and pagetype=0', (model_id,))
                    for data_page_record in cursor.fetchall():
                        input_page_id = data_page_record[2]
                        input_page_name = data_page_record[3]
                        InputPage.objects.update_or_create(model=model, tam_id=input_page_id,
                                                           defaults={'name': input_page_name})

                    # Save all nodes
                    cursor.execute('select * from Node where ModelId=?', (model_id,))
                    for node_record in cursor.fetchall():
                        node_id = node_record[2]
                        node_name = node_record[3]
                        node_type = node_record[5]
                        if node_type in ('inputnode', 'constnode', 'inputiteratornode', 'percentAllocationNode'):
                            Node.objects.update_or_create(model=model, tam_id=node_id, defaults={'name': node_name})
        finally:
            os.remove(filename)


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
