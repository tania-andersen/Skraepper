# Copyright Tania Andersen 2025 @taniaandersen.bsky.social
# Licence: GNU AFFERO GENERAL PUBLIC LICENSE Version 3 https://www.gnu.org/licenses/agpl-3.0.en.html

import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import os
import shutil
from datetime import datetime
import scrape

CANCEL_ = " Cancel "
START_NEW_SCRAPE_ = " Start new scrape "


def show_file_management_dialog(parent) -> bool:
    # Returns true if canceled.
    was_cancelled = False

    def on_delete():
        nonlocal was_cancelled
        try:
            for directory in [scrape.PAGINATION_PAGES, scrape.DETAIL_PAGES]:
                if os.path.exists(directory):
                    shutil.rmtree(directory)
            dialog.destroy()
            was_cancelled = show_delete_confirmation_dialog(parent)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete folder: {e}")

    def on_rename():
        nonlocal was_cancelled
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d-%H-%M")
            old_pagination_name = None
            old_detail_name = None

            if os.path.exists("pagination_pages"):
                old_pagination_name = f"old_pagination_pages_{timestamp}"
                os.rename("pagination_pages", old_pagination_name)

            if os.path.exists("detail_pages"):
                old_detail_name = f"old_detail_pages_{timestamp}"
                os.rename("detail_pages", old_detail_name)

            dialog.destroy()
            was_cancelled = show_rename_confirmation_dialog(parent, old_pagination_name, old_detail_name)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to rename folders: {e}")

    def on_cancel():
        nonlocal was_cancelled
        was_cancelled = True
        dialog.destroy()

    dialog = tk.Toplevel(parent)
    dialog.title("File Management")
    window_width = 825
    window_height = 150
    screen_width = dialog.winfo_screenwidth()
    screen_height = dialog.winfo_screenheight()
    x = (screen_width // 2) - (window_width // 2)
    y = (screen_height // 2) - (window_height // 2)
    dialog.geometry(f"{window_width}x{window_height}+{x}+{y}")
    main_frame = ttk.Frame(dialog)
    main_frame.pack(expand=True, fill="both", padx=20, pady=20)
    label_text = (
        "There are already downloaded files.\n"
        "Do you want to delete or rename the folders (delete cannot be undone)?"
    )
    label = ttk.Label(main_frame, text=label_text, justify="left")
    label.pack(anchor="w", pady=(0, 10))
    button_frame = ttk.Frame(main_frame)
    button_frame.pack()
    delete_button = ttk.Button(button_frame, text="Delete", command=on_delete)
    rename_button = ttk.Button(button_frame, text="Rename", command=on_rename)
    cancel_button = ttk.Button(button_frame, text="Cancel", command=on_cancel)
    delete_button.pack(side=tk.LEFT, padx=5)
    rename_button.pack(side=tk.LEFT, padx=5)
    cancel_button.pack(side=tk.LEFT, padx=5)
    button_frame.pack_configure(anchor="center")
    # Make the dialog modal and wait for it to close
    dialog.transient(parent)  # Set the dialog as a transient window of the parent
    dialog.grab_set()  # Grab all events to the dialog
    parent.wait_window(dialog)  # Wait until the dialog is closed
    return was_cancelled


def show_delete_confirmation_dialog(parent) -> bool:
    # returns true if cancelled
    was_cancelled_confirm = False

    def on_start_scrape():
        dialog.destroy()

    def on_cancel():
        dialog.destroy()
        nonlocal was_cancelled_confirm
        was_cancelled_confirm = True

    dialog = tk.Toplevel(parent)
    dialog.title("Delete Confirmation")
    window_width = 400
    window_height = 150
    screen_width = dialog.winfo_screenwidth()
    screen_height = dialog.winfo_screenheight()
    x = (screen_width // 2) - (window_width // 2)
    y = (screen_height // 2) - (window_height // 2)
    dialog.geometry(f"{window_width}x{window_height}+{x}+{y}")
    main_frame = ttk.Frame(dialog)
    main_frame.pack(expand=True, fill="both", padx=20, pady=20)
    label_text = "Old files were deleted."
    label = ttk.Label(main_frame, text=label_text, justify="left")
    label.pack(anchor="w", pady=(0, 10))
    button_frame = ttk.Frame(main_frame)
    button_frame.pack()
    start_scrape_button = ttk.Button(button_frame, text=START_NEW_SCRAPE_, command=on_start_scrape)
    cancel_button = ttk.Button(button_frame, text=CANCEL_, command=on_cancel)
    start_scrape_button.pack(side=tk.LEFT, padx=5)
    cancel_button.pack(side=tk.LEFT, padx=5)
    button_frame.pack_configure(anchor="center")
    # Make the dialog modal and wait for it to close
    dialog.transient(parent)
    dialog.grab_set()
    parent.wait_window(dialog)
    return was_cancelled_confirm


def show_rename_confirmation_dialog(parent, old_pagination_name, old_detail_name) -> bool:
    # Returns true if cancelled
    was_cancelled_confirm = False

    def on_start_scrape():
        dialog.destroy()

    def on_cancel():
        nonlocal was_cancelled_confirm
        dialog.destroy()
        was_cancelled_confirm = True

    dialog = tk.Toplevel(parent)
    dialog.title("Rename Confirmation")
    window_width = 800
    window_height = 150
    screen_width = dialog.winfo_screenwidth()
    screen_height = dialog.winfo_screenheight()
    x = (screen_width // 2) - (window_width // 2)
    y = (screen_height // 2) - (window_height // 2)
    dialog.geometry(f"{window_width}x{window_height}+{x}+{y}")
    main_frame = ttk.Frame(dialog)
    main_frame.pack(expand=True, fill="both", padx=20, pady=20)
    label_text = (
        f'Pagination pages folder was renamed "{old_pagination_name}".\n'
        f'Detail pages folder was renamed "{old_detail_name}".'
    )
    label = ttk.Label(main_frame, text=label_text, justify="left")
    label.pack(anchor="w", pady=(0, 10))
    button_frame = ttk.Frame(main_frame)
    button_frame.pack()
    start_scrape_button = ttk.Button(button_frame, text=START_NEW_SCRAPE_, command=on_start_scrape)
    cancel_button = ttk.Button(button_frame, text=CANCEL_, command=on_cancel)
    start_scrape_button.pack(side=tk.LEFT, padx=5)
    cancel_button.pack(side=tk.LEFT, padx=5)
    button_frame.pack_configure(anchor="center")
    dialog.transient(parent)
    dialog.grab_set()
    parent.wait_window(dialog)
    return was_cancelled_confirm
