from pony.orm import *
from decimal import Decimal
from datetime import datetime, timedelta


def create_StockCode(db):
    class StockCode(db.Entity):
        _table_ = 'stock_codes'
        cd = PrimaryKey(str)
        nm = Required(str)
        exp_cd = Required(str)
        market = Required(str)
        etf = Required(str)
    return StockCode


def create_StockTheme(db):
    class StockTheme(db.Entity):
        _table_ = 'stock_themes'
        cd = PrimaryKey(str)
        nm = Required(str)
    return StockTheme 


def create_StockThemeCodeMap(db):
    class StockThemeCodeMap(db.Entity):
        _table_ = 'stock_theme_codes'
        theme = PrimaryKey(str)
        code = Required(str)
    return StockThemeCodeMap


def create_StockSector(db):
    class StockSector(db.Entity):
        _table_ = 'stock_sectors'
        cd = PrimaryKey(str)
        nm = Required(str)
    return StockSector  


def create_StockSectorCodeMap(db):
    class StockSectorCodeMap(db.Entity):
        _table_ = 'stock_sector_codes'
        sector = PrimaryKey(str)
        code = Required(str)
    return StockSectorCodeMap  


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
