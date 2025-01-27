# Copyright Tania Andersen 2025 @taniaandersen.bsky.social
# Licence: GNU AFFERO GENERAL PUBLIC LICENSE Version 3 https://www.gnu.org/licenses/agpl-3.0.en.html

import ctypes
import logging
import platform
import threading
import tkinter as tk
from tkinter import ttk, scrolledtext
import scrape

widget = {}
widget_list = []
PARENT = None

if platform.system() == "Windows":
    ctypes.windll.shcore.SetProcessDpiAwareness(1)

hyperlink = None

def sethyperlink(func):
    global hyperlink
    hyperlink = func


def get_widget_list():
    global widget_list
    return widget_list


def scrape_button_command():
    global PARENT
    values = {
        "pagination_url_template": widget["Pagination url"].get(),
        "first_page": int(widget["First page"].get()),
        "last_page": int(widget["Last page"].get()),
        "detail_url_selector": widget["Detail page selector"].get(),
        "login_url": widget["Login page"].get(),
        "headless": widget["Headless"].get(),
        "persistent_session": widget["With session"].get(),
        "success_tokens": [item.strip() for item in widget["Success tokens"].get().split(",") if item.strip()],
        "failure_tokens": [item.strip() for item in widget["Failure tokens"].get().split(",") if item.strip()],

        "speed": widget["Speed"].get(),
        "log_handler_emitter": log_to_text_field,
        "parent": PARENT,
        "log_file": "skreapper.log"
    }

    threading.Thread(target=lambda: (
        scrape.scrape(**values), logging.info("Scraping completed.")
    )).start()


def create_upper_frame(parent):
    global PARENT, widget_list
    PARENT = parent
    upper_frame = ttk.Frame(parent, padding="10", relief=tk.SUNKEN)
    upper_frame.columnconfigure(1, weight=1)
    for i in range(12):
        upper_frame.rowconfigure(i, weight=1)
    labels = [
        "Pagination url",
        "First page",
        "Last page",
        "Detail page selector"
    ]
    for i, label_text in enumerate(labels):
        label = ttk.Label(upper_frame, text=label_text, foreground="blue", cursor="hand2")
        label.grid(row=i, column=0, padx=10, pady=2, sticky="e")  # Right-align labels
        label.bind("<Button-1>", lambda event, text=label_text: hyperlink(event,text))
        entry = ttk.Entry(upper_frame)
        entry.grid(row=i, column=1, padx=10, pady=2, sticky="ew")
        widget[label_text] = entry
    style = ttk.Style()
    style.configure("Bold.TLabel", font=("TkDefaultFont", 9, "bold"))
    options_label = ttk.Label(upper_frame, text="Options", style="Bold.TLabel")
    options_label.grid(row=4, column=1, padx=10, pady=2, sticky="w")
    login_label = ttk.Label(upper_frame, text="Login/GDPR page", foreground="blue", cursor="hand2")
    login_label.grid(row=5, column=0, padx=10, pady=2, sticky="e")  # Right-align label
    login_label.bind("<Button-1>", lambda event, text="Login page": hyperlink(event,text))
    login_entry = ttk.Entry(upper_frame)
    login_entry.grid(row=5, column=1, padx=10, pady=2, sticky="ew")
    widget["Login page"] = login_entry
    save_session_label = ttk.Label(upper_frame, text="With session", foreground="blue", cursor="hand2")
    save_session_label.grid(row=6, column=0, padx=10, pady=2, sticky="e")
    save_session_label.bind("<Button-1>", lambda event, text="With session": hyperlink(event,text))
    headless_label = ttk.Label(upper_frame, text="Headless", foreground="blue", cursor="hand2")
    headless_label.grid(row=7, column=0, padx=10, pady=2, sticky="e")
    headless_label.bind("<Button-1>", lambda event, text="Headless": hyperlink(event,text))
    save_session_var = tk.BooleanVar(value=False)
    headless_var = tk.BooleanVar(value=False)
    save_session_checkbox = ttk.Checkbutton(upper_frame, variable=save_session_var)
    save_session_checkbox.grid(row=6, column=1, padx=10, pady=2, sticky="w")
    headless_checkbox = ttk.Checkbutton(upper_frame, variable=headless_var)
    headless_checkbox.grid(row=7, column=1, padx=10, pady=2, sticky="w")
    widget["With session"] = save_session_var
    widget["Headless"] = headless_var
    tokens = [
        ("Success tokens", 8),
        ("Failure tokens", 9)
    ]
    for token_text, row in tokens:
        label = ttk.Label(upper_frame, text=token_text, foreground="blue", cursor="hand2")
        label.grid(row=row, column=0, padx=10, pady=2, sticky="e")  # Right-align labels
        label.bind("<Button-1>", lambda event, text=token_text: hyperlink(event,text))
        entry = ttk.Entry(upper_frame)
        entry.grid(row=row, column=1, padx=10, pady=2, sticky="ew")
        widget[token_text] = entry  # Store the entry in the widget dictionary
    speed_label = ttk.Label(upper_frame, text="Speed", foreground="blue", cursor="hand2")
    speed_label.grid(row=10, column=0, padx=10, pady=2, sticky="e")
    speed_label.bind("<Button-1>", lambda event, text="Speed": hyperlink(event,text))
    speed_frame = ttk.Frame(upper_frame)
    speed_frame.grid(row=10, column=1, padx=10, pady=2, sticky="w")
    speed_var = tk.StringVar(value="Normal")
    speeds = ["Fast", "Normal", "Slow"]
    for speed in speeds:
        radio_button = ttk.Radiobutton(speed_frame, text=speed, variable=speed_var, value=speed)
        radio_button.pack(side="left", padx=(0, 10))
    widget["Speed"] = speed_var
    button_frame = ttk.Frame(upper_frame)
    button_frame.grid(row=11, column=1, padx=10, pady=2)
    scrape_button = ttk.Button(button_frame, text="Scrape", command=scrape_button_command)
    scrape_button.pack(side="left", padx=(0, 10))
    stop_button = ttk.Button(button_frame, text="Stop")
    stop_button.pack(side="left")
    widget_list = list(widget.values())
    return upper_frame


lower_frame = None
log_text_widget = None


def create_lower_frame(parent):
    global lower_frame, log_text_widget
    lower_frame = ttk.Frame(parent, padding="10", relief=tk.SUNKEN)
    log_text_widget = scrolledtext.ScrolledText(lower_frame, wrap=tk.WORD, width=60, height=20, font="TkDefaultFont")
    log_text_widget.pack(fill="both", expand=True, padx=10, pady=10)
    return lower_frame


def log_to_text_field(record):
    global lower_frame, log_text_widget
    lower_frame.after(0, lambda: (
        log_text_widget.insert("1.0", record.getMessage() + '\n')
    ))


def create_gui_2(parent):
    parent.columnconfigure(0, weight=1)
    parent.rowconfigure(0, weight=1)
    paned_window = ttk.PanedWindow(parent, orient=tk.VERTICAL)
    paned_window.grid(row=0, column=0, sticky="nsew")
    upper_frame = create_upper_frame(paned_window)
    paned_window.add(upper_frame, weight=0)
    lower_frame = create_lower_frame(paned_window)
    paned_window.add(lower_frame, weight=1)
