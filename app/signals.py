import os
import tempfile

from django.db.models.signals import m2m_changed, post_save, post_init
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import Permission
from django.dispatch import receiver
from collections import OrderedDict

from app.models import (
    AnalyticsSolution,
    ConstNodeData,
    FilterCategory,
    FilterOption,
    InputDataSet,
    InputNodeData,
    InputPage,
    Model,
    Node,
    Scenario,
    NodeData,
)
from app.proto_modules import (
    ConstNodeData_pb2,
    InputNodeData_pb2,
    NodeTagListBlob_pb2,
    TagFilterOption_pb2,
)
from app.utils import Sqlite

from profile.models import Role
from guardian.shortcuts import assign_perm, get_objects_for_group, get_group_perms


def assign_model_and_object_perms(instance, role, codename):
    cls = instance.__class__
    content_type = ContentType.objects.get_for_model(cls)
    permission = Permission.objects.get(
        codename=codename,
        content_type=content_type,
    )
    role.permissions.add(permission)
    assign_perm(codename, role, instance)


def create_solution_role(solution):
    roles = Role.objects.filter(name='role_' + solution.name)
    if roles.count() < 1:
        role = Role.objects.create(name='role_' + solution.name)
        content_type = ContentType.objects.get_for_model(AnalyticsSolution)
        permission = Permission.objects.get(
            codename='view_analyticssolution',
            content_type=content_type,
        )
        role.permissions.add(permission)
        assign_perm('view_analyticssolution', role, solution)
    else:
        role = roles[0]
    return role


@receiver(post_save, sender=AnalyticsSolution)
def update_model(sender, **kwargs):
    solution = kwargs.get('instance')

    if 'tam_file' in solution.changed_fields:
        role = create_solution_role(solution)
        # Download tam model file and save only what we need
        f, filename = tempfile.mkstemp()
        try:
            os.write(f, solution.tam_file.read())
            os.close(f)

            # Open sqlite file
            with Sqlite(filename) as cursor:
                # Save all filters
                cursor.execute(
                    "SELECT CategoryName, FilterOptionsBlob FROM FilterCategories"
                )
                for category_name, filter_blob in cursor.fetchall():
                    category, _ = FilterCategory.objects.update_or_create(
                        solution=solution, name=category_name
                    )
                    assign_model_and_object_perms(category, role, 'view_filtercategory')

                    blob_model = TagFilterOption_pb2.List_TagFilterOption()
                    blob_model.ParseFromString(filter_blob)
                    for option in blob_model.items:
                        filter_option, _ = FilterOption.objects.update_or_create(
                            category=category,
                            tag=option.Tag,
                            display_name=option.DisplayName,
                        )
                        assign_model_and_object_perms(filter_option, role, 'view_filteroption')

                # Save all models
                cursor.execute("SELECT ModelId, ModelName FROM TruNavModel")
                for model_id, model_name in cursor.fetchall():
                    model, _ = Model.objects.update_or_create(
                        solution=solution,
                        tam_id=model_id,
                        defaults={'name': model_name},
                    )
                    assign_model_and_object_perms(model, role, 'view_model')

                    # Save all input pages
                    cursor.execute(
                        "SELECT PageId, PageName "
                        "FROM ModelDataPage "
                        "WHERE ModelId=? AND pagetype=0",
                        (model_id,),
                    )
                    for page_id, page_name in cursor.fetchall():
                        page, _ = InputPage.objects.update_or_create(
                            model=model, tam_id=page_id, defaults={'name': page_name}
                        )
                        assign_model_and_object_perms(page, role, 'view_inputpage')

                    # Save all nodes
                    tag_roles = {}
                    cursor.execute(
                        "SELECT n.NodeId, NodeName, NodeNotes, NodeType, TagList, NodeInputData "
                        "FROM Node AS n, NodeScenarioData AS d "
                        "WHERE n.NodeId = d.NodeId "
                        "   AND n.ModelId=? "
                        "   AND NodeType IN ('inputnode', 'constnode')",
                        (model_id,),
                    )
                    for (
                        node_id,
                        node_name,
                        node_notes,
                        node_type,
                        tag_list_blob,
                        node_data_blob,
                    ) in cursor.fetchall():
                        # Get tags
                        blob_model = NodeTagListBlob_pb2.List_String()
                        blob_model.ParseFromString(tag_list_blob)
                        tag_list = list(blob_model.items)

                        # Check if node has CAM tags
                        has_tags = any(True for tag in tag_list if tag.startswith('CAM_'))

                        # Only save nodes if they are used by CAM
                        if has_tags:
                            cam_roles = [tag for tag in tag_list if tag.startswith('CAM_ROLE==')]

                            # Create Node model
                            node, _ = Node.objects.update_or_create(
                                model=model,
                                tags=tag_list,
                                tam_id=node_id,
                                defaults={'name': node_name},
                                notes=node_notes,
                            )

                            # Apply CAM role to Node
                            for cam_role in cam_roles:
                                if cam_role in tag_roles:
                                    node_role = tag_roles[cam_role]
                                else:
                                    node_role = Role.objects.create(name='role_' + solution.name + '_' + cam_role)
                                    permission = Permission.objects.get(
                                        codename='view_node',
                                        content_type=ContentType.objects.get_for_model(Node),
                                    )
                                    node_role.permissions.add(permission)
                                    tag_roles[cam_role] = node_role
                                assign_perm('view_node', node_role, node)

                            # Create InputNodeData model
                            if node_type == 'inputnode':
                                blob_model = InputNodeData_pb2.InputNodeData()
                                blob_model.ParseFromString(node_data_blob)
                                node_data = [
                                    [
                                        val.InputData.LowerBound,
                                        val.InputData.Low,
                                        val.InputData.Nominal,
                                        val.InputData.High,
                                        val.InputData.UpperBound,
                                    ]
                                    for val in blob_model.LayerData
                                ]
                                ind, _ = InputNodeData.objects.update_or_create(
                                    node=node, default_data=node_data, is_model=True
                                )
                                assign_model_and_object_perms(ind, node_role, 'view_inputnodedata')

                            # Create ConstNodeData model
                            elif node_type == 'constnode':
                                blob_model = ConstNodeData_pb2.ConstNodeData()
                                blob_model.ParseFromString(node_data_blob)
                                node_data = [
                                    val.ConstData
                                    for val in blob_model.AllLayerData
                                ]
                                cnd, _ = ConstNodeData.objects.update_or_create(
                                    node=node, default_data=node_data, is_model=True
                                )
                                assign_model_and_object_perms(cnd, node_role, 'view_constnodedata')

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
            for input_page_id in scenario.input_data_sets.values_list(
                'input_page_id', flat=True
            ):
                if ids.input_page.id == input_page_id:
                    raise Exception(
                        f"Scenario '{scenario.name}' cannot have multiple input data sets associated with Input Page '{ids.input_page.name}'."
                    )
