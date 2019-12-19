from threading import Thread

from ansible_runner.interface import run_async


def run_playbook(playbook, extra_vars=None, tags=None):
    runner_thread, r = run_async(private_data_dir='playbook', playbook=playbook, extravars=extra_vars, tags=tags)
    log_thread = Thread(target=log_playbook, args=(r,))
    log_thread.start()


def log_playbook(r):
    print(f'{r.status}: {r.rc}')
    for each_host_event in r.events:
        print(each_host_event['event'])
    print('Final status:')
    print(r.stats)
