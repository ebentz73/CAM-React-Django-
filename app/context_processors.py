import environ


def export_vars(request):
    # Access variables in django templates
    env = environ.Env()

    return {
        'GRAFANA_HOST': env('GRAFANA_HOST'),
    }
