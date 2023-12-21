import numpy as np


class StochRSI:
	def __init__(self):
		pass

	@staticmethod
	def about_me():
		ret = {
			'required_fields':
				{
					'Period RSI':
						{
							'min': 2,
							'max': 200,
						},
					'Period Stoch':
						{
							'min': 1,
							'max': 200,
						},
					'Smooth K':
						{
							'min': 2,
							'max': 200,
						},
					'Smooth D':
						{
							'min': 2,
							'max': 200,
						},
				},
			'colors':
				[
					'Color K%',
					'Color D%',
				]
		}
		return ret

	def calc_output_len(self, data_len, params):
		period_rsi = params['Period RSI']
		smooth_k = params['Smooth K']
		smooth_d = params['Smooth D']
		rsi_len = data_len - period_rsi
		k_len = rsi_len - smooth_k + 1
		d_len = k_len - smooth_d + 1
		return [k_len, d_len]

	def _calc_rsi(self, data, period):
		output_shape = (data.shape[0] - period, data.shape[1])
		gain = np.zeros(output_shape, dtype=np.float32)
		loss = np.zeros(output_shape, dtype=np.float32)
		delta = np.diff(data, axis=0)
		delta_positive = np.where(delta > 0, delta, 0)
		delta_negative = np.where(delta < 0, -delta, 0)
		gain[0] = np.sum(delta_positive[0: period], axis=0) / period
		loss[0] = np.sum(delta_negative[0: period], axis=0) / period
		for x in range(1, output_shape[0]):
			gain[x] = (gain[x - 1] * (period - 1) + delta_positive[x + period - 1]) / period
			loss[x] = (loss[x - 1] * (period - 1) + delta_negative[x + period - 1]) / period
		return 100 - (100 / (1 + (gain / np.where(loss != 0, loss, 0.0000000001))))

	def _calc_hlc(self, data, period):
		ret = []
		for x in range(1, data.shape[0] + 1):
			timeseries = data[x - period if x - period > 0 else 0: x]
			lowest = timeseries.min(axis=0)
			highest = timeseries.max(axis=0)
			c = timeseries[-1]
			ret.append([highest, lowest, c])
		return np.array(ret, dtype=np.float32)

	def _calc_k(self, data, period):
		# %K = 100 x ( Recent Close - Lowest Low(n) / Highest High(n) - Lowest Low(n) )
		hlc = self._calc_hlc(data, period)
		h, l, c = hlc[:, 0, :], hlc[:, 1, :], hlc[:, 2, :]
		return 100 * ((c - l) / np.where(h == l, 0.0000000000001, h - l))

	def _calc_sma(self, data, period):
		#ret = []
		#for x in range(data.shape[0] - period + 1):
		#	avg = np.sum(data[x: x + period], axis=0) / np.float32(period)
		#	ret.append(avg)
		#return np.array(ret, dtype=np.float32)

		kernel = np.ones(period) / period
		return np.apply_along_axis(lambda x: np.convolve(x, kernel, mode='valid'), axis=0, arr=data)

	def calc(self, df, symbols, params):
		period_rsi = params['Period RSI']
		period_stoch = params['Period Stoch']
		smooth_k = params['Smooth K']
		smooth_d = params['Smooth D']
		column_names = sum([[symbol + column for column in ['-Close-price']] for symbol in symbols], [])
		data = df[column_names].values.astype(np.float32)

		rsi = self._calc_rsi(data, period_rsi)
		k = self._calc_k(rsi, period_stoch)
		k = self._calc_sma(k, smooth_k)
		d = self._calc_sma(k, smooth_d)

		return k, d
		#return np.concatenate((np.expand_dims(k, axis=-1), np.expand_dims(d, axis=-1)), axis=-1)
