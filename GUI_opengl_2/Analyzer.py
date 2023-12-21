from Analyzers.SMA import SMA
from Analyzers.EMA import EMA
from Analyzers.WMA import WMA
from Analyzers.VWAP import VWAP
from Analyzers.TRIX import TRIX
from Analyzers.MACD import MACD
from Analyzers.RSI import RSI
from Analyzers.MFI import MFI
from Analyzers.KDJ import KDJ
from Analyzers.StochRSI import StochRSI


class Analyzer:
	def __init__(self, locks, expected_data_len):
		self.locks = locks
		self.expected_data_len = expected_data_len
		self.minimum_output_len = 500

		self.analyzers = {}
		self.analyzers['SMA'] = SMA.about_me()
		self.analyzers['EMA'] = EMA.about_me()
		self.analyzers['WMA'] = WMA.about_me()
		self.analyzers['VWAP'] = VWAP.about_me()
		self.analyzers['TRIX'] = TRIX.about_me()
		self.analyzers['MACD'] = MACD.about_me()
		self.analyzers['RSI'] = RSI.about_me()
		self.analyzers['MFI'] = MFI.about_me()
		self.analyzers['KDJ'] = KDJ.about_me()
		self.analyzers['StochRSI'] = StochRSI.about_me()
		self.analyzers['SMA']['object'] = SMA()
		self.analyzers['EMA']['object'] = EMA()
		self.analyzers['WMA']['object'] = WMA()
		self.analyzers['VWAP']['object'] = VWAP()
		self.analyzers['TRIX']['object'] = TRIX()
		self.analyzers['MACD']['object'] = MACD()
		self.analyzers['RSI']['object'] = RSI()
		self.analyzers['MFI']['object'] = MFI()
		self.analyzers['KDJ']['object'] = KDJ()
		self.analyzers['StochRSI']['object'] = StochRSI()

		#print(self.analyzers)

		# type, name, colors, params
		self.analysis = []

		# type, name, colors, timestamp, data
		self.data = []

	def remove_analysis(self, name):
		with self.locks['analyzer_analysis']:
			names = [row[1] for row in self.analysis]
		if name not in names:
			return ['This name does not exist']
		idx = names.index(name)
		with self.locks['analyzer_analysis']:
			self.analysis.pop(idx)
		return []

	def _color_check(self, color):
		if len(color) != 7:
			return False
		if color[0] != '#':
			return False
		for char in color[1:]:
			if char not in '0123456789ABCDEF':
				return False
		return True

	def _list_of_colors_check(self, colors):
		for color in colors:
			if not isinstance(color, str):
				return False
			if not self._color_check(color):
				return False
		return True

	def _all_keys_in_dict(self, keys, dictionary):
		dict_keys = list(dictionary.keys())
		for key in keys:
			if key not in dict_keys:
				return False
		return True

	def _all_items_are_decimal_string(self, keys, dictionary):
		for key in keys:
			if not dictionary[key].isdecimal():
				return False
		return True

	def _check_params(self, params, required_fields, minimum_values, maximum_values):
		errors = []
		if not self._all_keys_in_dict(required_fields, params):
			errors.append('Missing required fields: {}'.format(','.join(required_fields)))
		else:
			if not self._all_items_are_decimal_string(required_fields, params):
				errors.append('Each field must be a decimal string')
			else:
				for x, key in enumerate(required_fields):
					value = int(params[key])
					if not minimum_values[x] <= value <= maximum_values[x]:
						errors.append('The value of the "{}" field must be in the range [{}; {}]'.format(key, minimum_values[x], maximum_values[x]))
		return errors

	def add_analysis(self, type, name, colors, params):
		errors = []
		if not isinstance(type, str):
			errors.append("Type must be a string")
		if not isinstance(name, str):
			errors.append("Name must be a string")
		if not isinstance(colors, list):
			errors.append("Colors must be a list")
		if not isinstance(params, dict):
			errors.append("Params must be a dictionary")
		if len(errors) > 0:
			return errors

		if sum([0 if isinstance(item, str) else 1 for item in colors]) > 0:
			errors.append('All elements of the color list must be a string')
		if sum([0 if isinstance(value, str) else 1 for key, value in params.items()]) > 0:
			errors.append('All values of the params field must be a string')
		if len(errors) > 0:
			return errors

		colors = [color.upper() for color in colors]
		if not self._list_of_colors_check(colors):
			errors.append("Invalid colors")
		if len(errors) > 0:
			return errors

		with self.locks['analyzer_analysis']:
			analysis = self.analysis.copy()
		with self.locks['analyzer_analyzers']:
			analyzers = self.analyzers.copy()

		names = [row[1] for row in analysis]
		if name in names:
			errors.append("This name is already occupied")
		if not 3 <= len(name) <= 15:
			errors.append('The length of the name must be in the range of [3; 15]')
		if type not in analyzers.keys():
			errors.append("Invalid type of analysis")
		if len(errors) > 0:
			return errors

		required_fields = list(analyzers[type]['required_fields'].keys())
		minimum_values = [analyzers[type]['required_fields'][x]['min'] for x in required_fields]
		maximum_values = [analyzers[type]['required_fields'][x]['max'] for x in required_fields]

		errors = self._check_params(params, required_fields, minimum_values, maximum_values)
		if len(errors) > 0:
			return errors
		params = {key: int(params[key]) for key in required_fields}
		if min(analyzers[type]['object'].calc_output_len(self.expected_data_len, params)) < self.minimum_output_len:
			return ['Given values will create too short output']
		if params in [x[3] for x in analysis if x[0] == type]:
			return ['The given parameters already exist']

		with self.locks['analyzer_analysis']:
			self.analysis.append([type, name, colors, params])
		return []

	def update_analysis(self, dataFrame, symbols, callback_again):
		#print("START ANALYSIS !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
		if len(dataFrame) > 0:
			df_timestamp = dataFrame[symbols[0] + '-Kline-open-time'].iloc[-1]
			with self.locks['analyzer_analysis']:
				target_analysis = self.analysis.copy()
			with self.locks['analyzer_data']:
				done_analysis = self.data.copy()
			with self.locks['analyzer_analyzers']:
				analyzers = self.analyzers.copy()

			#print("============================================================")
			#print("target_analysis", df_timestamp)
			#for type, name, color, params in target_analysis:
			#	print('\t', type, name, color, params)
			#print("============================================================")
			#print("done_analysis")
			#for type, name, color, timestamp, data in done_analysis:
			#	print(type, name, color, timestamp)


			done_names = [row[1] for row in done_analysis]
			done_timestamps = [row[3] for row in done_analysis]
			to_analyse_idx = []
			ret = []
			for x, (type, name, color, params) in enumerate(target_analysis):
				if name not in done_names:
					to_analyse_idx.append(x)
				else:
					idx = done_names.index(name)
					done_timestamp = done_timestamps[idx]
					if done_timestamp != df_timestamp:
						to_analyse_idx.append(x)
					else:
						ret.append(done_analysis[idx])

			#print("============================================================")
			#print("to analyse")
			#for x in to_analyse_idx:
			#	print('\t', target_analysis[x])

			#print("============================================================")
			for x in to_analyse_idx:
				type, name, color, params = target_analysis[x]
				result = analyzers[type]['object'].calc(dataFrame, symbols, params)
				#print('\t', '\t', "calculated: ", [type, name, color, df_timestamp])
				ret.append([type, name, color, df_timestamp, result])

			with self.locks['analyzer_data']:
				self.data = ret

		callback_again(from_callback=True)


