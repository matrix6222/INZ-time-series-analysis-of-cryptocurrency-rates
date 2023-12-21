import tkinter as tk


class MessageBox(tk.Toplevel):
	def __init__(self, root, title, lines):
		tk.Toplevel.__init__(self, root)
		self.title(title)

		for line in lines:
			tk.Label(self, text=line).pack(padx=5)
		tk.Button(self, text="OK", command=self.on_close).pack(pady=5, padx=5)

	def on_close(self):
		self.destroy()
