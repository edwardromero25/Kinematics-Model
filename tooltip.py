import tkinter as tk

class Tooltip:
    def __init__(self, widget, text, x_offset, y_offset):
        self.widget = widget
        self.text = text
        self.x_offset = x_offset
        self.y_offset = y_offset
        self.tip_window = None
        self.widget.bind("<Enter>", self.show_tooltip)
        self.widget.bind("<Leave>", self.hide_tooltip)

    def show_tooltip(self, event):
        if self.tip_window or not self.text:
            return

        x, y, _, _ = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + self.x_offset
        y += self.widget.winfo_rooty() + self.y_offset

        self.tip_window = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")

        label = tk.Label(
            tw,
            text=self.text,
            justify=tk.LEFT,
            background="SystemButtonFace",
            relief=tk.SOLID,
            borderwidth=1
        )
        label.pack(ipadx=1)

    def hide_tooltip(self, event):
        if self.tip_window:
            self.tip_window.destroy()
            self.tip_window = None