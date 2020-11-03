import os
import tempfile

from django.db.models.signals import m2m_changed, post_save
from django.dispatch import receiver

from app.models import (AnalyticsSolution, FilterCategory,
                        FilterOption, InputDataSet, InputPage,
                        Model, Scenario, Node, InputNodeData, ConstNodeData)
from app.proto_modules import TagFilterOption_pb2, InputNodeData_pb2, NodeTagListBlob_pb2, ConstNodeData_pb2
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
                cursor.execute("select * from FilterCategories")
                for record in cursor.fetchall():
                    #
                    blob_model = TagFilterOption_pb2.List_TagFilterOption()
                    blob_model.ParseFromString(record[2])
                    category_name = record[1]
                    category, _ = FilterCategory.objects.update_or_create(solution=solution, name=category_name)
                    for option in blob_model.items._values:
                        option, _ = FilterOption.objects.update_or_create(category=category, tag=option.Tag,
                                                                          display_name=option.DisplayName)
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
                        blob_model = NodeTagListBlob_pb2.List_String()
                        blob_model.ParseFromString(node_record[15])
                        tag_list = blob_model.items._values
                        is_right_type = node_type in ('inputnode', 'constnode', 'inputiteratornode', 'percentAllocationNode')

                        # Check if node has CAM tags
                        has_cam_tags = False
                        for tag in tag_list:
                            has_cam_tags = has_cam_tags or tag.startswith('CAM_INPUT_CATEGORY==')
                            if has_cam_tags:
                                break
                        if is_right_type and has_cam_tags:
                            # Create Node model
                            node, _ = Node.objects.update_or_create(model=model, tags=tag_list,
                                                                    tam_id=node_id, defaults={'name': node_name})
                            # Create InputNodeData model
                            if node_type == 'inputnode':
                                cursor.execute("select NodeInputData from NodeScenarioData"
                                               " where NodeId=?", (node_id,))
                                blob_model = InputNodeData_pb2.InputNodeData()
                                record = cursor.fetchone()
                                blob_model.ParseFromString(record[0])
                                node_data = [[val.InputData.LowerBound, val.InputData.Low, val.InputData.Nominal,
                                              val.InputData.High, val.InputData.UpperBound]
                                             for val in blob_model.LayerData._values]
                                InputNodeData.objects.update_or_create(node=node, default_data=node_data, is_model=True)

                            # Create ConstNodeData model
                            if node_type == 'constnode':
                                cursor.execute("select NodeInputData from NodeScenarioData where NodeId=?", (node_id,))
                                record = cursor.fetchone()
                                blob_model = ConstNodeData_pb2.ConstNodeData()
                                blob_model.ParseFromString(record[0])
                                node_data = [val.ConstData for val in blob_model.AllLayerData._values]
                                ConstNodeData.objects.update_or_create(node=node, default_data=node_data, is_model=True)

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
