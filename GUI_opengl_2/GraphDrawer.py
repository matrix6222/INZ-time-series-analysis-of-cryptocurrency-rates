from ctypes import CDLL, c_uint64, c_uint32
import tkinter as tk
import numpy as np
from time import time

class GraphDrawer:
	def __init__(self, main_frame):
		self.dll = CDLL('./opengl_drawer.dll')
		self.dll.Initialize.argtypes = [c_uint64]
		self.dll.Destructor.argtypes = []
		self.dll.Redraw.argtypes = [c_uint32,  # int width,
									c_uint32,  # int height,

									c_uint32,  # int mouse_in_canvas,
									c_uint32,  # int mouse_x,
									c_uint32,  # int mouse_y,
									c_uint32,  # int size_x,

									c_uint32,  # int height_info,
									c_uint32,  # int height_timeline,
									c_uint32,  # int height_volumes,
									c_uint32,  # int height_graph_padding,
									c_uint32,  # int height_volumes_padding,
									c_uint32,  # int width_unknown,

									np.ctypeslib.ndpointer(dtype=np.float32, ndim=2, flags='C_CONTIGUOUS'),  # float* data,
									c_uint32,                                                                # int data_rows,

									c_uint64,                                                                # unsigned long long timestamp,

									c_uint32,                                                                # UINT32 analyse_config_rows,
									np.ctypeslib.ndpointer(dtype=np.uint32, ndim=2, flags='C_CONTIGUOUS'),   # UINT32* analyse_config,

									c_uint32,                                                                # UINT32 analyse_data_cols,
									np.ctypeslib.ndpointer(dtype=np.float32, ndim=2, flags='C_CONTIGUOUS')   # FLOAT* analyse_data,
									]
		'''
	#  UINT32 width,
    #  UINT32 height,

    #  UINT32 mouse_in_canvas,
    #  UINT32 mouse_x,
    #  UINT32 mouse_y,
    #  UINT32 size_x,

    #  UINT64 timestamp,

    #  FLOAT* data,
    #  UINT32 data_rows,

    #  UINT32 analyse1_config_rows,
    #  UINT32* analyse1_config,
    #  FLOAT* analyse1_data,

    #  UINT32 analyse2_config_rows,
    #  UINT32* analyse2_config,
    #  FLOAT* analyse2_data,

    #  UINT32 analyse3_config_rows,
    #  UINT32* analyse3_config,
    #  FLOAT* analyse3_data
		'''
		self.dll.Redraw2.argtypes = [
			c_uint32,                                                                # UINT32 width,
			c_uint32,                                                                # UINT32 height,

			c_uint32,                                                                # UINT32 mouse_in_canvas,
			c_uint32,                                                                # UINT32 mouse_x,
			c_uint32,                                                                # UINT32 mouse_y,
			c_uint32,                                                                # UINT32 size_x,

			c_uint64,                                                                # UINT64 timestamp,

			c_uint32,                                                                # UINT32 data_rows,
			np.ctypeslib.ndpointer(dtype=np.float32, ndim=2, flags='C_CONTIGUOUS'),  # FLOAT* data,

			c_uint32,                                                                # UINT32 analyse1_config_rows,
			np.ctypeslib.ndpointer(dtype=np.uint32, ndim=2, flags='C_CONTIGUOUS'),   # UINT32* analyse1_config,
			c_uint32,                                                                # UINT32 analyse1_config_cols,
			np.ctypeslib.ndpointer(dtype=np.float32, ndim=2, flags='C_CONTIGUOUS'),  # FLOAT* analyse1_data,

			c_uint32,                                                                # UINT32 analyse2_config_rows,
			np.ctypeslib.ndpointer(dtype=np.uint32, ndim=2, flags='C_CONTIGUOUS'),   # UINT32* analyse2_config,
			c_uint32,                                                                # UINT32 analyse2_config_cols,
			np.ctypeslib.ndpointer(dtype=np.float32, ndim=2, flags='C_CONTIGUOUS'),  # FLOAT* analyse2_data,

			c_uint32,                                                                # UINT32 analyse3_config_rows,
			np.ctypeslib.ndpointer(dtype=np.uint32, ndim=2, flags='C_CONTIGUOUS'),   # UINT32* analyse3_config,
			c_uint32,                                                                # UINT32 analyse4_config_cols,
			np.ctypeslib.ndpointer(dtype=np.float32, ndim=2, flags='C_CONTIGUOUS'),  # FLOAT* analyse3_data
		]

		self.canvas = tk.Canvas(main_frame, highlightthickness=0)
		self.canvas.bind("<MouseWheel>", self.mouse_canvas_scroll)
		self.canvas.bind("<Motion>", self.mouse_canvas_coordinates)
		self.canvas.bind("<Enter>", self.mouse_canvas_enter)
		self.canvas.bind("<Leave>", self.mouse_canvas_leave)
		self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

		self.mouse_x = 0
		self.mouse_y = 0
		self.mouse_in_canvas = 0
		self.mouse_scroll_min = 1
		self.mouse_scroll = 2
		self.mouse_scroll_max = 20
		self.mouse_scroll_scale = 5

		self.height_info = 100
		self.height_timeline = 10
		self.height_volumes = 200
		self.height_graph_padding = 10
		self.height_volumes_padding = 10
		self.width_unknown = 300

		self.dll.Initialize(self.canvas.winfo_id())

	def redraw(self, df, symbol, symbols, analysis, active_names):
		# t1 = time()
		width = self.canvas.winfo_width()
		height = self.canvas.winfo_height()
		column_names = [symbol + x for x in ['-Open-price', '-High-price', '-Low-price', '-Close-price', '-Volume', '-Taker-buy-base-asset-volume']]
		data = df[column_names].values.astype(np.float32).copy(order='C')
		timestamp = df[symbol + '-Kline-open-time'].iloc[-1] if len(data) > 0 else 0

		'''
		['SMA', 'qwe', ['#FF0000'], 1702177200000, array([[40930.43    ,    71.747   ,  2196.5103  ],
			[40930.09    ,    71.7465  ,  2196.4644  ],
			[40930.824   ,    71.75099 ,  2196.475   ],
			...,
			[40743.273   ,    72.00001 ,  2184.355   ],
			[40742.727   ,    71.985504,  2184.3474  ],
			[40742.33    ,    71.971504,  2184.3384  ]], dtype=float32)]
		'''

		idx = symbols.index(symbol)
		done_types = []
		done_names = []
		done_colors = []
		done_timestamp = []
		done_data = []
		for row in analysis:
			done_types.append(row[0])
			done_names.append(row[1])
			done_colors.append(row[2][0])
			done_timestamp.append(row[3])
			done_data.append(row[4][:, idx])
		type_to_int = {'SMA': 1, 'EMA': 2, 'WMA': 3, 'VWAP': 4, 'TRIX': 5}
		max_len = 0
		analyse_config = []  # type, len, color_r, color_g, color_b
		analyse_data = []
		for name in active_names:
			if name in done_names:
				idx = done_names.index(name)
				if timestamp == done_timestamp[idx]:
					config_type = type_to_int[done_types[idx]]
					config_len = len(done_data[idx])
					if config_len > max_len:
						max_len = config_len
					config_color_r, config_color_g, config_color_b = [int(x, 16) for x in [done_colors[idx][y:y+2] for y in range(1, 7, 2)]]
					analyse_config.append([config_type, config_len, config_color_r, config_color_g, config_color_b])
					analyse_data.append(done_data[idx])

		if len(analyse_config) == 0:
			analyse_config_to_draw = np.zeros((0, 0), dtype=np.uint32)
		else:
			analyse_config_to_draw = np.array(analyse_config, dtype=np.uint32)
		analyse_data_to_draw = np.zeros((len(analyse_data), max_len), dtype=np.float32)
		for x, sublist in enumerate(analyse_data):
			analyse_data_to_draw[x, :len(sublist)] = sublist





		self.dll.Redraw(
			width,
			height,

			self.mouse_in_canvas,
			self.mouse_x,
			self.mouse_y,
			self.mouse_scroll * self.mouse_scroll_scale,

			self.height_info,
			self.height_timeline,
			self.height_volumes,
			self.height_graph_padding,
			self.height_volumes_padding,
			self.width_unknown,

			data,
			data.shape[0],

			timestamp,

			analyse_config_to_draw.shape[0],
			analyse_config_to_draw,

			analyse_data_to_draw.shape[1],
			analyse_data_to_draw
		)

	def redraw2(self, df, symbol, symbols, analysis, active_names):
		width = self.canvas.winfo_width()
		height = self.canvas.winfo_height()
		column_names = [symbol + x for x in ['-Open-price', '-High-price', '-Low-price', '-Close-price', '-Volume', '-Taker-buy-base-asset-volume']]
		data = df[column_names].values.astype(np.float32).copy(order='C')
		timestamp = df[symbol + '-Kline-open-time'].iloc[-1] if len(data) > 0 else 0

		# extract all
		symbol_idx = symbols.index(symbol)
		done_types = []
		done_names = []
		done_colors = []
		done_timestamp = []
		done_data = []
		for row in analysis:
			done_types.append(row[0])
			done_names.append(row[1])
			done_colors.append(row[2])
			done_timestamp.append(row[3])
			done_data.append(row[4])  # [B, T, C] lub [K[B, T, C]20, D[B, T, C]15, J[B, T, C]10]

		# filter active and actual and group
		type_to_int = {'SMA': 1, 'EMA': 2, 'WMA': 3, 'VWAP': 4, 'TRIX': 5, 'RSI': 6, 'MFI': 7, 'StochRSI': 8, 'MACD': 9, 'KDJ': 10}
		type_to_group = {'SMA': 1, 'EMA': 1, 'WMA': 1, 'VWAP': 1, 'TRIX': 1, 'RSI': 1, 'MFI': 1, 'StochRSI': 2, 'MACD': 3, 'KDJ': 3}
		max_len1 = 0
		max_len2 = 0
		max_len3 = 0
		analyse1_config = []  # type, len,            color_r, color_g, color_b
		analyse2_config = []  # type, len, len,       color_r, color_g, color_b, color_r, color_g, color_b
		analyse3_config = []  # type, len, len, len,  color_r, color_g, color_b, color_r, color_g, color_b, color_r, color_g, color_b
		analyse1_data = []
		analyse2_data = []
		analyse3_data = []
		for name in active_names:
			if name in done_names:
				idx = done_names.index(name)
				if timestamp == done_timestamp[idx]:
					group = type_to_group[done_types[idx]]
					config_type = type_to_int[done_types[idx]]
					if group == 1:
						config_len = len(done_data[idx])
						if config_len > max_len1:
							max_len1 = config_len
						config_color_r, config_color_g, config_color_b = [int(x, 16) for x in [done_colors[idx][0][y:y + 2] for y in range(1, 7, 2)]]

						analyse1_config.append([config_type, config_len, config_color_r, config_color_g, config_color_b])
						analyse1_data.append(done_data[idx][:, symbol_idx])
					if group == 2:
						config_color1_r, config_color1_g, config_color1_b = [int(x, 16) for x in [done_colors[idx][0][y:y + 2] for y in range(1, 7, 2)]]
						config_color2_r, config_color2_g, config_color2_b = [int(x, 16) for x in [done_colors[idx][1][y:y + 2] for y in range(1, 7, 2)]]

						data1 = done_data[idx][0][:, symbol_idx]
						data2 = done_data[idx][1][:, symbol_idx]
						config_len1 = len(data1)
						config_len2 = len(data2)
						if max(config_len1, config_len2) > max_len2:
							max_len2 = max(config_len1, config_len2)

						analyse2_config.append([config_type, config_len1, config_len2, config_color1_r, config_color1_g, config_color1_b, config_color2_r, config_color2_g, config_color2_b])
						analyse2_data.append(data1)
						analyse2_data.append(data2)
					if group == 3:
						config_color1_r, config_color1_g, config_color1_b = [int(x, 16) for x in [done_colors[idx][0][y:y + 2] for y in range(1, 7, 2)]]
						config_color2_r, config_color2_g, config_color2_b = [int(x, 16) for x in [done_colors[idx][1][y:y + 2] for y in range(1, 7, 2)]]
						config_color3_r, config_color3_g, config_color3_b = [int(x, 16) for x in [done_colors[idx][2][y:y + 2] for y in range(1, 7, 2)]]

						data1 = done_data[idx][0][:, symbol_idx]
						data2 = done_data[idx][1][:, symbol_idx]
						data3 = done_data[idx][2][:, symbol_idx]
						config_len1 = len(data1)
						config_len2 = len(data2)
						config_len3 = len(data3)
						if max(config_len1, config_len2, config_len3) > max_len3:
							max_len3 = max(config_len1, config_len2, config_len3)

						analyse3_config.append([config_type, config_len1, config_len2, config_len3, config_color1_r, config_color1_g, config_color1_b, config_color2_r, config_color2_g, config_color2_b, config_color3_r, config_color3_g, config_color3_b])
						analyse3_data.append(data1)
						analyse3_data.append(data2)
						analyse3_data.append(data3)

		if len(analyse1_config) == 0:
			analyse1_config_to_draw = np.zeros((0, 0), dtype=np.uint32)
		else:
			analyse1_config_to_draw = np.array(analyse1_config, dtype=np.uint32)
		if len(analyse2_config) == 0:
			analyse2_config_to_draw = np.zeros((0, 0), dtype=np.uint32)
		else:
			analyse2_config_to_draw = np.array(analyse2_config, dtype=np.uint32)
		if len(analyse3_config) == 0:
			analyse3_config_to_draw = np.zeros((0, 0), dtype=np.uint32)
		else:
			analyse3_config_to_draw = np.array(analyse3_config, dtype=np.uint32)
		#print('an1config', analyse1_config)
		#print('an2config', analyse2_config)
		#print('an3config', analyse3_config)
		#print('an1data', analyse1_data)
		#print('an2data', analyse2_data)
		#print('an3data', analyse3_data)

		analyse1_data_to_draw = np.zeros((len(analyse1_data), max_len1), dtype=np.float32)
		analyse2_data_to_draw = np.zeros((len(analyse2_data), max_len2), dtype=np.float32)
		analyse3_data_to_draw = np.zeros((len(analyse3_data), max_len3), dtype=np.float32)
		for x, sublist in enumerate(analyse1_data):
			analyse1_data_to_draw[x, :len(sublist)] = sublist
		for x, sublist in enumerate(analyse2_data):
			analyse2_data_to_draw[x, :len(sublist)] = sublist
		for x, sublist in enumerate(analyse3_data):
			analyse3_data_to_draw[x, :len(sublist)] = sublist

		#analyse3_config_to_draw = np.array([[9, 3,4,5, 255,0,0, 0,255,0, 0,0,255]], dtype=np.uint32)cd GUI_
		#analyse3_data_to_draw = np.array([[1,2,-3,0,0], [10,11,12,13,0], [100, 101, 102, 103, 104]], dtype=np.float32)

		self.dll.Redraw2(
			width,
			height,

			self.mouse_in_canvas,
			self.mouse_x,
			self.mouse_y,
			self.mouse_scroll * self.mouse_scroll_scale,

			timestamp,

			data.shape[0],
			data,

			analyse1_config_to_draw.shape[0],
			analyse1_config_to_draw,
			analyse1_data_to_draw.shape[1],
			analyse1_data_to_draw,

			analyse2_config_to_draw.shape[0],
			analyse2_config_to_draw,
			analyse2_data_to_draw.shape[1],
			analyse2_data_to_draw,

			analyse3_config_to_draw.shape[0],
			analyse3_config_to_draw,
			analyse3_data_to_draw.shape[1],
			analyse3_data_to_draw
		)





	def mouse_canvas_coordinates(self, event):
		self.mouse_x, self.mouse_y = event.x, event.y

	def mouse_canvas_enter(self, event):
		self.mouse_in_canvas = 1

	def mouse_canvas_leave(self, event):
		self.mouse_in_canvas = 0

	def mouse_canvas_scroll(self, event):
		if event.delta < 0:
			self.mouse_scroll -= 1
			if self.mouse_scroll < self.mouse_scroll_min:
				self.mouse_scroll = self.mouse_scroll_min
		else:
			self.mouse_scroll += 1
			if self.mouse_scroll > self.mouse_scroll_max:
				self.mouse_scroll = self.mouse_scroll_max

	def __del__(self):
		self.dll.Destructor()
