import tkinter as tk
from tkinter import ttk
from tkinter.colorchooser import askcolor
from tkinter import filedialog
from MessageBox import MessageBox
from json import loads, dumps


class AddAnalyseForm(tk.Toplevel):
	def __init__(self, root, add_analyse_callback, get_all_analyse_callback, analyzers_configuration):
		tk.Toplevel.__init__(self, root)
		self.add_analyse_callback = add_analyse_callback
		self.get_all_analyse_callback = get_all_analyse_callback
		self.analyzers_configuration = analyzers_configuration
		self.geometry("500x600")
		self.title("New Window")

		self.left_frame = ttk.Frame(self)
		self.left_frame.pack(side=tk.LEFT, fill=tk.Y)

		self.right_frame = ttk.Frame(self)
		self.right_frame.pack(side=tk.LEFT, fill=tk.Y)

		self.bottom_frame = tk.Frame(self)
		self.bottom_frame.pack(side=tk.BOTTOM, fill=tk.X)

		self.name_field = tk.Entry(self.right_frame)
		self.param_fields = {}
		self.button_fields = {}
		self.color_fields = {}

		tk.Button(self.bottom_frame, text="Add", command=self.on_add).pack(side=tk.RIGHT, padx=5, pady=5)
		tk.Button(self.bottom_frame, text="Save", command=self.on_save).pack(side=tk.LEFT, padx=5, pady=5)
		tk.Button(self.bottom_frame, text="Load", command=self.on_load).pack(side=tk.LEFT, padx=5, pady=5)

		tk.Label(self.left_frame, text="Select Analysis").pack()
		self.items = list(self.analyzers_configuration.keys())
		self.lb = tk.Listbox(self.left_frame, selectmode=tk.SINGLE)
		for x, item in enumerate(self.items):
			self.lb.insert(x, item)
		self.lb.pack()
		self.lb.bind("<<ListboxSelect>>", self.on_select)

		self.default_color = "#FF0000"
		self.selected = ''

	def on_save(self):
		file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
		if file_path:
			data = self.get_all_analyse_callback()
			json = dumps({'config': [{'type': d[0], 'name': d[1], 'colors': d[2], 'params': {key: str(value) for key, value in d[3].items()}} for d in data]})
			with open(file_path, 'w') as file:
				file.write(json)

	def on_load(self):
		file_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
		if file_path:
			with open(file_path, 'r') as file:
				data = file.read()

			try:
				json = loads(data)
			except:
				MessageBox(self, 'Error', ['Invalid json'])
				return None

			if 'config' not in json.keys():
				MessageBox(self, 'Error', ['Missing "config" field in json file'])
				return None
			arr = json['config']
			if not isinstance(arr, list):
				MessageBox(self, 'Error', ['The "config" field is not a list'])
				return None
			for row in arr:
				# row = {"type": "SMA", "name": "qwe", "colors": ["#FF0000"], "params": {"period": "20"}}
				if isinstance(row, dict):
					keys = row.keys()
					if 'type' in keys and 'name' in keys and 'colors' in keys and 'params' in keys:
						row_type = row['type']
						row_name = row['name']
						row_color = row['colors']
						row_params = row['params']
						result = self.add_analyse_callback(row_type, row_name, row_color, row_params)
						if result != []:
							MessageBox(self, "Error {}".format(row_name), result)
					else:
						MessageBox(self, 'Error', ['Missing fields'])
				else:
					MessageBox(self, 'Error', ['List item is not a dictionary'])

	def on_add(self):
		if self.selected in self.items:
			configuration = self.analyzers_configuration[self.selected]
			params = list(configuration['required_fields'].keys())
			colors = configuration['colors']
			name = self.name_field.get()
			params_values = {param: self.param_fields[param].get() for param in params}
			colors_values = [self.color_fields[color] for color in colors]
			print(self.selected, name, colors_values, params_values)
			result = self.add_analyse_callback(self.selected, name, colors_values, params_values)
			if result != []:
				MessageBox(self, 'Error', result)

	def on_select(self, event):
		idx = self.lb.curselection()
		if len(idx) == 1:
			idx = idx[0]
			self.selected = self.items[idx]
			self.right_frame.destroy()
			self.right_frame = tk.Frame(self)

			if self.selected in self.items:
				configuration = self.analyzers_configuration[self.selected]
				params = list(configuration['required_fields'].keys())
				colors = configuration['colors']

				tk.Label(self.right_frame, text='Configure {}'.format(self.selected)).grid(row=0, column=0)

				tk.Label(self.right_frame, text="Name").grid(row=1, column=0)
				self.name_field = tk.Entry(self.right_frame)
				self.name_field.grid(row=1, column=1)

				for x, param in enumerate(params):
					tk.Label(self.right_frame, text=param).grid(row=x + 2, column=0)
					self.param_fields[param] = tk.Entry(self.right_frame)
					self.param_fields[param].grid(row=x + 2, column=1)

				for x, color in enumerate(colors):
					self.color_fields[color] = self.default_color
					tk.Label(self.right_frame, text=color).grid(row=x + 2 + len(params), column=0)
					self.button_fields[color] = tk.Button(self.right_frame, text="   ", bg=self.default_color, activebackground=self.default_color, command=lambda color_arg=color: self.chose_color(color_arg))
					self.button_fields[color].grid(row=x + 2 + len(params), column=1)

				self.right_frame.pack(side=tk.LEFT, fill=tk.Y)

	def chose_color(self, color):
		c = askcolor(title="Color Chooser")[1]
		self.color_fields[color] = c if c is not None else self.default_color
		self.button_fields[color].configure(bg=self.color_fields[color], activebackground=self.color_fields[color])
