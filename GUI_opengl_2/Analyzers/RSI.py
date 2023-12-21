import numpy as np


class RSI:
	def __init__(self):
		pass

	@staticmethod
	def about_me():
		ret = {
			'required_fields':
				{
					'Period':
						{
							'min': 2,
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
		return [data_len - period]

	def calc(self, df, symbols, params):
		period = params['Period']
		column_names = sum([[symbol + column for column in ['-Close-price']] for symbol in symbols], [])
		data = df[column_names].values.astype(np.float32)

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

		#return rsi.reshape((rsi.shape[0], rsi.shape[1], 1))
