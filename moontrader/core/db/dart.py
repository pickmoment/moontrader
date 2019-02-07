from pony.orm import *

def create_Disclosure(db):
    class Disclosure(db.Entity):
        _table_ = 'disclosures'
        id = PrimaryKey(str)
        title = Required(str)
        corp_cd = Required(str, index=True)
        corp_nm = Required(str)
        corp_cls = Required(str)
        dt = Required(str, index=True)
        writer = Required(str)
        remark = Optional(str)

    return Disclosure
