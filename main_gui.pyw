import logging
import platform
import ctypes
import threading
import webbrowser
from tkinter import filedialog, messagebox
import os
import yaml
from scraper_gui import create_gui_2, get_widget_list as scraper_gui_widget_list
from component_state import *
from extract import extract
from extract import OUTPUT_CSV
import tkinter as tk
from tkinter import ttk

root = None
STATE_FILENAME = 'components_state.json'
test_file_paths = []
EXTRACT_TEXT_AREA = None
FOLDER_ENTRY = None
PROGRESS_BAR = None
text_area = None
table = None
widgets = []
test_files_entry = None
BASE_HELP_URL = "https://github.com/tania-andersen/Skraepper/blob/main/help.md"

def open_link(event, url):
    if '#' in url:
        index = url.index('#')
        url = url[:index] + url[index:].replace(' ', '-')
    webbrowser.open_new(url)


def pick_files(test_files_entry):
    curr_dir = os.getcwd()
    file_paths = filedialog.askopenfilenames(initialdir=curr_dir)
    test_files_entry.config(state='normal')
    test_files_entry.delete(0, 'end')
    test_files_entry.insert(0, ', '.join(file_paths))
    global test_file_paths
    test_file_paths = list(file_paths)


def create_text_area(container):
    global text_area
    if platform.system() == 'Windows':
        text_area = tk.Text(container, font=('Consolas', 10), borderwidth=0, highlightthickness=0,
                            wrap='none')
    else:
        text_area = tk.Text(container, highlightthickness=0, wrap='none')
    text_area.grid(row=1, column=1, sticky="nsew", pady=10, padx=10)
    text_area.bind('<KeyRelease>', schedule_process)
    container.grid_rowconfigure(1, weight=1)
    v_scrollbar = tk.Scrollbar(container, command=text_area.yview)
    v_scrollbar.grid(row=1, column=2, sticky='ns', padx=0)
    text_area['yscrollcommand'] = v_scrollbar.set
    h_scrollbar = tk.Scrollbar(container, orient='horizontal', command=text_area.xview)
    h_scrollbar.grid(row=2, column=1, sticky='ew', padx=0)  # Set padx=0 here
    text_area['xscrollcommand'] = h_scrollbar.set
    widgets.append(text_area)


def create_test_tab(notebook):
    global table, test_files_entry
    frame = tk.Frame(notebook)
    notebook.add(frame, text='Refine')
    paned_window = tk.PanedWindow(frame, orient=tk.VERTICAL, sashwidth=10, sashrelief=tk.RAISED)
    paned_window.pack(fill=tk.BOTH, expand=True)
    upper_frame = tk.Frame(paned_window)
    lower_frame = tk.Frame(paned_window, padx=10, pady=10)
    container = tk.Frame(upper_frame, padx=10, highlightthickness=0)
    container.pack(fill='both', expand=True, pady=(10, 0))
    container.columnconfigure(1, weight=1, pad=10)
    url = BASE_HELP_URL + "Test"
    label = tk.Label(container, text="Test pages", anchor="e", fg="blue", cursor="hand2")
    label.grid(row=0, column=0, sticky="w")
    label.bind("<Button-1>", lambda event, endpoint=url: open_link(event, endpoint))
    url = BASE_HELP_URL + "Extract"
    label = tk.Label(container, text="Extract", anchor="e", fg="blue", cursor="hand2")
    label.grid(row=1, column=0, sticky="ne", pady=10)
    label.bind("<Button-1>", lambda event, endpoint=url: open_link(event, endpoint))
    text_field_button_frame = tk.Frame(container)
    text_field_button_frame.grid(row=0, column=1, sticky="ew", padx=10)
    test_files_entry = tk.Entry(text_field_button_frame, state='normal')
    test_files_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
    widgets.append(test_files_entry)
    pick_files_button = ttk.Button(text_field_button_frame, text="Pick test files",
                                   command=lambda: pick_files(test_files_entry)) #root,
    pick_files_button.pack(side=tk.LEFT, padx=10)
    root.after(0, lambda: create_text_area(
        container))
    paned_window.add(upper_frame)
    paned_window.add(lower_frame)
    root.update()
    paned_window.sash_place(0, 0, root.winfo_height() // 2)
    output_text = tk.StringVar()
    output_text.set("Output")
    label = tk.Label(lower_frame, textvariable=output_text)
    label.pack(anchor="w")
    style = ttk.Style()
    style.configure("Custom.Treeview", rowheight=28)  # Set the row height to 30
    table = ttk.Treeview(lower_frame, show="headings", style="Custom.Treeview")
    vsb = ttk.Scrollbar(lower_frame, orient="vertical", command=table.yview)
    vsb.pack(side='right', fill='y')
    table.pack(fill=tk.BOTH, expand=True)
    table.configure(yscrollcommand=vsb.set)
    table.pack(fill='both', expand=True)


def create_extract_tab(notebook):
    global EXTRACT_TEXT_AREA, FOLDER_ENTRY, PROGRESS_BAR
    frame = tk.Frame(notebook)
    notebook.add(frame, text='Extract')
    container = tk.Frame(frame, padx=10, highlightthickness=0)
    container.pack(fill='both', expand=True, pady=(10, 0))
    container.columnconfigure(1, weight=1, pad=10)
    url = BASE_HELP_URL + "Test"
    label = tk.Label(container, text="Folder", anchor="e", fg="blue", cursor="hand2")
    label.grid(row=0, column=0, sticky="e")
    label.bind("<Button-1>", lambda event, endpoint=url: open_link(event, endpoint))
    url = BASE_HELP_URL + "Extract"
    label = tk.Label(container, text="Extraction", anchor="e", fg="blue", cursor="hand2")
    label.grid(row=1, column=0, sticky="ne", pady=10)
    label.bind("<Button-1>", lambda event, endpoint=url: open_link(event, endpoint))
    text_field_button_frame = tk.Frame(container)
    text_field_button_frame.grid(row=0, column=1, sticky="ew", padx=10)
    folder_entry = tk.Entry(text_field_button_frame, state='normal')
    folder_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
    widgets.append(folder_entry)
    FOLDER_ENTRY = folder_entry
    choose_folder_button = ttk.Button(text_field_button_frame, text=" Choose folder ",
                                      command=lambda: pick_folder(root, folder_entry))
    choose_folder_button.pack(side=tk.LEFT, padx=10)
    if platform.system() == 'Windows':
        text_area = tk.Text(container, font=('Consolas', 10), borderwidth=0, highlightthickness=0,
                            wrap='none')
    else:
        text_area = tk.Text(container, highlightthickness=0, wrap='none')
    text_area.grid(row=1, column=1, sticky="nsew", pady=10, padx=10)
    container.grid_rowconfigure(1, weight=1)
    widgets.append(text_area)
    EXTRACT_TEXT_AREA = text_area
    v_scrollbar = tk.Scrollbar(container, command=text_area.yview)
    v_scrollbar.grid(row=1, column=2, sticky='ns', padx=0)
    h_scrollbar = tk.Scrollbar(container, orient='horizontal', command=text_area.xview)
    h_scrollbar.grid(row=2, column=1, sticky='ew', padx=0)
    text_area['xscrollcommand'] = h_scrollbar.set
    extract_button_progbar_frame = tk.Frame(container)
    extract_button_progbar_frame.grid(row=3, column=1, sticky="ew", padx=10)
    extract_button = ttk.Button(
        extract_button_progbar_frame,
        text=" Extract ",
        command=lambda: threading.Thread(target=lambda: (start_extract(), logging.info("Extraction completed.")),
                                         daemon=True).start()
    )
    extract_button.pack(side=tk.LEFT, padx=10, pady=10)
    progress_bar = ttk.Progressbar(extract_button_progbar_frame, orient='horizontal', mode='determinate')
    progress_bar.pack(side=tk.LEFT, fill=tk.X, expand=True)
    PROGRESS_BAR = progress_bar


def start_extract():
    global EXTRACT_TEXT_AREA, FOLDER_ENTRY
    folder_path = FOLDER_ENTRY.get().strip()
    code = EXTRACT_TEXT_AREA.get("1.0", tk.END).strip()
    extract(input_code=code, folders_or_files=folder_path, no_duplicates=True, testing=False,
            progress_callback=update_progress_bar)
    update_progress_bar(1.0)
    messagebox.showinfo("Extraction Complete", f"Extracted to {OUTPUT_CSV}.")
    update_progress_bar(0.0)


def update_progress_bar(progress: float):
    """
    Updates the progress bar in the GUI.

    :param progress: A float between 0.0 and 1.0 representing the progress.
    """
    global PROGRESS_BAR
    #print(f"progress: {progress}")
    PROGRESS_BAR["value"] = progress * 100  # Convert to percentage for the progress bar
    root.update_idletasks()  # Refresh the GUI


def pick_folder(root, entry_widget):
    """
    Opens a dialog to select a folder and inserts the selected folder path into the entry widget.

    :param root: The root window of the tkinter application.
    :param entry_widget: The Entry widget where the selected folder path will be inserted.
    """
    folder_path = filedialog.askdirectory(parent=root, title="Select a folder")
    if folder_path:
        entry_widget.delete(0, tk.END)
        entry_widget.insert(0, folder_path)  #


def create_scrape_tab(notebook):
    frame = tk.Frame(notebook)
    notebook.add(frame, text='Scrape')
    create_gui_2(frame)


def create_root():
    root = tk.Tk()
    #root.iconbitmap('icon.ico')
    root.title("Skræpper")
    root.update_idletasks()
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    window_width = int(0.66 * screen_width)
    window_height = int(window_width * 9 / 16)
    window_x = int((screen_width - window_width) / 2)
    window_y = int((screen_height - window_height) / 2)
    root.geometry(f'{window_width}x{window_height}+{window_x}+{window_y}')
    return root


if platform.system() == "Windows":
    ctypes.windll.shcore.SetProcessDpiAwareness(1)


def interpret_code():
    global text_area, fill
    test_file_paths = test_files_entry.get().split(", ")
    #print(f"test_file_paths: {test_file_paths}")
    code = text_area.get("1.0", tk.END)
    try:
        df = extract(code, test_file_paths, testing=True)
        update_table(df)
    except yaml.parser.ParserError as e:
        print(f"Parse error at line: {e.problem_mark.line + 1}, column: {e.problem_mark.column + 1}")
    except Exception as e:
        raise e
        """SelectorSyntaxError"""


def schedule_process(event):
    if event.keysym not in ('Left', 'Up', 'Right', 'Down'):
        if schedule_process.job:
            root.after_cancel(schedule_process.job)
        schedule_process.job = root.after(200, interpret_code)


schedule_process.job = None


def update_table(df):
    global table
    for row in table.get_children():
        table.delete(row)
    for col in table["columns"]:
        table.heading(col, text="")
        table.column(col, width=0)
    table["columns"] = []
    columns = df.columns.tolist()
    table["columns"] = columns
    for col in columns:
        table.heading(col, text=col)
        table.column(col, width=100, stretch=tk.YES)
    for index, row in df.iterrows():
        table.insert("", tk.END, values=list(row))


def start_gui():
    global root
    root = create_root()
    menu_bar = tk.Menu(root)
    file_menu = tk.Menu(menu_bar, tearoff=0)
    file_menu.add_command(label="Open scrape settings", command=None)
    file_menu.add_command(label="Save scrape settings", command=None)
    file_menu.add_command(label="Detail Page Folder", command=None)  # Replace 'None' with the function to be called
    file_menu.add_command(label="Pagination Page Folder", command=None)
    file_menu.add_command(label="Error File", command=None)
    file_menu.add_command(label="Log", command=None)
    file_menu.add_separator()
    file_menu.add_command(label="Quit", command=root.quit)
    menu_bar.add_cascade(label="File", menu=file_menu)
    help_menu = tk.Menu(menu_bar, tearoff=0)
    help_menu.add_command(label="Help...", command=None)  # Replace 'None' with the function to be called
    help_menu.add_command(label="About", command=None)
    menu_bar.add_cascade(label="Help", menu=help_menu)
    root.config(menu=menu_bar)
    style = ttk.Style()
    style.configure('TNotebook.Tab', padding=[10, 5])
    notebook = ttk.Notebook(root, style='TNotebook')
    notebook.pack(fill=tk.BOTH, expand=True)
    create_scrape_tab(notebook)
    create_extract_tab(notebook)
    create_test_tab(notebook)
    components = scraper_gui_widget_list()
    components.extend(widgets)
    root.protocol("WM_DELETE_WINDOW", lambda: on_exit(root, components, 'components_state.json'))
    load_components_state(components, STATE_FILENAME)
    root.mainloop()


def on_exit(root, components, file_name):
    save_components_state(components, file_name)
    root.destroy()


start_gui()
