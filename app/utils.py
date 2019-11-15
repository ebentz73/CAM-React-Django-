from ansible_runner.interface import init_runner


def run_playbook(playbook, tags=None):
    r = init_runner(private_data_dir='playbook', playbook=playbook, tags=tags)
    r.run()
    print(f'{r.status}: {r.rc}')
    for each_host_event in r.events:
        print(each_host_event['event'])
    print('Final status:')
    print(r.stats)
