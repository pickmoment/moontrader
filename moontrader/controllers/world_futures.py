from cement import Controller, ex

month_map = {'F': 1, 'G': 2, 'H': 3, 'J': 4, 'K': 5, 'M': 6, 
             'N': 7, 'Q': 8, 'U': 9, 'V': 10, 'X': 11, 'Z': 12}

class WorldFutures(Controller):
    class Meta:
        label = 'world_futures'
        stacked_type = 'embedded'
        stacked_on = 'base'

    @ex(help='get code list')
    def codes(self):
        response = self.app.ebest.codes()
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
