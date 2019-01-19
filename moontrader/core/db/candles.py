from pony.orm import *
from decimal import Decimal
from datetime import datetime, timedelta

db = Database()
class Candle(db.Entity):
    _table_ = 'candles'
    dt = PrimaryKey(str)
    open = Required(Decimal)
    high = Required(Decimal)
    low = Required(Decimal)
    close = Required(Decimal)
    volume = Required(int)
    day = Required(str, index=True)


def bind(data_dir, code):
    db.bind(provider='sqlite', filename='{}{}.sqlite'.format(data_dir, code), create_db=True)


def init():
    db.generate_mapping(create_tables=True)


@db_session
def save_candles(rows):
    for row in rows:
        day = row['date']
        time = row['time'] if 'time' in row else ''        
        dt = day + time

        if Candle.get(dt=dt):
            continue

        work_day = day
        if time >= '180000':
            work_day = (datetime.strptime(day, '%Y%m%d') + timedelta(days=1)).strftime('%Y%m%d')
        Candle(dt=dt, open=row['open'], high=row['high'], low=row['low'], close=row['close'], volume=row['volume'], day=work_day)