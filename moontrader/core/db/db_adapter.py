from pony.orm import *
from decimal import Decimal
from datetime import datetime, timedelta
from .candles import create_Candle
from .ebest import create_Code

Candle = None
Code = None

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

def define_ebest(db):
    global Code
    Code = create_Code(db)


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
def insert_codes(rows):
    for row in rows:
        Code(cd=row['Symbol'], nm=row['SymbolNm'])   

def drop_codes():
    Code.drop_table(with_all_data=True)