from threading import Thread, Lock
from tkinter import ttk
import tkinter as tk
import asyncio
from GraphDrawer import GraphDrawer
from Data import Data

from AddAnalyseForm import AddAnalyseForm
from RemoveAnaliseForm import RemoveAnalyseForm
from Analyzer import Analyzer
from AnalyseCheckBoxList import AnalyseCheckBoxList


class GUI:
	def __init__(self):
		self.timeseries_past = 1000
		self.interval_ms = 60_000
		self.locks = {'data_past': Lock(), 'analyzer_analysis': Lock(), 'analyzer_data': Lock(), 'analyzer_status': Lock(), 'analyzer_analyzers': Lock()}
		self.symbols = ['BTCEUR', 'LTCEUR', 'ETHEUR']
		self.data = Data(self.symbols, self.interval_ms, self.timeseries_past, self.locks)

		loop = asyncio.get_event_loop()
		self.data_past_thread = Thread(target=self.data.run, args=(loop, self.process_new_data, ), daemon=True)
		self.data_past_thread.start()

		self.wnd = tk.Tk()
		self.wnd.geometry('1000x800')
		self.wnd.title('xdd')

		self.main_frame = ttk.Frame(self.wnd)
		self.main_frame.pack(fill=tk.BOTH, expand=True)

		self.canvas = GraphDrawer(self.main_frame)

		self.right_frame = tk.Frame(self.main_frame, width=300)
		self.right_frame.pack(side=tk.RIGHT, fill=tk.BOTH)

		self.selected_symbol = self.symbols[0]
		self.selector = ttk.Combobox(self.right_frame, values=self.symbols)
		self.selector.set(self.selected_symbol)
		self.selector.bind('<<ComboboxSelected>>', self.selector_select)
		self.selector.pack()

		self.analyzer = Analyzer(self.locks, self.timeseries_past)
		self.analyzer_status = {'working': False, 'analyse_again': False}

		self.add_analyse_form_is_opened = None
		self.remove_analyse_form_is_opened = None
		tk.Button(self.right_frame, text="Add Analyse", command=self.add_analyse_form).pack()
		tk.Button(self.right_frame, text="Remove Analyse", command=self.remove_analyse_form).pack()

		self.analysis_frame = AnalyseCheckBoxList(self.right_frame)

		self.frame_time = 16
		self.wnd.after(0, self.draw_canvas)
		self.wnd.mainloop()

	def get_all_analyse(self):
		with self.locks['analyzer_analysis']:
			ret = self.analyzer.analysis.copy()
		return ret

	def add_analyse_form(self):
		if self.add_analyse_form_is_opened is None or not self.add_analyse_form_is_opened.winfo_exists():
			with self.locks['analyzer_analyzers']:
				analyzers = self.analyzer.analyzers.copy()
			self.add_analyse_form_is_opened = AddAnalyseForm(self.wnd, self.add_analyse, self.get_all_analyse, analyzers)

	def remove_analyse_form(self):
		if self.remove_analyse_form_is_opened is None or not self.remove_analyse_form_is_opened.winfo_exists():
			with self.locks['analyzer_analysis']:
				names = [row[1] for row in self.analyzer.analysis]
			self.remove_analyse_form_is_opened = RemoveAnalyseForm(self.wnd, names, self.remove_analyse)

	def draw_canvas(self):
		with self.locks['data_past']:
			df = self.data.data_past.copy()
		with self.locks['analyzer_data']:
			analysis = self.analyzer.data.copy()
		#self.canvas.redraw(df, self.selected_symbol, self.symbols, analysis, self.analysis_frame.get_active_names())
		self.canvas.redraw2(df, self.selected_symbol, self.symbols, analysis, self.analysis_frame.get_active_names())
		self.wnd.after(self.frame_time, self.draw_canvas)

	def selector_select(self, event):
		self.selected_symbol = self.selector.get()

	def remove_analyse(self, name):
		result = self.analyzer.remove_analysis(name)
		if result == []:
			self.analysis_frame.remove_checkbox(name)
			self.run_analyser()
		return result

	def add_analyse(self, type, name, color, parameters):
		result = self.analyzer.add_analysis(type, name, color, parameters)
		if result == []:
			self.analysis_frame.add_checkbox(name)
			self.run_analyser()
		return result

	def process_new_data(self):
		print("New data arrived")
		self.run_analyser()

	def run_analyser(self, from_callback=False):
		with self.locks['analyzer_status']:
			if from_callback == False:
				if self.analyzer_status['working'] == False and self.analyzer_status['analyse_again'] == False:
					self.analyzer_status['working'] = True
					with self.locks['data_past']:
						df = self.data.data_past.copy()
					Thread(target=self.analyzer.update_analysis, args=(df, self.symbols, self.run_analyser, ), daemon=True).start()
				elif self.analyzer_status['working'] == True and self.analyzer_status['analyse_again'] == False:
					self.analyzer_status['analyse_again'] = True
				elif self.analyzer_status['working'] == True and self.analyzer_status['analyse_again'] == True:
					pass
				elif self.analyzer_status['working'] == False and self.analyzer_status['analyse_again'] == True:
					self.analyzer_status['working'] = True
					self.analyzer_status['analyse_again'] = False
					with self.locks['data_past']:
						df = self.data.data_past.copy()
					Thread(target=self.analyzer.update_analysis, args=(df, self.symbols, self.run_analyser,), daemon=True).start()
			elif from_callback == True:
				if self.analyzer_status['working'] == False and self.analyzer_status['analyse_again'] == False:
					pass
				elif self.analyzer_status['working'] == True and self.analyzer_status['analyse_again'] == False:
					self.analyzer_status['working'] = False
				elif self.analyzer_status['working'] == True and self.analyzer_status['analyse_again'] == True:
					self.analyzer_status['analyse_again'] = False
					with self.locks['data_past']:
						df = self.data.data_past.copy()
					Thread(target=self.analyzer.update_analysis, args=(df, self.symbols, self.run_analyser,), daemon=True).start()
				elif self.analyzer_status['working'] == False and self.analyzer_status['analyse_again'] == True:
					self.analyzer_status['working'] = True
					self.analyzer_status['analyse_again'] = False
					with self.locks['data_past']:
						df = self.data.data_past.copy()
					Thread(target=self.analyzer.update_analysis, args=(df, self.symbols, self.run_analyser,), daemon=True).start()
