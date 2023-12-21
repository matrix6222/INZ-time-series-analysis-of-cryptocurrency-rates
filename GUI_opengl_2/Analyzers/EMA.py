import numpy as np


class EMA:
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
		return [data_len - period + 1]

	def calc(self, df, symbols, params):
		period = params['Period']
		column_names = sum([[symbol + column for column in ['-Close-price']] for symbol in symbols], [])
		data = df[column_names].values.astype(np.float32)

		sf = 2 / (period + 1)
		ema = np.ones((data.shape[0] - period + 1, data.shape[1]), dtype=np.float32)
		ema[0] = np.sum(data[0: period], axis=0) / np.float32(period)
		for x in range(1, ema.shape[0]):
			ema[x] = (data[x + period - 1] - ema[x - 1]) * sf + ema[x - 1]
		return ema

		#return ema.reshape((ema.shape[0], ema.shape[1], 1))
