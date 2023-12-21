import tkinter as tk
from MessageBox import MessageBox


class RemoveAnalyseForm(tk.Toplevel):
	def __init__(self, root, names, remove_callback):
		self.remove_callback = remove_callback
		self.names = names
		self.selected = ''

		tk.Toplevel.__init__(self, root)
		self.geometry("500x600")
		self.title("New Window")

		self.frame = tk.Frame(self)
		self.frame.pack(side=tk.LEFT, fill=tk.Y)

		self.bottom_frame = tk.Frame(self)
		self.bottom_frame.pack(side=tk.BOTTOM, fill=tk.X)

		tk.Button(self.bottom_frame, text="Remove", command=self.on_remove).pack(side=tk.RIGHT, padx=5, pady=5)

		tk.Label(self.frame, text="Select").pack()
		self.lb = tk.Listbox(self.frame, selectmode=tk.SINGLE)
		for x, name in enumerate(self.names):
			self.lb.insert(x, name)
		self.lb.pack()
		self.lb.bind("<<ListboxSelect>>", self.on_select)

	def on_remove(self):
		if self.selected != '' and self.selected in self.names:
			result = self.remove_callback(self.selected)
			if result == []:
				self.names.remove(self.selected)

				self.frame.destroy()
				self.frame = tk.Frame(self)
				tk.Label(self.frame, text="Select").pack()
				self.lb = tk.Listbox(self.frame, selectmode=tk.SINGLE)
				for x, name in enumerate(self.names):
					self.lb.insert(x, name)
				self.lb.pack()
				self.lb.bind("<<ListboxSelect>>", self.on_select)
				self.frame.pack(side=tk.LEFT, fill=tk.Y)
			else:
				MessageBox(self, "Error", result)

	def on_select(self, event):
		idx = self.lb.curselection()
		if len(idx) == 1:
			idx = idx[0]
			self.selected = self.names[idx]
