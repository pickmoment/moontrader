# -*- coding: utf-8 -*-
import win32com.client
import time
import pythoncom
from .xaquery import Query, setLogger as querySetLogger
import logging

log = logging.getLogger()

def setLogger(logger):
    global log
    log = logger
    querySetLogger(logger)

class _XASessionEvents:
    def __init__(self):
        self.code = -1
        self.msg = None

    def reset(self):
        self.code = -1
        self.msg = None

    def OnLogin(self, code, msg):
        self.code = str(code)
        self.msg = str(msg)
        log.debug('[OnLogin] code:{}, msg:{}'.format(code, msg))

    def OnLogout(self):
        log.debug("[OnLogout] method is called")

    def OnDisconnect(self):
        log.debug("[OnDisconnect] method is called")

class Session:
    def __init__(self, url, port):
        self.session = win32com.client.DispatchWithEvents("XA_Session.XASession", _XASessionEvents)
        self.url = url
        self.port = port

    def login(self, user_id, user_pw, user_cert):
        self.session.reset()
        self.session.ConnectServer(self.url, self.port)
        self.session.Login(user_id, user_pw, user_cert, 0, False)
        while self.session.code == -1:
            pythoncom.PumpWaitingMessages()
            time.sleep(0.1)

        if self.session.code == "0000":
            log.debug("로그인 성공")
            return True
        else:
            log.error("로그인 실패 : %s" % xacom.parseErrorCode(self.session.code))
            return False

    def logout(self):
        """서버와의 연결을 끊는다.
            ::
                session.logout()
        """
        self.session.DisconnectServer()
        log.debug('Request DisconnectServer')

    def account(self):
        """계좌 정보를 반환한다.
            :return: 계좌 정보를 반환한다.
            :rtype: object {no:"계좌번호",name:"계좌이름",detailName:"계좌상세이름"}
            ::
                session.account()
        """
        acc = []
        for p in range(self.session.GetAccountListCount()):
            acc.append({
                "no" : self.session.GetAccountList(p),
                "name" : self.session.GetAccountName(p),
                "detailName" : self.session.GetAcctDetailName(p)
            })
        return acc

    def heartbeat(self):
        response = Query("t0167").request(
            input = {}, 
            output = {
                'block': 'OutBlock',
                'cols': ('dt', 'time')
            }
        )
        return response

    def codes(self):
        response = Query("o3101").request(
            input = {'gubun': ''}, 
            output = {
                'block': 'OutBlock',
                'cols': ('Symbol', 'SymbolNm')
            }
        )
        return response

    def candle_minute(self, code, minute, date=None, time=None):
        input_param = {'shcode': code, 'ncnt': minute}
        if date:
            input_param['cts_date'] = date
        if time:
            input_param['cts_time'] = time
        log.debug('[candle_minute] input: {}'.format(input_param))
        response = Query('o3103').request(
            input = input_param, 
            output = {
                'block': 'OutBlock1',
                'cols': ('date', 'time', 'open', 'high', 'low', 'close', 'volume')
            },
            cts = {
                'block': 'OutBlock',
                'cols': ('cts_date', 'cts_time')
            } 
        )
        return response


    def candle_day(self, code, start_day, end_day, cts_date=None):
        input_param = {'shcode': code, 'gubun': '0', 'sdate': start_day, 'edate': end_day}
        if cts_date:
            input_param['cts_date'] = cts_date
        log.debug('[candle_day] input: {}'.format(input_param))
        response = Query('o3108').request(
            input = input_param, 
            output = {
                'block': 'OutBlock1',
                'cols': ('date', 'open', 'high', 'low', 'close', 'volume')
            }
        )
        return response