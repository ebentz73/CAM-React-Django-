"""Seed the database.

Example:
    >>> python manage.py seed --mode=refresh
"""
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.management.base import BaseCommand
from django.utils import timezone

from app.models import AnalyticsSolution, Scenario, ExecutiveView, InputPage, InputDataSet, Input, InputChoice

"""Clear all data and creates addresses"""
MODE_REFRESH = 'refresh'

"""Clear all data and do not create any object"""
MODE_CLEAR = 'clear'


class Command(BaseCommand):
    help = 'seed database for testing and development.'

    def add_arguments(self, parser):
        parser.add_argument('--mode', type=str, help='Mode')

    def handle(self, *args, **options):
        self.stdout.write('seeding data...')
        run_seed(options['mode'])
        self.stdout.write('done.')


def clear_data():
    """Deletes all the table data."""
    print('Delete Analytics Solution instances')
    AnalyticsSolution.objects.all().delete()


def create_analytics_solution():
    """Creates an analytics solution object combining different elements from
    the list."""
    print('Creating Analytics Solution')
    with open('app/management/commands/tam_model.tam', 'rb') as f:
        solution = AnalyticsSolution.objects.create(
            name='Penguin Evaluation',
            upload_date=timezone.now(),
            tam_file=SimpleUploadedFile('test_model.tam', f.read())
        )

    print('Creating Scenarios')
    low_scenario = Scenario.objects.create(
        solution=solution,
        name='low'
    )
    mid_scenario = Scenario.objects.create(
        solution=solution,
        name='mid'
    )
    high_scenario = Scenario.objects.create(
        solution=solution,
        name='high'
    )

    print('Creating Input Pages')
    model = solution.models.first()
    input_page = InputPage.objects.create(
        model=model,
        name='Penguin Page'
    )

    print('Creating Input Data Sets')
    with open('app/management/commands/low.xlsx', 'rb') as f:
        low_ids = InputDataSet.objects.create(
            input_page=input_page,
            name='Penguin be low',
            file=SimpleUploadedFile('low.xlsx', f.read())
        )
    low_ids.scenarios.add(low_scenario)
    with open('app/management/commands/mid.xlsx', 'rb') as f:
        mid_ids = InputDataSet.objects.create(
            input_page=input_page,
            name='Penguin be mid',
            file=SimpleUploadedFile('mid.xlsx', f.read())
        )
    mid_ids.scenarios.add(mid_scenario)
    with open('app/management/commands/high.xlsx', 'rb') as f:
        high_ids = InputDataSet.objects.create(
            input_page=input_page,
            name='Penguin be high',
            file=SimpleUploadedFile('high.xlsx', f.read())
        )
    high_ids.scenarios.add(high_scenario)
    with open('app/management/commands/highv2.xlsx', 'rb') as f:
        highv2_ids = InputDataSet.objects.create(
            input_page=input_page,
            name='Penguin be very high',
            file=SimpleUploadedFile('highv2.xlsx', f.read())
        )

    print('Creating Executive View')
    exec_view = ExecutiveView.objects.create(
        solution=solution,
        name='Penguin God looks here'
    )

    print('Creating Inputs')
    input_ = Input.objects.create(
        exec_view=exec_view,
        name='Penguin gotta input low'
    )

    print('Creating Input Choices')
    InputChoice.objects.create(
        input=input_,
        ids=low_ids,
        label='Penguin put low'
    )
    InputChoice.objects.create(
        input=input_,
        ids=mid_ids,
        label='Penguin put mid'
    )
    InputChoice.objects.create(
        input=input_,
        ids=high_ids,
        label='Penguin put high'
    )
    InputChoice.objects.create(
        input=input_,
        ids=highv2_ids,
        label='Penguin put very high'
    )


def run_seed(mode):
    """Seed database based on mode.

    Args:
        mode: refresh/clear
    """
    # Clear data from tables
    clear_data()
    if mode == MODE_CLEAR:
        return

    create_analytics_solution()
