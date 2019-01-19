from pony.orm import *

db = Database()
class Code(db.Entity):
    _table_ = 'codes'
    cd = PrimaryKey(str)
    nm = Required(str)

def bind(data_dir):
    db.bind(provider='sqlite', filename='{}ebest.sqlite'.format(data_dir), create_db=True)

def init():
    db.generate_mapping(create_tables=True)

@db_session
def insert_codes(rows):
    for row in rows:
        Code(cd=row['Symbol'], nm=row['SymbolNm'])