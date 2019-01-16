import sys
from PyQt5.QtWidgets import *
from PyQt5.QAxContainer import *
from PyQt5.QtCore import *

trcode_map = {
    'opc10001': {
        'name': '해외선물옵션틱차트조회',
        'items': ['체결시간','시가','고가','저가','현재가','거래량','영업일자'],
        'keys': ['dt','open','high','low','close','volume','day']
    },
    'opc10002': {
        'name': '해외선물옵션분차트조회',
        'items': ['체결시간','시가','고가','저가','현재가','거래량','영업일자'],
        'keys': ['dt','open','high','low','close','volume','day']
    },
    'opc10003': {
        'name': '해외선물옵션일차트조회',
        'items': ['일자','시가','고가','저가','현재가','누적거래량','영업일자'],
        'keys': ['dt','open','high','low','close','volume','day']
    }
}

unit_map = {
    'M': 'opc10002',
    'T': 'opc10001',
    'D': 'opc10003'
}

class KiwoomF(QAxWidget):
    def __init__(self):
        super().__init__()
        self._create_kiwoom_instance()
        self._set_signal_slot()

    def _create_kiwoom_instance(self):
        self.setControl("KFOPENAPI.KFOpenAPICtrl.1")

    def _set_signal_slot(self):
        self.OnEventConnect.connect(self._event_connect)
        self.OnReceiveTrData.connect(self._receive_tr_data)
        
    def comm_connect(self, callback):
        self._event_connect_callback = callback
        self.dynamicCall("CommConnect(1)")
        # self.login_event_loop = QEventLoop()
        # self.login_event_loop.exec_()

    def comm_terminate(self):
        self.dynamicCall("CommTerminate()")
        self.get_connect_state()

    def get_connect_state(self):
        state = self.dynamicCall("GetConnectState()")
        print('연결상태', state)

    def _event_connect(self, err_code):
        if err_code == 0:
            print("로그인 성공")
            self.get_connect_state()
        else:
            print("로그인 실패")

        self._event_connect_callback(err_code)
        
        # self.login_event_loop.exit()

    def get_future_code_info_map(self, item_type, callback):
        code_infos = self.dynamicCall("GetGlobalFutOpCodeInfoByType(int, QString)", 0, item_type)
        code_info_map = self.make_code_info_map(code_infos)
        callback(code_info_map)        

    def make_code_info_list(self, code_infos):
        n = 170
        code_info_list = [code_infos[i:i+n] for i in range(0, len(code_infos), n)]
        lengths = [12, 6, 40, 3, 3, 15, 15, 15, 15, 1, 15, 10, 8, 10, 1, 1]
        results = []
        for code_info in code_info_list:
            start = 0
            row = []
            for l in lengths:
                row.append(code_info[start:start+l].strip())
                start += l
            results.append(row)
        return results

    def make_code_info_map(self, code_infos):
        code_info_list = self.make_code_info_list(code_infos)
        code_info_map = {}
        for code_info in code_info_list:
            code = code_info[0][2:]
            item = code_info[1]
            item_name = code_info[2][:-7]
            code_name = code_info[2][-6:-1]
            recent = code_info[14]
            active = code_info[15]
            if item not in code_info_map:
                code_info_map[item] = {'name': item_name, 'codes': []}
            code_info_map[item]['codes'].append({'code': code, 'name': code_name + ("*" if active == '1' else '')})
        return code_info_map


    def get_future_item_list(self, callback):
        item_list = self.dynamicCall("GetGlobalFutureItemlist()")
        callback(item_list.split(';'))

    def get_future_code_list(self, item, callback):
        code_list = self.dynamicCall("GetGlobalFutureCodelist(QString)", item)
        callback(code_list)

    def _set_input_value(self, id, value):
        self.dynamicCall("SetInputValue(QString, QString)", id, value)

    def _comm_rq_data(self, trcode, next, code_timeunit):
        rqname = code_timeunit #trcode
        screen_no = trcode[-5:]
        # print('CommRqData - rqname: {}, trcode: {}, next: {}, screen_no: {}'.format(rqname, trcode, next, screen_no))
        response = self.dynamicCall("CommRqData(QString, QString, QString, QString)", rqname, trcode, next, screen_no)
        # print('CommRqData - response: {}'.format(response))
        # self.tr_event_loop = QEventLoop()
        # self.tr_event_loop.exec_()

    def _get_comm_data(self, code, record_name, index, item_name):
        ret = self.dynamicCall("GetCommData(QString, QString, int, QString)", code,
                               record_name, index, item_name)
        return ret.strip()

    def _get_repeat_cnt(self, trcode, rqname):
        ret = self.dynamicCall("GetRepeatCnt(QString, QString)", trcode, rqname)
        return ret

    def _receive_tr_data(self, screen_no, rqname, trcode, record_name, next):
        # print('receive_tr_data - trcode: {}, rqname: {}, record_name: {}, next: {}'.format(trcode, rqname, record_name, next))
        data = self._read_tr_data(trcode, rqname)
        self._receive_tr_data_callback(data, next.strip(), rqname)
 
        # try:
        #     self.tr_event_loop.exit()
        # except AttributeError:
        #     pass    

    def _read_tr_data(self, trcode, rqname):
        conf = trcode_map[trcode]
        if conf:
            data_cnt = self._get_repeat_cnt(trcode, rqname)
            data = []
            for i in range(data_cnt):
                candle = {}
                for k in range(len(conf['items'])):
                    key = conf['keys'][k]
                    item = conf['items'][k]
                    candle[key] = self._get_comm_data(trcode, rqname, i, item)
                
                data.append(candle)
            return data

        return {}


    def get_ohlc(self, code, time_unit, callback, next):
        if len(time_unit) > 1:
            time = int(time_unit[:-1])
        unit = time_unit[-1:].upper()
        self._receive_tr_data_callback = callback
        self._set_input_value('종목코드', code)
        if unit == 'D':
            self._set_input_value('조회일자', '')
        else:
            self._set_input_value('시간단위', time)
        self._comm_rq_data(unit_map[unit], next, code+'/'+time_unit)