import numpy as np


class VWAP:
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
		return [data_len]

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
		for x in range(1, typical_price.shape[0] + 1):
			typical_price_timeseries = typical_price[x - period if x - period > 0 else 0: x]
			volume_btc_timeseries = volume[x - period if x - period > 0 else 0: x]
			volume_btc_timeseries_sum = np.sum(volume_btc_timeseries, axis=0)
			ret.append(np.sum(typical_price_timeseries * volume_btc_timeseries, axis=0) / np.where(volume_btc_timeseries_sum == 0.0, 0.00000001, volume_btc_timeseries_sum))
		return np.array(ret, dtype=np.float32)

		#return ret.reshape((ret.shape[0], ret.shape[1], 1))
