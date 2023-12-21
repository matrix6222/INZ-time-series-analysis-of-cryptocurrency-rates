import numpy as np


class KDJ:
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
					'Color K',
					'Color D',
					'Color J',
				]
		}
		return ret

	def calc_output_len(self, data_len, params):
		period = params['Period']
		return [data_len - period + 1]

	def _calc_hlc(self, high, low, close, period):
		ret = []
		for x in range(close.shape[0] - period + 1):
			lowest = low[x: x + period].min(axis=0)
			highest = high[x: x + period].max(axis=0)
			c = close[x + period - 1]
			ret.append([highest, lowest, c])
		return np.array(ret, dtype=np.float32)


	def calc(self, df, symbols, params):
		period = params['Period']
		smooth_k = params['Smooth K']
		smooth_d = params['Smooth D']
		column_names_high = sum([[symbol + column for column in ['-High-price']] for symbol in symbols], [])
		column_names_low = sum([[symbol + column for column in ['-Low-price']] for symbol in symbols], [])
		column_names_close = sum([[symbol + column for column in ['-Close-price']] for symbol in symbols], [])
		high = df[column_names_high].values.astype(np.float32)
		low = df[column_names_low].values.astype(np.float32)
		close = df[column_names_close].values.astype(np.float32)

		hlc = self._calc_hlc(high, low, close, period)
		h, l, c = hlc[:, 0, :], hlc[:, 1, :], hlc[:, 2, :]
		rsv = 100 * ((c - l) / np.where(h == l, 0.0000000000001, h - l))

		k = np.zeros(rsv.shape, dtype=np.float32)
		d = np.zeros(rsv.shape, dtype=np.float32)
		k[0] = ((smooth_k - 1) * np.full(rsv.shape[1], 50, dtype=np.float32) + rsv[0]) / smooth_k
		d[0] = ((smooth_d - 1) * np.full(rsv.shape[1], 50, dtype=np.float32) + k[0]) / smooth_d
		for x in range(1, rsv.shape[0]):
			k[x] = ((smooth_k - 1) * k[x - 1] + rsv[x]) / smooth_k
			d[x] = ((smooth_d - 1) * d[x - 1] + k[x]) / smooth_d
		j = 3 * k - 2 * d

		return k, d, j
		#return np.concatenate((np.expand_dims(k, axis=-1), np.expand_dims(d, axis=-1), np.expand_dims(j, axis=-1)), axis=-1)

