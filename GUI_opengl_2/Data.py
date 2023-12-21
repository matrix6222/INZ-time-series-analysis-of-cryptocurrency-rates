from time import time, sleep
import numpy as np
from json import loads
import asyncio
import aiohttp
import pandas as pd

pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)


class Data:
	def __init__(self, symbols, interval_ms, data_len, locks):
		self.interval_ms = interval_ms
		self.data_len = data_len
		self.symbols = symbols
		self.locks = locks

		self.request_columns = ['Kline-open-time', 'Open-price', 'High-price', 'Low-price', 'Close-price', 'Volume', 'Kline-Close-time', 'Quote-asset-volume', 'Number-of-trades', 'Taker-buy-base-asset-volume', 'Taker-buy-quote-asset-volume', 'Unused-field']
		self.request_columns_dtypes = [np.int64, np.float32, np.float32, np.float32, np.float32, np.float32, np.int64, np.float32, np.float32, np.float32, np.float32, np.int64]
		self.data_columns = sum([['{}-{}'.format(symbol, column_name) for column_name in self.request_columns] for symbol in symbols], [])
		self.data_columns_dtypes = sum([[column_dtype for column_dtype in self.request_columns_dtypes] for symbol in symbols], [])
		self.data_columns_dtypes = {name: dtype for name, dtype in zip(self.data_columns, self.data_columns_dtypes)}
		self.data_past = pd.DataFrame(columns=self.data_columns)
		self.data_past = self.data_past.astype(self.data_columns_dtypes)

		if self.interval_ms == 60_000:
			self.interval_ms_name = '1m'
		else:
			print('Invalid interval ms -> [60_000]')

	def run(self, loop, callback):
		verbose = False
		asyncio.set_event_loop(loop)

		time_actual_ms = int(time()) * 1000
		time_end_ms = time_actual_ms // self.interval_ms * self.interval_ms - 1
		time_start_ms = time_end_ms - self.data_len * self.interval_ms

		if verbose:
			print('time_actual_ms: {}ms'.format(time_actual_ms))
			print('time_start_ms: {}ms'.format(time_start_ms))
			print('time_end_ms: {}ms'.format(time_end_ms))

		temp = loop.run_until_complete(self.download_data(self.interval_ms_name, time_start_ms, time_end_ms, 1000, verbose=verbose))

		while temp == -1:
			sleep(1.0)
			print('data not loaded properly, trying again to fetch')
			temp = loop.run_until_complete(self.download_data(self.interval_ms_name, time_start_ms, time_end_ms, 1000, verbose=verbose))

		temp = [sum([temp[y][x] for y in range(len(temp))], []) for x in range(len(temp[0]))]
		with self.locks['data_past']:
			for i, (col, dtype) in enumerate(self.data_columns_dtypes.items()):
				self.data_past[col] = pd.Series([row[i] for row in temp], dtype=dtype)
		callback()
			#print(self.data_past)

		while True:
			with self.locks['data_past']:
				time_next_fetch = self.data_past[self.symbols[0] + '-Kline-open-time'].iloc[-1] + self.interval_ms * 2
			wait_s = time_next_fetch / 1000 - time()
			if verbose:
				print('time_next_fetch: ', time_next_fetch)
				print('wait_s: ', wait_s)
			sleep(max(0, wait_s))

			time_actual_ms = int(time()) * 1000
			time_end_ms = time_actual_ms // self.interval_ms * self.interval_ms - 1
			time_start_ms = time_end_ms - self.data_len * self.interval_ms

			if verbose:
				print('time_actual_ms: {}ms'.format(time_actual_ms))
				print('time_start_ms: {}ms'.format(time_start_ms))
				print('time_end_ms: {}ms'.format(time_end_ms))

			temp = loop.run_until_complete(self.download_data(self.interval_ms_name, time_start_ms, time_end_ms, 1000, verbose=verbose))

			while temp == -1:
				sleep(1.0)
				print('data not loaded properly, trying again to fetch')
				temp = loop.run_until_complete(self.download_data(self.interval_ms_name, time_start_ms, time_end_ms, 1000, verbose=verbose))

			temp = [sum([temp[y][x] for y in range(len(temp))], []) for x in range(len(temp[0]))]
			with self.locks['data_past']:
				for i, (col, dtype) in enumerate(self.data_columns_dtypes.items()):
					self.data_past[col] = pd.Series([row[i] for row in temp], dtype=dtype)
			callback()

	async def download_data(self, interval, start_time_ms, end_time_ms, limit, verbose=False):
		data = []
		async with aiohttp.ClientSession() as session:
			print("Send requests at time: {}s".format(time()))
			responses = await asyncio.gather(*[self.fetch(session, 'https://api.binance.com/api/v3/klines?symbol={}&interval={}&startTime={}&endTime={}&limit={}'.format(symbol, interval, int(start_time_ms), int(end_time_ms), limit)) for symbol in self.symbols])
		if verbose:
			for res in responses:
				res = res.replace('"', '')
				try:
					json = loads(res)
					if not isinstance(json, list):
						print('json is not list')
						return -1
					if len(json) != self.data_len:
						print('invalid length of timeseries')
						return -1
					for row in json:
						if not isinstance(row, list):
							print('row is not list')
							return -1
						if len(row) != 12:
							print('row length is not equal 12')
							return -1
					print('good')
					data.append(json)
				except:
					print('json = loads() error')
					return -1
			if len(data) != len(self.symbols):
				print('all symbols not loaded')
				return -1

		else:
			for res in responses:
				res = res.replace('"', '')
				try:
					json = loads(res)
					if not isinstance(json, list):
						return -1
					if len(json) != self.data_len:
						return -1
					for row in json:
						if not isinstance(row, list):
							return -1
						if len(row) != 12:
							return -1
					data.append(json)
				except:
					return -1
			if len(data) != len(self.symbols):
				return -1

		return data

	async def fetch(self, session, url):
		async with session.get(url) as res:
			return await res.text()
