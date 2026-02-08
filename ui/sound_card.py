import tkinter as tk
from ui.theme import *

class SoundCard(tk.Frame):
    def __init__(self, parent, name, manager, config, refresh):
        super().__init__(parent, bg=PANEL, padx=10, pady=10)

        self.name = name
        self.manager = manager
        self.config = config
        self.refresh = refresh

        top = tk.Frame(self, bg=PANEL)
        top.pack(fill="x")

        tk.Button(
            top, text=name, bg=ACCENT, fg=TEXT,
            command=self.toggle, relief="flat"
        ).pack(side="left", fill="x", expand=True)

        tk.Button(
            top, text="🗑", bg=DANGER, fg="white",
            command=self.delete, relief="flat"
        ).pack(side="right")

        self.slider = tk.Scale(
            self, from_=0, to=2, resolution=0.01,
            orient="horizontal", bg=PANEL, fg=TEXT,
            highlightthickness=0, troughcolor=BTN
        )
        self.slider.set(manager.sounds[name]["volume"])
        self.slider.pack(fill="x")

        self.slider.config(command=self.set_volume)

    def toggle(self):
        self.manager.toggle(self.name)
        self.refresh()

    def delete(self):
        self.manager.remove(self.name)
        self.refresh()

    def set_volume(self, val):
        v = float(val)
        self.manager.sounds[self.name]["volume"] = v
        self.config["volumes"][self.name] = v