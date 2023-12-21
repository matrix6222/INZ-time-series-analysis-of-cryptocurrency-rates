import tkinter as tk


class AnalyseCheckBoxList(tk.Frame):
	def __init__(self, root):
		tk.Frame.__init__(self, root)

		self.names = []
		self.active = []

		self.items = tk.Frame(self)
		self.items.pack()

	def get_active_names(self):
		return [self.names[x] for x in range(len(self.names)) if self.active[x].get() == 1]

	def refresh(self):
		self.items.destroy()
		self.items = tk.Frame(self)
		for x, name in enumerate(self.names):
			tk.Checkbutton(self.items, text=name, variable=self.active[x]).pack()
		self.items.pack()
		self.pack()

	def add_checkbox(self, name):
		self.names.append(name)
		self.active.append(tk.IntVar(value=1))
		self.refresh()

	def remove_checkbox(self, name):
		if name in self.names:
			idx = self.names.index(name)
			self.names.pop(idx)
			self.active.pop(idx)
			self.refresh()
