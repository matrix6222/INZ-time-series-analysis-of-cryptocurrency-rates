import numpy as np


class MACD:
	def __init__(self):
		pass

	@staticmethod
	def about_me():
		ret = {
			'required_fields':
				{
					'Fast Length':
						{
							'min': 1,
							'max': 200,
						},
					'Slow Length':
						{
							'min': 1,
							'max': 200,
						},
					'Signal Length':
						{
							'min': 1,
							'max': 200,
						},
				},
			'colors':
				[
					'MACD',
					'MACD Signal',
					'Histogram'
				]
		}
		return ret

	def calc_output_len(self, data_len, params):
		fast_len = params['Fast Length']
		slow_len = params['Slow Length']
		signal_len = params['Signal Length']
		ema_fast_len = data_len - fast_len + 1
		ema_slow_len = data_len - slow_len + 1
		macd_len = min(ema_fast_len, ema_slow_len)
		macd_signal_len = macd_len - signal_len + 1
		histogram_len = macd_signal_len
		return [macd_len, macd_signal_len, histogram_len]

	def _calc_ema(self, data, period):
		sf = 2 / (period + 1)
		ema = np.ones((data.shape[0] - period + 1, data.shape[1]), dtype=np.float32)
		ema[0] = np.sum(data[0: period], axis=0) / np.float32(period)
		for x in range(1, ema.shape[0]):
			ema[x] = (data[x + period - 1] - ema[x - 1]) * sf + ema[x - 1]
		return ema

	def calc(self, df, symbols, params):
		fast_len = params['Fast Length']
		slow_len = params['Slow Length']
		signal_len = params['Signal Length']
		column_names = sum([[symbol + column for column in ['-Close-price']] for symbol in symbols], [])
		data = df[column_names].values.astype(np.float32)

		ema_fast = self._calc_ema(data, fast_len)
		ema_slow = self._calc_ema(data, slow_len)
		if ema_fast.shape[0] > ema_slow.shape[0]:
			macd = ema_fast[-ema_slow.shape[0]:] - ema_slow
		elif ema_fast.shape[0] < ema_slow.shape[0]:
			macd = ema_fast - ema_slow[-ema_fast.shape[0]:]
		else:
			macd = ema_fast - ema_slow
		macd_signal = self._calc_ema(macd, signal_len)
		histogram = macd[-macd_signal.shape[0]:] - macd_signal

		return macd, macd_signal, histogram
		#return np.concatenate((np.expand_dims(macd, axis=-1), np.expand_dims(macd_signal, axis=-1), np.expand_dims(histogram, axis=-1)), axis=-1)
