from pony.orm import *

def create_Code(db):
    class Code(db.Entity):
        _table_ = 'codes'
        cd = PrimaryKey(str)
        nm = Required(str)
    return Code
