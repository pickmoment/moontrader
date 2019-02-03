from pony.orm import *
from decimal import Decimal
from datetime import datetime, timedelta

def create_Candle(db):
    class Candle(db.Entity):
        _table_ = 'candles'
        dt = PrimaryKey(str)
        open = Required(Decimal, 12, 5)
        high = Required(Decimal, 12, 5)
        low = Required(Decimal, 12, 5)
        close = Required(Decimal, 12, 5)
        volume = Required(int)
        day = Required(str, index=True)

    return Candle


def create_StockCandle(db):
    class StockCandle(db.Entity):
        _table_ = 'stock_candles'
        dt = Required(str)
        cd = Required(str)
        open = Required(Decimal, 12, 2)
        high = Required(Decimal, 12, 2)
        low = Required(Decimal, 12, 2)
        close = Required(Decimal, 12, 2)
        volume = Required(int)
        amount = Optional(Decimal, 12, 2)
        adj_rate = Optional(float)
        PrimaryKey(dt,cd)

    return StockCandle
