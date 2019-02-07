from cement import Controller, ex
from ..core.db import db_adapter
from tqdm import tqdm
from pony.orm import Database
import requests
import json
import re
from html2text import html2text


STOCK_MARKET_START_DATE = '19560303'
DATE_FORMAT = '%Y%m%d'

DB_FILE_NAME = 'Dart'

class Dart(Controller):
    class Meta:
        label = 'dart'
        stacked_type = 'nested'
        stacked_on = 'base'

        arguments = [
            (['-s', '--save'], {'help': 'save to file',
                'action': 'store_true', 'dest': 'save'})
        ]


    @ex(help='get disclosure list',
        arguments=[(['--code', '--cd'], {'help': 'corporation code', 'action': 'store', 'dest': 'code'}),
            (['--start_date', '--start'], {'help': 'start date', 'action': 'store', 'dest': 'start_date'}),
            (['--end_date', '--end'], {'help': 'end date', 'action': 'store', 'dest': 'end_date'}),
            (['--loop'], {'help': 'loop count', 'action': 'store', 'dest': 'loop_count'})]
    )
    def disclosure(self):
        code = self.app.pargs.code
        start_date = self.app.pargs.start_date
        end_date = self.app.pargs.end_date
        loop_count = self.app.pargs.loop_count
        self.app.log.info('code: {}, start_date: {}, end_date: {}, loop: {}'.format(code, start_date, end_date, loop_count))

        url = 'http://dart.fss.or.kr/api/search.json?auth=a9cb7bfa9da7baa384bebafa92e73a3dae6cd9a5&page_set=100{}{}{}{}'
        param_code = '&crp_cd={}'.format(code) if code else ''
        param_start_date = '&start_dt={}'.format(start_date) if start_date else ''
        param_end_date = '&end_dt={}'.format(end_date) if end_date else ''

        with tqdm(total=100) as pbar:
            current_page = 1
            while True:
                param_page_no = '&page_no={}'.format(current_page)
                response = requests.get(url.format(param_code, param_start_date, param_end_date, param_page_no))
                data = json.loads(response.content)
                if current_page == 1:
                    total_page = data['total_page']
                    update_value = 100 / total_page
                pbar.update(update_value)
                self.treat_candle_save(current_page == 1, data)
                if current_page == total_page:
                    break
                current_page += 1

    @ex(help='get disclosure documents',
        arguments=[(['id'], {'help': 'disclosure id'})]
    )
    def disclosure_documents(self):
        id = self.app.pargs.id

        p = re.compile("openPdfDownload\('[0-9]+', '[0-9]+'\)")
        p2 = re.compile("[0-9]+")
        p3 = re.compile("/pdf/download/pdf.do\?rcp_no=[0-9]+&dcm_no=[0-9]+")

        # 첨부문서 ID
        url = 'http://dart.fss.or.kr/dsaf001/main.do?rcpNo={}'.format(id)
        self.app.log.info(url)
        response = requests.get(url)
        m = p.findall(response.text)
        docId = p2.findall(m[0])[1]
        print(docId)

        # 첨부문서 다운로드 경로
        url = 'http://dart.fss.or.kr/pdf/download/main.do?rcp_no={}&dcm_no={}'.format(id, docId)
        self.app.log.info(url)
        response = requests.get(url)
        download = p3.findall(response.text)
        print(download)

        # 목차
        url = 'http://m.dart.fss.or.kr/viewer/main.st?rcpNo={}&dcmNo={}'.format(id, docId)
        self.app.log.info(url)
        response = requests.get(url)
        toc = json.loads(response.text)['toc']
        print(toc)

        # page 내용
        self.print_page(id, toc)

    
    def print_page(self, id, toc):
        for i in range(len(toc)):
            url = 'http://m.dart.fss.or.kr/report/main.do'
            page = toc[i]
            data = {'rcpNo': id, 'dcmNo': page['dcmNo'], 'eleId': page['eleId']}
            self.app.log.info('url: {}, data: {}'.format(url, data))
            response = requests.post(url, data=data)
            content = response.text
            print(html2text(content))
            self.print_page(id, page['children'])

                
    
    def treat_candle_save(self, is_first, response):
        rows = response['list']
        if not rows:
            return
        self.app.log.debug('{} ({})'.format(rows[-1], len(rows)))

        if self.app.pargs.save:
            self.save_candle_data(rows, is_first)
        else:
            self.app.log.info('{} ({})'.format(rows, len(rows)))
        
        return rows     


    def save_candle_data(self, rows, need_init=False):
        if need_init:
            data_conf = self.app.config.get('moontrader', 'data')
            db_dart = Database()
            db_adapter.define_dart(db_dart)
            db_adapter.bind(db_dart, data_conf['dir'], DB_FILE_NAME)
            db_adapter.init(db_dart)
        db_adapter.save_dart_disclosures(rows)       

