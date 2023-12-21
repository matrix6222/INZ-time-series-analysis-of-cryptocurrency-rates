import tkinter as tk


class FoldingMenu(tk.Frame):
	def __init__(self, root, name):
		tk.Frame.__init__(self, root)

		self.items_pad_x = 10
		self.items_pad_y = 10

		self.arrowDown = tk.PhotoImage(data="R0lGODlhEAAQAKIAAP///9TQyICAgEBAQAAAAAAAAAAAAAAAACwAAAAAEAAQAAADNhi63BMgyinFAy0HC3Xj2EJoIEOM32WeaSeeqFK+say+2azUi+5ttx/QJeQIjshkcsBsOp/MBAA7")
		self.arrowRight = tk.PhotoImage(data="R0lGODlhEAAQAKIAAP///9TQyICAgEBAQAAAAAAAAAAAAAAAACwAAAAAEAAQAAADMxi63BMgyinFAy0HC3XjmLeA4ngpRKoSZoeuDLmo38mwtVvKu93rIo5gSCwWB8ikcolMAAA7")

		self.is_collapsed = False

		self.container = tk.Frame(self, borderwidth=2, height=16, relief=tk.GROOVE)
		self.container.pack(fill=tk.X, pady=9, padx=7)

		self.arrow_button = tk.Label(self, borderwidth=0, image=self.arrowDown)
		self.arrow_button.place(in_=self.container, x=5, y=-8, bordermode="ignore")
		self.arrow_button.bind("<Button-1>", self.toggle)

		self.title = tk.Label(self, borderwidth=1, text=name)
		self.title.place(in_=self.container, x=26, y=-9, bordermode="ignore")

		self.items = tk.Frame(self.container)

	def toggle(self, event):
		if self.is_collapsed:
			self.items.pack_forget()
			self.container.configure(height=16)
			self.arrow_button.configure(image=self.arrowDown)
			self.is_collapsed = False
		else:
			self.items.pack(fill=tk.X, padx=self.items_pad_x, pady=self.items_pad_y)
			self.arrow_button.configure(image=self.arrowRight)
			self.is_collapsed = True
