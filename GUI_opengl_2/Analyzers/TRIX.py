import numpy as np


class TRIX:
	def __init__(self):
		pass

	@staticmethod
	def about_me():
		ret = {
			'required_fields':
				{
					'Period':
						{
							'min': 1,
							'max': 200,
						},
				},
			'colors':
				[
					'Color'
				]
		}
		return ret

	def calc_output_len(self, data_len, params):
		period = params['Period']
		return [data_len - 3 * period + 3]

	def _calc_ema(self, data, period):
		sf = 2 / (period + 1)
		ema = np.ones((data.shape[0] - period + 1, data.shape[1]), dtype=np.float32)
		ema[0] = np.sum(data[0: period], axis=0) / np.float32(period)
		for x in range(1, ema.shape[0]):
			ema[x] = (data[x + period - 1] - ema[x - 1]) * sf + ema[x - 1]
		return ema

	def calc(self, df, symbols, params):
		period = params['Period']
		# can be extended to period_EMA1, period_EMA2 and period_EMA3
		column_names = sum([[symbol + column for column in ['-Close-price']] for symbol in symbols], [])
		data = df[column_names].values.astype(np.float32)

		return self._calc_ema(self._calc_ema(self._calc_ema(data, period), period), period)

		#return trix.reshape((trix.shape[0], trix.shape[1], 1))
