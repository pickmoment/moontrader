from cement import Controller, ex
import subprocess
from datetime import datetime, timedelta

class Scenario(Controller):
    class Meta:
        label = 'scenario'
        stacked_type = 'embedded'
        stacked_on = 'base'

    @ex(help='execute scenario',
        arguments=[(['command_file'], {}),
            (['--next'], {'help': 'next file', 'action': 'store_true', 'dest': 'exec_next'})]
    )
    def scenario(self):
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

        commands = open(command_file, 'r').readlines()
        while commands:
            next_commands = []
            for command in commands:
                command = command.strip().format(**param_dict)
                self.app.log.info('[EXECUTE] {}'.format(command))
                result = subprocess.check_output(command, shell=True)
                if exec_next:
                    next_command = result.decode("utf-8").strip()
                    if next_command:
                        next_commands.append(next_command)

            commands = None

            if next_commands:
                commands = next_commands