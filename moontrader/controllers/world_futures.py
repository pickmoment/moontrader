from cement import Controller, ex
from pony.orm import *

month_map = {'F': 1, 'G': 2, 'H': 3, 'J': 4, 'K': 5, 'M': 6, 
             'N': 7, 'Q': 8, 'U': 9, 'V': 10, 'X': 11, 'Z': 12}

db = Database()
class Code(db.Entity):
    _table_ = 'codes'
    cd = PrimaryKey(str)
    nm = Required(str)

@db_session
def insert_codes(rows):
    for row in rows:
        Code(cd=row['Symbol'], nm=row['SymbolNm'])

class WorldFutures(Controller):
    class Meta:
        label = 'futures'
        stacked_type = 'embedded'
        stacked_on = 'base'

        arguments = [
            (['-s', '--save'], {'help': 'save to file',
                'action': 'store_true', 'dest': 'save'})
        ]

    @ex(help='get code list')
    def codes(self):
        response = self.app.ebest.codes()
        rows = response.content

        if self.app.pargs.save:
            data_conf = self.app.config.get('moontrader', 'data')
            db.bind(provider='sqlite', filename=data_conf['dir']+'ebest.sqlite', create_db=True)
            Code.drop_table(with_all_data=True)
            db.generate_mapping(create_tables=True)
            insert_codes(rows)
        self.app.log.info(response.content)

    @ex(help='get minute candle list',
        arguments=[(['code'],{}), (['minute'],{})]
    )
    def candle_minute(self):
        code = self.app.pargs.code
        minute = self.app.pargs.minute
        response = self.app.ebest.candle_minute(code, minute)
        self.app.log.info(response.content)
        self.app.log.info(len(response.content))
        if response.has_cts:
            response = response.request_next()
            self.app.log.info(response.content)
            self.app.log.info(len(response.content))
