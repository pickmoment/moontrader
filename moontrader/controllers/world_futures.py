from cement import Controller, ex
from ..core.db import db_adapter
from ..core.xasession import Session as ebestSession, setLogger as ebestSetLogger
import time
from tqdm import tqdm
from pony.orm import Database

month_map = {'F': 1, 'G': 2, 'H': 3, 'J': 4, 'K': 5, 'M': 6, 
             'N': 7, 'Q': 8, 'U': 9, 'V': 10, 'X': 11, 'Z': 12}

codes_currency = {'AD': 'Australian Dollar', 'BP': 'British Pound', 'BR': 'Brazilian Real'}

class WorldFutures(Controller):
    ebest = None

    class Meta:
        label = 'futures'
        stacked_type = 'embedded'
        stacked_on = 'base'

        arguments = [
            (['-s', '--save'], {'help': 'save to file',
                'action': 'store_true', 'dest': 'save'})
        ]


    @ex(help='get code list')
    def codes(self):
        self.connect_ebest()
        response = self.ebest.codes()
        rows = response.content
        self.app.log.info(rows)

        if self.app.pargs.save:
            data_conf = self.app.config.get('moontrader', 'data')
            db_ebest = Database()
            db_adapter.define_ebest(db_ebest)
            db_adapter.bind(db_ebest, data_conf['dir'], 'ebest')
            db_adapter.drop_codes()
            db_adapter.init(db_ebest)
            db_adapter.insert_codes(rows)


    @ex(help='get candle list',
        arguments=[(['code'],{}), (['period_type'],{'help': 'm(minute), d(day)'}), 
            (['--period', '-p'], {'help': 'period for minute', 'action': 'store', 'dest': 'period'}),
            (['--date', '--start'], {'help': 'start date', 'action': 'store', 'dest': 'cts_date'}),
            (['--time'], {'help': 'start time', 'action': 'store', 'dest': 'cts_time'}),
            (['--last', '--end'], {'help': 'last date', 'action': 'store', 'dest': 'last_date'}),
            (['--loop'], {'help': 'loop count', 'action': 'store', 'dest': 'loop_count'})]
    )
    def candle(self):
        code = self.app.pargs.code
        period_type = self.app.pargs.period_type
        period = self.app.pargs.period
        cts_date = self.app.pargs.cts_date
        cts_time = self.app.pargs.cts_time
        last_date = self.app.pargs.last_date
        loop_count = self.app.pargs.loop_count
        loop_count = int(loop_count if loop_count else 200)

        self.connect_ebest()

        if period_type == 'm':
            self.candle_minute(code, period, cts_date, cts_time, last_date, loop_count)
        elif period_type == 'd':
            self.candle_day(code, cts_date, last_date)


    @ex(help='get multi code candle list',
        arguments=[(['codes'],{}), (['minute'],{}), 
            (['--date', '--start'], {'help': 'start date', 'action': 'store', 'dest': 'cts_date'}),
            (['--time'], {'help': 'start time', 'action': 'store', 'dest': 'cts_time'}),
            (['--last', '--end'], {'help': 'last date', 'action': 'store', 'dest': 'last_date'}),
            (['--loop'], {'help': 'loop count', 'action': 'store', 'dest': 'loop_count'})]
    )
    def codes_candle(self):
        codes = self.app.pargs.codes.strip().split(',')
        period = self.app.pargs.minute
        cts_date = self.app.pargs.cts_date
        cts_time = self.app.pargs.cts_time
        last_date = self.app.pargs.last_date
        loop_count = self.app.pargs.loop_count
        loop_count = int(loop_count if loop_count else 200)

        self.connect_ebest()
    
        for code in codes:
            self.candle_minute(code, period, cts_date, cts_time, last_date, loop_count)
            time.sleep(1)


    def candle_day(self, code, start_day, end_day):
        self.app.log.debug('[candle_day] code:{}, start_day:{}, end_day:{}'.format(code, start_day, end_day))

        for i in tqdm(range(1)):
            response = self.ebest.candle_day(code, start_day, end_day)

        self.treat_candle_save(True, response, code, 'd', '')


    def candle_minute(self, code, minute, cts_date, cts_time, last_date, loop_count):
        self.app.log.info('[candle_minute] code:{}, minute:{}, cts_date:{}, cts_time:{}, last_date:{}, loop_count:{}'.format(code, minute, cts_date, cts_time, last_date, loop_count))
        period_type = 'm'
        
        response = self.candle_minute_call(code, minute, cts_date, cts_time, last_date, loop_count)

        if response and response.content and response.has_cts:
            save_option = '-s' if self.app.pargs.save else ''
            last_option = ' --last {}'.format(last_date) if last_date else ''
            next_command = 'moontrader {} candle {} {} -p {} --date {} --time {}{}'.format(save_option, code, period_type, minute, response._cts_map['cts_date'], response._cts_map['cts_time'], last_option)
            print(next_command)


    def candle_minute_call(self, code, minute, cts_date, cts_time, last_date, loop_count):
        for i in tqdm(range(loop_count)):
            if i == 0:
                response = self.ebest.candle_minute(code, minute, cts_date, cts_time)
                response = self.treat_candle_response(True, response, code, 'm', minute, last_date)
            else:
                if response and response.content and response.has_cts:
                    response = response.request_next()
                    response = self.treat_candle_response(False, response, code, 'm', minute, last_date)
                else:
                    break

        return response


    def treat_candle_save(self, is_first, response, code, period_type, period):
        rows = response.content
        if not rows:
            return
        self.app.log.debug('{} ({})'.format(rows[-1], len(rows)))

        if self.app.pargs.save:
            self.save_candle_data(rows, code, period_type, period, is_first)
        else:
            self.app.log.info('{} ({})'.format(rows, len(rows)))
        
        return rows


    def treat_candle_response(self, is_first, response, code, period_type, period, last_date):
        rows = self.treat_candle_save(is_first, response, code, period_type, period)
        
        if last_date:
            if rows[-1]['date'] < last_date:
                return

        return response


    def save_candle_data(self, rows, code, period_type, period, need_init=False):
        if need_init:
            data_conf = self.app.config.get('moontrader', 'data')
            db_candle = Database()
            db_adapter.define_candle(db_candle)
            db_adapter.bind(db_candle, data_conf['dir'], '{}_{}{}'.format(code, period_type, period))
            db_adapter.init(db_candle)
        db_adapter.save_candles(rows)        


    def connect_ebest(self):
        ebestSetLogger(self.app.log)
        self.app.log.debug('Connect eBest API')
        config = self.app.config.get('moontrader', 'ebest')
        ebest = ebestSession(config['url'], config['port'])
        ebest.login(config['id'], config['pw'], config['cert'])
        # self.app.log.info('Server Time: %s' % ebest.heartbeat().content)
        self.ebest = ebest

