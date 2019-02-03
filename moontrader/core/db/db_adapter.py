from pony.orm import *
from decimal import Decimal
from datetime import datetime, timedelta
from .candles import create_Candle
from .ebest import create_FutureCode
from .korea_stock import create_StockCode, create_StockTheme, create_StockCandle, create_StockSector, create_StockThemeCodeMap, create_StockSectorCodeMap

Candle = None
FutureCode = None

StockCode = None
StockTheme = None
StockThemeCodeMap = None
StockSector = None
StockSectorCodeMap = None
StockCandle = None

def bind(db, data_dir, file_name):
    file_path = '{}{}.sqlite'.format(data_dir, file_name)
    db.bind(provider='sqlite', filename=file_path, create_db=True)


def init(db):
    db.generate_mapping(create_tables=True)


def disconnect(db):
    db.disconnect()


def define_candle(db):
    global Candle
    Candle = create_Candle(db)


def define_korea_stock(db):
    global StockCandle
    StockCandle = create_StockCandle(db)
    global StockCode
    StockCode = create_StockCode(db)
    global StockTheme
    StockTheme = create_StockTheme(db)
    global StockSector
    StockSector = create_StockSector(db)
    global StockThemeCodeMap
    StockThemeCodeMap = create_StockThemeCodeMap(db)
    global StockSectorCodeMap
    StockSectorCodeMap = create_StockSectorCodeMap(db)


def define_ebest(db):
    global FutureCode
    FutureCode = create_FutureCode(db)


@db_session
def save_candles(rows):
    for row in rows:
        day = row['date']
        time = row['time'] if 'time' in row else ''        
        dt = day + time

        candle = Candle.get(dt=dt)
        if candle:
            candle.open = row['open']
            candle.high = row['high']
            candle.low = row['low']
            candle.close = row['close']
            candle.volume = row['volume']
        else:
            work_day = day
            if time >= '180000':
                work_day = (datetime.strptime(day, '%Y%m%d') + timedelta(days=1)).strftime('%Y%m%d')
            Candle(dt=dt, open=row['open'], high=row['high'], low=row['low'], close=row['close'], volume=row['volume'], day=work_day)
    

@db_session
def insert_future_codes(rows):
    for row in rows:
        FutureCode(cd=row['Symbol'], nm=row['SymbolNm'])   

def drop_future_codes():
    FutureCode.drop_table(with_all_data=True)

@db_session
def insert_stock_codes(rows):
    for row in rows:
        StockCode(cd=row['shcode'], nm=row['hname'], exp_cd=row['expcode'], market=row['gubun'], etf=row['etfgubun'])   

def drop_stock_codes():
    StockCode.drop_table(with_all_data=True)

@db_session
def insert_stock_themes(rows):
    for row in rows:
        StockTheme(cd=row['tmcode'], nm=row['tmname'])   

def drop_stock_themes():
    StockTheme.drop_table(with_all_data=True)


@db_session
def insert_stock_sectors(rows):
    for row in rows:
        StockSector(cd=row['upcode'], nm=row['hname'])   

def drop_stock_sectors():
    StockSector.drop_table(with_all_data=True)

@db_session
def delete_stock_theme_code_map(theme):
    StockThemeCodeMap.select(lambda t: t.theme == theme).delete(bulk=True)

@db_session
def insert_stock_theme_code_map(theme, rows): 
    for row in rows:
        StockThemeCodeMap(theme=theme, code=row['shcode'])

def drop_stock_theme_code_map():
    StockThemeCodeMap.drop_table(with_all_data=True)

@db_session
def delete_stock_sector_code_map(sector):
    StockSectorCodeMap.select(lambda t: t.sector == sector).delete(bulk=True)

@db_session
def insert_stock_sector_code_map(sector, rows):
    for row in rows:
        StockSectorCodeMap(sector=sector, code=row['shcode'])

def drop_stock_sector_code_map():
    StockSectorCodeMap.drop_table(with_all_data=True)


@db_session
def get_stock_codes():
    return StockCode.select()[:]


@db_session
def get_stock_themes():
    return StockTheme.select()[:]


@db_session
def get_stock_sectors():
    return StockSector.select()[:]


@db_session
def save_stock_candles(rows, code):
    for row in rows:
        dt = row['date']

        candle = StockCandle.get(dt=dt, cd=code)
        if candle:
            candle.open = row['open']
            candle.high = row['high']
            candle.low = row['low']
            candle.close = row['close']
            candle.volume = row['jdiff_vol']
            candle.amount = row['value']
            candle.adj_rate = row['rate']
        else:
            StockCandle(dt=dt, cd=code, open=row['open'], high=row['high'], low=row['low'], close=row['close'], volume=row['jdiff_vol'], amount=row['value'], adj_rate=row['rate'])
