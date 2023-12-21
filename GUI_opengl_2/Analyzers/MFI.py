import numpy as np


class MFI:
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
		return [data_len - 1]

	def calc(self, df, symbols, params):
		period = params['Period']
		column_names_high = sum([[symbol + column for column in ['-High-price']] for symbol in symbols], [])
		column_names_low = sum([[symbol + column for column in ['-Low-price']] for symbol in symbols], [])
		column_names_close = sum([[symbol + column for column in ['-Close-price']] for symbol in symbols], [])
		column_names_volume = sum([[symbol + column for column in ['-Volume']] for symbol in symbols], [])
		high = df[column_names_high].values.astype(np.float32)
		low = df[column_names_low].values.astype(np.float32)
		close = df[column_names_close].values.astype(np.float32)
		volume = df[column_names_volume].values.astype(np.float32)

		ret = []
		typical_price = (high + low + close) / np.float32(3)
		delta = typical_price[1:] - typical_price[:-1]
		raw_money_flow = typical_price * volume
		positive_money_flow = np.where(delta > 0, raw_money_flow[1:], 0)
		negative_money_flow = np.where(delta < 0, raw_money_flow[1:], 0)

		for x in range(1, delta.shape[0] + 1):
			gain = np.sum(positive_money_flow[x - period if x - period > 0 else 0: x], axis=0)
			loss = np.sum(negative_money_flow[x - period if x - period > 0 else 0: x], axis=0)
			loss = np.where(loss != 0.0, loss, 0.000000001)
			mfi = 100 - (100 / (1 + (gain / loss)))
			ret.append(mfi)
		return np.array(ret, dtype=np.float32)

		#return ret.reshape((ret.shape[0], ret.shape[1], 1))
