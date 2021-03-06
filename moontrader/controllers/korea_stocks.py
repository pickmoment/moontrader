from cement import Controller, ex
from ..core.db import db_adapter
from ..core.xasession import Session as ebestSession, setLogger as ebestSetLogger
import time
from tqdm import tqdm
from pony.orm import Database
from datetime import datetime, timedelta
import math


STOCK_MARKET_START_DATE = '19560303'
DATE_FORMAT = '%Y%m%d'

DB_FILE_NAME = 'KoreaStocks'

class KoreaStocks(Controller):
    ebest = None

    class Meta:
        label = 'stocks'
        stacked_type = 'nested'
        stacked_on = 'base'

        arguments = [
            (['-s', '--save'], {'help': 'save to file',
                'action': 'store_true', 'dest': 'save'})
        ]


    @ex(help='get code list')
    def codes(self):
        self.connect_ebest()
        response = self.ebest.stock_codes()
        rows = response.content
        self.app.log.info(rows)

        if self.app.pargs.save:
            data_conf = self.app.config.get('moontrader', 'data')
            db_ebest = Database()
            db_adapter.define_korea_stock(db_ebest)
            db_adapter.bind(db_ebest, data_conf['dir'], DB_FILE_NAME)
            db_adapter.drop_stock_codes()
            db_adapter.init(db_ebest)
            db_adapter.insert_stock_codes(rows)


    @ex(help='get theme list')
    def themes(self):
        self.connect_ebest()
        response = self.ebest.stock_themes()
        rows = response.content
        self.app.log.info(rows)

        if self.app.pargs.save:
            data_conf = self.app.config.get('moontrader', 'data')
            db_ebest = Database()
            db_adapter.define_korea_stock(db_ebest)
            db_adapter.bind(db_ebest, data_conf['dir'], DB_FILE_NAME)
            db_adapter.drop_stock_themes()
            db_adapter.init(db_ebest)
            db_adapter.insert_stock_themes(rows)


    @ex(help='get all themes code map senario file', 
        arguments=[(['file_name'], {'help': 'senario file name'})])
    def all_themes_map(self):
        file_name = self.app.pargs.file_name
        self.app.log.info('file_name: {}'.format(file_name))

        data_conf = self.app.config.get('moontrader', 'data')
        db_ebest = Database()
        db_adapter.define_korea_stock(db_ebest)
        db_adapter.bind(db_ebest, data_conf['dir'], DB_FILE_NAME)
        db_adapter.init(db_ebest)
        themes = db_adapter.get_stock_themes()
        
        db_adapter.drop_stock_theme_code_map()

        with open(file_name, 'w') as sfile:
            for theme in themes:
                cmd = 'moontrader stocks -s theme-map {}'.format(theme.cd)
                print(cmd)
                sfile.write(cmd + '\n')


    @ex(help='get theme code map list', 
        arguments=[(['theme'], {})])
    def theme_map(self):
        theme = self.app.pargs.theme
        self.connect_ebest()
        response = self.ebest.stock_prices_by_theme(theme)
        rows = response.content
        self.app.log.info(rows)

        if self.app.pargs.save:
            data_conf = self.app.config.get('moontrader', 'data')
            db_ebest = Database()
            db_adapter.define_korea_stock(db_ebest)
            db_adapter.bind(db_ebest, data_conf['dir'], DB_FILE_NAME)
            db_adapter.init(db_ebest)
            db_adapter.delete_stock_theme_code_map(theme)
            db_adapter.insert_stock_theme_code_map(theme, rows)


    @ex(help='get sector list')
    def sectors(self):
        self.connect_ebest()
        response = self.ebest.stock_sectors()
        rows = response.content
        self.app.log.info(rows)

        if self.app.pargs.save:
            data_conf = self.app.config.get('moontrader', 'data')
            db_ebest = Database()
            db_adapter.define_korea_stock(db_ebest)
            db_adapter.bind(db_ebest, data_conf['dir'], DB_FILE_NAME)
            db_adapter.drop_stock_sectors()
            db_adapter.init(db_ebest)
            db_adapter.insert_stock_sectors(rows)


    @ex(help='get all sectors code map senario file', 
        arguments=[(['file_name'], {'help': 'senario file name'})])
    def all_sectors_map(self):
        file_name = self.app.pargs.file_name
        self.app.log.info('file_name: {}'.format(file_name))

        data_conf = self.app.config.get('moontrader', 'data')
        db_ebest = Database()
        db_adapter.define_korea_stock(db_ebest)
        db_adapter.bind(db_ebest, data_conf['dir'], DB_FILE_NAME)
        db_adapter.init(db_ebest)
        sectors = db_adapter.get_stock_sectors()
        
        db_adapter.drop_stock_sector_code_map()

        with open(file_name, 'w') as sfile:
            for sector in sectors:
                cmd = 'moontrader stocks -s sector-map {}'.format(sector.cd)
                print(cmd)
                sfile.write(cmd + '\n')


    @ex(help='get sector code map list', 
        arguments=[(['sector'], {})])
    def sector_map(self):
        sector = self.app.pargs.sector
        self.connect_ebest()

        if self.app.pargs.save:
            data_conf = self.app.config.get('moontrader', 'data')
            db_ebest = Database()
            db_adapter.define_korea_stock(db_ebest)
            db_adapter.bind(db_ebest, data_conf['dir'], DB_FILE_NAME)
            db_adapter.init(db_ebest)
            db_adapter.delete_stock_sector_code_map(sector)

        start_code = ''
        while True:
            response = self.ebest.stock_prices_by_sector(sector, start_code)
            rows = response.content
            self.app.log.info(rows)

            if self.app.pargs.save:
                db_adapter.insert_stock_sector_code_map(sector, rows)

            if (len(rows) < 40):
                break
            else:
                start_code = rows[-1]['shcode']
                time.sleep(0.2)

            
    @ex(help='get candle list',
        arguments=[(['code'],{}), 
            (['--start_date', '--start'], {'help': 'start date', 'action': 'store', 'dest': 'start_date'}),
            (['--end_date', '--end'], {'help': 'end date', 'action': 'store', 'dest': 'end_date'}),
            (['--loop'], {'help': 'loop count', 'action': 'store', 'dest': 'loop_count'})]
    )
    def candle(self):
        code = self.app.pargs.code
        start_date = self.app.pargs.start_date
        end_date = self.app.pargs.end_date
        loop_count = self.app.pargs.loop_count
        start_datetime, end_datetime = self.get_datetime_range(start_date if start_date else STOCK_MARKET_START_DATE, end_date)
        loop_count = int(loop_count) if loop_count else math.ceil((end_datetime - start_datetime).days / 500)
        self.app.log.info('code: {}, start_date: {}, end_date: {}, loop: {}'.format(code, start_date, end_date, loop_count))

        self.connect_ebest()

        response = None
        for i in tqdm(range(loop_count)):
            if response and not response.has_cts:
                break
            response = self.get_stock_candle(code, start_date, end_date)
            self.treat_candle_save(i == 0, response, code)
            if response.has_cts:
                end_date = response._cts_map['cts_date']

    
    @ex(help='get scenario for all stock candle list',
        arguments=[(['file_name'], {'help': 'senario file name'}),
            (['--start_date', '--start'], {'help': 'start date', 'action': 'store', 'dest': 'start_date'}),
            (['--end_date', '--end'], {'help': 'end date', 'action': 'store', 'dest': 'end_date'}),
            (['--short'], {'help': 'short period', 'action': 'store_true', 'dest': 'is_short'}),
            (['--loop'], {'help': 'loop count', 'action': 'store', 'dest': 'loop_count'})]    )
    def all_stock_candles(self):
        start_date = self.app.pargs.start_date
        end_date = self.app.pargs.end_date
        loop_count = self.app.pargs.loop_count
        file_name = self.app.pargs.file_name
        is_short = self.app.pargs.is_short
        self.app.log.info('start_date: {}, end_date: {}, loop: {}, file_name: {}, is_short: {}'.format(start_date, end_date, loop_count, file_name, is_short))

        data_conf = self.app.config.get('moontrader', 'data')
        db_ebest = Database()
        db_adapter.define_korea_stock(db_ebest)
        db_adapter.bind(db_ebest, data_conf['dir'], DB_FILE_NAME)
        db_adapter.init(db_ebest)
        codes = db_adapter.get_stock_codes()

        param_start = ' --start {}'.format(start_date) if start_date else ''
        param_end = ' --end {}'.format(end_date) if end_date else ''
        param_loop = ' --loop {}'.format(loop_count) if loop_count else ''

        if is_short:
            param_start = ' --start {yesterday}'
            param_end = ' --end {today}'

        with open(file_name, 'w') as sfile:
            for code in codes:
                cmd = 'moontrader stocks -s candle {}{}{}{}'.format(code.cd, param_start, param_end, param_loop)
                print(cmd)
                sfile.write(cmd + '\n')


    def get_datetime_range(self, start_date, end_date):
        today = datetime.now()
        if not end_date:
            end_datetime = today
        else:
            end_datetime = datetime.strptime(end_date, DATE_FORMAT)
        
        if not start_date:
            start_datetime = end_datetime - timedelta(days=800)
        else:
            start_datetime = datetime.strptime(start_date, DATE_FORMAT)

        return start_datetime, end_datetime      


    def get_stock_candle(self, code, start_date, end_date):
        today = datetime.now()
        if not end_date:
            end_date = today.strftime(DATE_FORMAT)
        if not start_date:
            start_date = (datetime.strptime(end_date, DATE_FORMAT) - timedelta(days=800)).strftime(DATE_FORMAT)

        response = self.ebest.stock_candle_day(code, start_date, end_date)
        return response


    def treat_candle_save(self, is_first, response, code):
        rows = response.content
        if not rows:
            return
        self.app.log.debug('{} ({})'.format(rows[-1], len(rows)))

        if self.app.pargs.save:
            self.save_candle_data(rows, code, is_first)
        else:
            self.app.log.info('{} ({})'.format(rows, len(rows)))
        
        return rows     


    def save_candle_data(self, rows, code, need_init=False):
        if need_init:
            data_conf = self.app.config.get('moontrader', 'data')
            db_candle = Database()
            db_adapter.define_korea_stock(db_candle)
            db_adapter.bind(db_candle, data_conf['dir'], DB_FILE_NAME)
            db_adapter.init(db_candle)
        db_adapter.save_stock_candles(rows, code)       


    def connect_ebest(self):
        ebestSetLogger(self.app.log)
        self.app.log.debug('Connect eBest API')
        config = self.app.config.get('moontrader', 'ebest')
        ebest = ebestSession(config['url'], config['port'])
        ebest.login(config['id'], config['pw'], config['cert'])
        # self.app.log.info('Server Time: %s' % ebest.heartbeat().content)
        self.ebest = ebest

