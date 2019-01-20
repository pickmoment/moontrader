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
