# -*- coding: utf-8 -*-
import win32com.client
import time
import pythoncom
from enum import Enum
import datetime
# import os

class MarketType(Enum):
    INTERVAL = 0  #국내(주식,선물옵션)
    GLOBAL_STOCK = 1  #해외주식
    GLOBAL_DERIVATIVE = 2   #해외선물옵션
    INTERNAL_STOCK = 3    #국내 주식
    INTERVAL_KOSPIFUTURE = 4   #국내 코스피선물
    INTERVAL_KOSPIOPTION = 5   #국내 코스피옵션

DT_FORMAT = '%Y%m%d%H%M%S'
DAY_FORMAT = '%Y%m%d'
TIME_FORMAT = '%H%M%S'

DEFAULT_URL = 'simul.tradarglobal.api.com'
DEFAULT_PATH = 'c:/tools/YuantaAPI'

def calculate_dt(basedate, basetime, unit):
    dt = basedate + basetime
    return dt

def calculate_start(basedate, basetime, unit):
    dt = basedate + basetime
    if unit == 'd':
        return dt
    elif unit[:1] == 'm':
        stamp = datetime.datetime.strptime(dt, DT_FORMAT) - datetime.timedelta(minutes=int(unit[1:]))
        return stamp.strftime(DT_FORMAT)
    elif unit[:1] == 't':
        return ''

def calculate_day(basedate, basetime, unit):
    dt = basedate + basetime
    if unit == 'd':
        return basedate
    elif unit[:1] in ('m', 't'):
        stamp = datetime.datetime.strptime(dt, DT_FORMAT)
        if stamp <= datetime.datetime.strptime(basedate + '070000', DT_FORMAT):
            return (stamp - datetime.timedelta(days=1)).strftime(DAY_FORMAT)
        return stamp.strftime(DAY_FORMAT)

class SessionEventHandler:
    def __init__(self):
        self.code = -1
        self.msg = None
        self.real = {}
        self.query = {}

    def reset(self):
        self.code = -1
        self.msg = None

    def OnLogin(self, result, msg):
        if result == 2:
            print('로그인 성공')
            self.code = result
            self.msg = None
        else:
            print('로그인 실패', result, msg)
            self.code = result
            self.msg = msg

    def OnReceiveError(self, req_id, err_code, msg):
        print('OnReceiveError', req_id, err_code, msg)
        self.code = 1
        self.msg = msg
	
    def OnReceiveData(self, req_id, tr_id):
        print('OnReceiveData', req_id, tr_id)
        self.query['data'] = self.process_data(req_id, tr_id)
        # print(self.query)
        self.code = 0
        self.msg = None

    def OnReceiveRealData(self, req_id, auto_id):
        print('OnReceiveRealData', req_id, auto_id)
        if req_id not in self.real:
            self.real[req_id] = {}        
        self.real[req_id]['data'] = self.process_current(auto_id)
        print(self.real)
        self.code = 0
        self.msg = None

    def OnReceiveSystemMessage(self, n_id, msg):
        print('SystemMessage', n_id, msg)

    def process_data(self, req_id, tr_id):
        results = []

        block = 'NextBlock1'
        condate = self.YOA_GetTRFieldString(tr_id, block, 'condate', 0)
        contime = self.YOA_GetTRFieldString(tr_id, block, 'contime', 0)
        self.query['condate'] = condate
        self.query['contime'] = contime

        block = 'MSG'
        self.YOA_SetTRInfo(tr_id, block)
        count = self.YOA_GetRowCount(tr_id, block)
        for i in range(count-1):
            basedate = "{:06d}".format(self.YOA_GetFieldLong("basedate", i))
            basetime = "{:06d}".format(self.YOA_GetFieldLong("basetime", i))
            startjuka = self.YOA_GetFieldDouble("startjuka", i)
            highjuka = self.YOA_GetFieldDouble("highjuka", i)
            lowjuka = self.YOA_GetFieldDouble("lowjuka", i)
            lastjuka = self.YOA_GetFieldDouble("lastjuka", i)
            volume = self.YOA_GetFieldDouble("volume", i)
            results.append({
                'dt': calculate_dt(basedate, basetime, self.query['unit']),
                'open': startjuka,
                'high': highjuka,
                'low': lowjuka,
                'close': lastjuka,
                'volume': volume,
                'dt_start': calculate_start(basedate, basetime, self.query['unit']),
                'day': calculate_day(basedate, basetime, self.query['unit'])
            })
        # self.YOA_ReleaseData(req_id)
        return results

    def process_current(self, auto_id):
        current = {}
        block = 'OutBlock1'
        string_cols = ('jongcode','filter','time2','time','hightime','lowtime','filter1','filter2')
        double_cols = ('start','high','low','last','medoprice','mesuprice','changerate','change','startchange','highchange','lowchange','totmesuvol','totmedovol')
        long_cols = ('openinterest','opendebi','volume','nowvol','pointsize','dispscale')

        for c in string_cols:
            current[c] = self.YOA_GetTRFieldString(auto_id, block, c, 0)
        for c in double_cols:
            current[c] = self.YOA_GetTRFieldDouble(auto_id, block, c, 0)
        for c in long_cols:
            current[c] = self.YOA_GetTRFieldLong(auto_id, block, c, 0)
        return current

class Session:
    def __init__(self):
        self.api = win32com.client.DispatchWithEvents("YuantaAPICOM.YuantaAPI", SessionEventHandler)

    def waiting(self):
        start = time.time()
        while self.api.code < 0:
            pythoncom.PumpWaitingMessages()
            time.sleep(0.1)
            if time.time() - start > 5:
                return

    def login(self, id, pw, cert):
        self.api.reset()
        result = self.api.YOA_Login(id, pw, cert)
        if result != 1000:
            raise Exception('로그인 요청 실패')
        self.waiting()
        return self.api.code

    def connect(self, url=DEFAULT_URL, path=DEFAULT_PATH):
        result = self.api.YOA_Initial(url, path)
        if result != 1000:
            raise Exception('연결 실패')
        print('연결 성공')
        return result

    def disconnect(self):
        result = self.api.YOA_UnInitial()
        print('연결해제', result)
        return result

    def accounts(self):
        accounts = []
        count = self.api.YOA_GetAccountCount()
        for i in range(count):
            account = self.api.YOA_GetAccount(i)
            account_name = self.api.YOA_GetAccountInfo(1, account)
            account_nick = self.api.YOA_GetAccountInfo(2, account)
            account_type = self.api.YOA_GetAccountInfo(3, account)
            accounts.append({'account': account, 'name': account_name, 'nick': account_nick, 'type': account_type})

        return accounts

    def codes(self):
        market_type = MarketType.GLOBAL_DERIVATIVE.value
        codes = []
        count = self.api.YOA_GetCodeCount(market_type)
        for i in range(count):
            cd = self.api.YOA_GetCodeInfoByIndex(market_type, 0, i)
            std_cd = self.api.YOA_GetCodeInfoByIndex(market_type, 1, i)
            name = self.api.YOA_GetCodeInfoByIndex(market_type, 2, i)
            eng_name = self.api.YOA_GetCodeInfoByIndex(market_type, 3, i)
            market = self.api.YOA_GetCodeInfoByIndex(market_type, 4, i)
            # if market == '111' and 'CL' in cd:  # 해외선물
            if market == '111':
                code = {'cd':cd, 'name':name}
                codes.append(code)

        return codes

    def chart(self, code, unit, enddate='', endtime=''):
        self.api.reset()
        req_id = self.chart_call(code, unit, enddate, endtime)
        print(req_id)
        if req_id <= 1000:
            print('get_chart error', self.api.YOA_GetErrorMessage(self.api.YOA_GetLastError()))
            return []
        self.waiting()
        return self.get_query()

    def set_query(self, req_id, tr_id, code, unit, release, enddate, endtime):
        self.api.query['req_id'] = req_id
        self.api.query['tr_id'] = tr_id     
        self.api.query['code'] = code     
        self.api.query['unit'] = unit
        self.api.query['release'] = release
        self.api.query['enddate'] = enddate
        self.api.query['enddtime'] = endtime

    def get_query(self):
        return self.api.query

    def get_real(self):
        return self.api.real

    def chart_call(self, code, unit, enddate='', endtime='', r_id=-1):
        req_id = None
        tr_id = None
        if unit == 'd':
            (req_id, tr_id) = self.chart_day(code, enddate, r_id)
        elif unit[:1] in ('m', 't'):
            (req_id, tr_id) = self.chart_time(code, unit, enddate, endtime, r_id)
        self.set_query(req_id, tr_id, code, unit, True, enddate, endtime)
        return req_id

    def chart_day(self, code, enddate='', r_id=-1):
        tr_id = '820101'
        self.api.YOA_SetTRInfo(tr_id, "InBlock1")
        self.api.YOA_SetFieldString("jongcode", code, 0)
        self.api.YOA_SetFieldString("startdate", '', 0)
        self.api.YOA_SetFieldString("enddata", enddate, 0)
        self.api.YOA_SetFieldString("readcount", 500, 0)
        self.api.YOA_SetFieldString("link_yn", 'N', 0)
        req_id = self.api.YOA_Request(tr_id, True, r_id)
        return (req_id, tr_id)            

    def chart_time(self, code, timeunit, enddate='', endtime='', r_id=-1):
        now = datetime.datetime.now()
        if enddate == '':
            enddate = now.strftime(DAY_FORMAT)
        if endtime == '':
            endtime = now.strftime(TIME_FORMAT)

        tr_id = '820104' if timeunit[:1] == 'm' else '820106'
        self.api.YOA_SetTRInfo(tr_id, "InBlock1")
        self.api.YOA_SetFieldString("jongcode", code, 0)
        self.api.YOA_SetFieldString("timeuint", timeunit[1:], 0)
        self.api.YOA_SetFieldString("startdate", '', 0)
        self.api.YOA_SetFieldString("starttime", '', 0)
        self.api.YOA_SetFieldString("enddate", enddate, 0)
        self.api.YOA_SetFieldString("endtime", endtime, 0)
        self.api.YOA_SetFieldString("readcount", 500, 0)
        self.api.YOA_SetFieldString("link_yn", 'N', 0)
        req_id = self.api.YOA_Request(tr_id, True, r_id)
        return (req_id, tr_id)

    def chart_next(self, req_id):
        self.api.reset()
        req_id = int(req_id)
        req = self.get_query(req_id)
        req_id = self.chart_call(req['code'], req['unit'], req['condate'], req['contime'])
        print(req_id)
        if req_id <= 1000:
            print('get_chart error', self.api.YOA_GetErrorMessage(self.api.YOA_GetLastError()))
            return []
        self.waiting()
        return self.get_query()

    def request(self, req_id):
        req_id = int(req_id)
        req = self.api.query[req_id]
        ret = self.api.YOA_Request(req['tr_id'], False, req_id)
        print(ret)
        if ret <= 1000:
            print('get_chart error', self.api.YOA_GetErrorMessage(self.api.YOA_GetLastError()))
            return []
        self.waiting()
        return self.get_query(req_id)

    def release(self, req_id):
        req_id = int(req_id)
        ret = self.api.YOA_ReleaseData(req_id)
        if ret <= 1000:
            print(self.api.YOA_GetErrorMessage(self.api.YOA_GetLastError()))
        return ret

    def real_current(self, code):
        tr_id = '61'
        self.api.YOA_SetTRInfo(tr_id, "InBlock1")
        self.api.YOA_SetFieldString("jongcode", code, 0)
        req_id = self.api.YOA_RegistAuto(tr_id)
        self.set_real(req_id, tr_id, code)

    def set_real(self, req_id, auto_id, code):
        if req_id not in self.api.query:
            self.api.real[req_id] = {}
        self.api.real[req_id]['req_id'] = req_id
        self.api.real[req_id]['auto_id'] = auto_id
        self.api.real[req_id]['code'] = code

    def check(self):
        pythoncom.PumpWaitingMessages()
        return self.get_real()
        
if __name__ == '__main__':        
    url = 'simul.tradarglobal.api.com'
    path = 'c:/tools/YuantaAPI'

    session = Session()
    session.connect(url, path)
    session.login('moongux', 'gogo5', '')
    # print(session.real_current('ECU18'))
    print(session.real_current('CLG19'))
    while True:
        pythoncom.PumpWaitingMessages()
        time.sleep(1)
    # accounts = session.get_accounts()
    # print(accounts)
    # codes = session.get_codes(2)
    # [(lambda c: print(c))(code) for code in codes]
    # print(codes)
    # session.chart('CLV18', 'd')
    # session.disconnect()
    # session.clear()