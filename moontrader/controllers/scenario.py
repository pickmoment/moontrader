from cement import Controller, ex
import subprocess
from datetime import datetime, timedelta
import time
from multiprocessing import Pool
import logging
from functools import partial

log = logging.getLogger()

class Scenario(Controller):
    class Meta:
        label = 'scenario'
        stacked_type = 'embedded'
        stacked_on = 'base'

    @ex(help='execute scenario',
        arguments=[(['command_file'], {}),
            (['--workers'], {'help': 'workers size', 'action': 'store', 'dest': 'workers'}),
            (['--next'], {'help': 'next file', 'action': 'store_true', 'dest': 'exec_next'})]
    )
    def scenario(self):
        global log
        log = self.app.log
        today = datetime.now()
        yesterday = datetime.now() - timedelta(days=1)
        week = datetime.now() - timedelta(weeks=1)
        month = datetime.now() - timedelta(days=30)
        param_dict = {
            'today': today.strftime('%Y%m%d'),
            'yesterday': yesterday.strftime('%Y%m%d'),
            'week': week.strftime('%Y%m%d'),
            'month': month.strftime('%Y%m%d')
        }

        command_file = self.app.pargs.command_file
        exec_next = self.app.pargs.exec_next
        workers = int(self.app.pargs.workers) if self.app.pargs.workers else 1

        commands = open(command_file, 'r').readlines()

        if workers > 1:
            with Pool(workers) as pool:
                pool.map(partial(execute, param_dict=param_dict, exec_next=exec_next), commands)
        else:
            for command in commands:
                execute(command, param_dict, exec_next)



def execute(command, param_dict, exec_next):
    while command:
        next_command = None
        command = command.strip().format(**param_dict)
        log.info('[EXECUTE] {}'.format(command))
        result = ''
        while True:
            try:
                result = subprocess.check_output(command, shell=True)
                break
            except KeyboardInterrupt as ki:
                break
            except Exception as ex:
                log.error('Error: {}'.format(ex))
                time.sleep(1)
        if exec_next:
            next_command = result.decode("utf-8").strip()

        command = None

        if next_command:
            command = next_command
        