import os
import tempfile

from django.contrib.auth.models import Group, User
from django.db.models.signals import m2m_changed, post_save
from django.dispatch import receiver
from guardian.shortcuts import assign_perm
from profile.models import Role

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
)
from app.proto_modules import (
    ConstNodeData_pb2,
    InputNodeData_pb2,
    NodeTagListBlob_pb2,
    TagFilterOption_pb2,
)
from app.utils import Sqlite, remove_model_perm, PowerBI

CAM_ROLE_PREFIX = 'CAM_ROLE=='


@receiver(post_save, sender=AnalyticsSolution)
def post_save_solution(sender, instance, **kwargs):
    if 'tam_file' in instance.changed_fields:
        update_tam_model(instance)


def update_tam_model(solution):
        tag_roles = {}
        group = get_or_create_solution_group(solution)

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
                    category, created = FilterCategory.objects.update_or_create(
                        solution=solution, name=category_name
                    )
                    if created:
                        assign_perm('app.view_filtercategory', group, category)

                    blob_model = TagFilterOption_pb2.List_TagFilterOption()
                    blob_model.ParseFromString(filter_blob)
                    for option in blob_model.items:
                        filter_option, created = FilterOption.objects.update_or_create(
                            category=category,
                            tag=option.Tag,
                            display_name=option.DisplayName,
                        )
                        if created:
                            assign_perm('app.view_filteroption', group, filter_option)

                # Save all models
                cursor.execute("SELECT ModelId, ModelName FROM TruNavModel")
                for model_id, model_name in cursor.fetchall():
                    model, created = Model.objects.update_or_create(
                        solution=solution,
                        tam_id=model_id,
                        defaults={'name': model_name},
                    )
                    if created:
                        assign_perm('app.view_model', group, model)

                    # Save all input pages
                    cursor.execute(
                        "SELECT PageId, PageName "
                        "FROM ModelDataPage "
                        "WHERE ModelId=? AND pagetype=0",
                        (model_id,),
                    )
                    for page_id, page_name in cursor.fetchall():
                        page, created = InputPage.objects.update_or_create(
                            model=model, tam_id=page_id, defaults={'name': page_name}
                        )
                        if created:
                            assign_perm('app.view_inputpage', group, page)

                    # Save all nodes
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


                            node_data = node_data_codename = None
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
                                node_data, _ = InputNodeData.objects.update_or_create(
                                    node=node, default_data=node_data, is_model=True
                                )
                                assign_model_and_object_perms(ind, role, 'view_inputnodedata')
                                node_data_codename = 'app.view_inputnodedata'

                            # Create ConstNodeData model
                            elif node_type == 'constnode':
                                blob_model = ConstNodeData_pb2.ConstNodeData()
                                blob_model.ParseFromString(node_data_blob)
                                node_data = [
                                    val.ConstData for val in blob_model.AllLayerData
                                ]
                                node_data, _ = ConstNodeData.objects.update_or_create(
                                    node=node, default_data=node_data, is_model=True
                                )
                                assign_model_and_object_perms(cnd, role, 'view_constnodedata')
                                node_data_codename = 'app.view_constnodedata'

                            # Apply CAM role to Node
                            # only create roles for nodes we are saving
                            if node_data and node_data_codename:
                                cam_roles = (
                                    tag[len(CAM_ROLE_PREFIX):]
                                    for tag in tag_list
                                    if tag.startswith(CAM_ROLE_PREFIX)
                                )
                                for cam_role in cam_roles:
                                    node_role = tag_roles.get(cam_role)
                                    if node_role is None:
                                        # Create role since it does not exist
                                        role_name = f'{solution.name} - {cam_role}'
                                        node_role = Role.objects.create(name=role_name)
                                        tag_roles[cam_role] = node_role
                                    assign_perm('app.view_node', node_role, node)
                                    assign_perm(node_data_codename, node_role, node_data)

        finally:
            os.remove(filename)


def get_or_create_solution_group(solution):
    groups = Group.objects.filter(name=solution.name)
    group = groups.first()
    if group is None:
        group = Group.objects.create(name=solution.name)
        assign_perm('app.view_analyticssolution', group, solution)
    return group


@receiver(post_save, sender=Scenario)
def post_save_scenario(sender, instance, **kwargs):
    if 'status' in instance.changed_fields and instance.status == 'Completed.':
        PowerBI(instance.solution).refresh_dataset()


@receiver(m2m_changed, sender=InputDataSet.scenarios.through)
def input_data_set_scenario_changed(sender, action, instance, pk_set, **kwargs):
    if action == 'pre_add':
        scenarios = Scenario.objects.filter(pk__in=pk_set)
        for scenario in scenarios:
            for input_page_id in scenario.input_data_sets.values_list(
                'input_page_id', flat=True
            ):
                if instance.input_page.id == input_page_id:
                    raise Exception(
                        f"Scenario '{scenario.name}' cannot have multiple input data sets "
                        f"associated with Input Page '{instance.input_page.name}'."
                    )


@receiver(m2m_changed, sender=Scenario.shared.through)
def shared_scenario_changed(sender, action, instance, pk_set, **kwargs):
    def post_add():
            assign_perm('app.view_scenario', user, instance)
            assign_perm('app.change_scenario', user, instance)

    def post_remove():
            remove_model_perm(user, instance)

    do_action = locals().get(action)
    if action is None:
        return

    users = User.objects.filter(pk__in=pk_set)
    for user in users:
        do_action()

    PowerBI(instance).refresh_dataset()
