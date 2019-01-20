
import logging
from cement import App, TestApp, init_defaults
from cement.core.exc import CaughtSignal
from .core.exc import MoonTraderAppError

from .controllers.base import Base
from .controllers.world_futures import WorldFutures
from .controllers.scenario import Scenario

from .core.yuanta import Session
from .core.xasession import Session as ebestSession, setLogger as ebestSetLogger

# configuration defaults
CONFIG = init_defaults('moontrader')

def extend_yuanta(app):
    app.log.info('Extending Yuanta API')
    config = app.config.get('moontrader', 'yuanta')
    yuanta = Session()
    yuanta.connect(config['url'], config['path'])
    result = yuanta.login(config['id'], config['pw'], config['cert'])
    if result[0] == 2:
        app.log.info('Success login')
    else:
        app.log.info('Fail login -> %s:%s' % result)

    app.extend('yuanta', yuanta)

class MoonTraderApp(App):
    """Moon Trader primary application."""

    class Meta:
        label = 'moontrader'

        # hooks = [
        #     ('post_setup', extend_ebest)
        # ]

        config_dirs = [
            'c:/Users/Lenovo/',
            './'
        ]

        # configuration defaults
        config_defaults = CONFIG

        # call sys.exit() on close
        close_on_exit = True

        # load additional framework extensions
        extensions = [
            'yaml',
            'colorlog',
            'jinja2',
        ]

        # configuration handler
        config_handler = 'yaml'

        # configuration file suffix
        config_file_suffix = '.yml'

        # set the log handler
        log_handler = 'colorlog'

        # set the output handler
        output_handler = 'jinja2'

        # register handlers
        handlers = [
            Base,
            WorldFutures,
            Scenario
        ]


class MoonTraderAppTest(TestApp,MoonTraderApp):
    """A sub-class of MoonTraderApp that is better suited for testing."""

    class Meta:
        label = 'moontrader'


def main():
    with MoonTraderApp() as app:
        try:
            app.run()

        except AssertionError as e:
            print('AssertionError > %s' % e.args[0])
            app.exit_code = 1

            if app.debug is True:
                import traceback
                traceback.print_exc()

        except MoonTraderAppError as e:
            print('MoonTraderAppError > %s' % e.args[0])
            app.exit_code = 1

            if app.debug is True:
                import traceback
                traceback.print_exc()

        except CaughtSignal as e:
            # Default Cement signals are SIGINT and SIGTERM, exit 0 (non-error)
            print('\n%s' % e)
            app.exit_code = 0


if __name__ == '__main__':
    main()
