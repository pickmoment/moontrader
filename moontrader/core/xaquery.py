# -*- coding: utf-8 -*-
import time
import pythoncom
import win32com.client
from datetime import datetime
import logging

log = logging.getLogger()

def setLogger(logger):
	log = logger

class _XAQueryEvents:
	def __init__(self):
		self.status = 0
		self.code = None
		self.msg = None

	def reset(self):
		self.status = 0
		self.code = None
		self.msg = None

	def OnReceiveData(self, szTrCode):
		self.status = 1

	def OnReceiveMessage(self, systemError, messageCode, message):
		self.code = str(messageCode)
		self.msg = str(message)
		log.debug("OnReceiveMessage", self.code, self.msg)

class Query:
	_in_block = 'InBlock'
	_out_block = None
	_out_cols = None
	_cts_block = None
	_cts_cols = None
	_cts_map = {}
	has_cts = False
	content = []

	def __init__(self, type):
		self.query = win32com.client.DispatchWithEvents("XA_DataSet.XAQuery", _XAQueryEvents)
		self.query.LoadFromResFile("Res/" + type + ".res")
		self.type = type;

	def request(self, input, output, cts=None):	
		self.content = []

		self._out_block = output['block']
		self._out_cols = output['cols']
		for k,v in input.items():
			self.query.SetFieldData(self.type + self._in_block, k, 0, v)

		self._query_request(False)
		self._wait_content()
		self._update_content()
		if cts:
			self._cts_block = cts['block']
			self._cts_cols = cts['cols']
			self._update_cts()

		return self

	def request_next(self):
		self.content = []

		if self.has_cts == False:
			return self

		for col in self._cts_cols:
			self.query.SetFieldData(self.type + self._in_block, col, 0, self._cts_map[col])
		
		self._query_request(True)
		self._wait_content()		
		self._update_content()
		self._update_cts()

		return self


	def _query_request(self, is_cts):
		requestCode = self.query.Request(is_cts)
		if requestCode < 0:
			log.critical(requestCode)
			return self		

	def _wait_content(self):
		while self.query.status == 0:
			pythoncom.PumpWaitingMessages()
			time.sleep(0.1)
		self.query.status = 0

	def _update_content(self):
		row_count = self.query.GetBlockCount(self.type + self._out_block)
		for i in range(row_count):
			row = {}
			self.content.append(row)
			for col in self._out_cols:
				row[col] = self.query.GetFieldData(self.type + self._out_block, col, i)		

	def _update_cts(self):
		self.has_cts = False
		for col in self._cts_cols:
			cts_value = self.query.GetFieldData(self.type + self._cts_block, col, 0)
			self._cts_map[col] = cts_value
			if cts_value:
				self.has_cts = True		
