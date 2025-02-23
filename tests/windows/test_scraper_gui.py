# Copyright Tania Andersen 2025 @taniaandersen.bsky.social
# License: GNU AFFERO GENERAL PUBLIC LICENSE Version 3 https://www.gnu.org/licenses/agpl-3.0.en.html

# NB: DO NOT RUN ON YOUR DESKTOP. Run in a controlled environment.
# This script will delete files, perform automated GUI interactions etc.

import sys
import pyautogui
import time
import threading
import os
import subprocess
import shutil
import pyperclip

exe_name = ""
process = None


def stream_output(process):
    """Continuously reads process output without blocking."""
    for line in iter(process.stdout.readline, ''):
        print(f"[GUI Output] {line.strip()}", flush=True)
    process.stdout.close()


def start_gui_exe_process():
    """Launches the Skraepper executable in test mode."""
    global process, base_dir
    exe_path = os.path.join(base_dir, exe_name)
    command = [exe_path, "-testmode"]
    env = os.environ.copy()
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, env=env,
                               cwd=base_dir)
    threading.Thread(target=stream_output, args=(process,), daemon=True).start()
    print(f"Started '{exe_path}' with PID {process.pid}")
    return process


def start_gui_script_process():
    """
    Launches the main_gui.pyw script in test mode and captures its output non-blocking.
    Supposes a .venv venv dir in base dir.
    """
    global process, base_dir

    python_path = os.path.join(base_dir, ".venv", "Scripts", "pythonw.exe")
    script_path = os.path.join(base_dir, "main_gui.pyw")

    print(f"Current Working Directory: {os.getcwd()}")
    print(f"Resolved Python Path: {python_path}")
    print(f"Resolved Script Path: {script_path}")

    command = [python_path, script_path, "-testmode"]

    # Preserve existing environment variables and add PLAYWRIGHT_BROWSERS_PATH
    env = os.environ.copy()
    env["PLAYWRIGHT_BROWSERS_PATH"] = "0"

    process = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        env=env,
        cwd=base_dir  # Run subprocess in the parent directory
    )

    # Start a separate thread to capture and print output
    threading.Thread(target=stream_output, args=(process,), daemon=True).start()

    print(f"Started '{script_path}' with PID {process.pid}")
    return process


def setup(test_type):
    global process

    """Sets up the test environment by cleaning up old data."""
    cleanup_items = [
        os.path.join(base_dir, "pagination_pages"),
        os.path.join(base_dir, "detail_pages"),
        os.path.join(base_dir, "components_state.json")
    ]

    for item in cleanup_items:
        if os.path.exists(item):
            shutil.rmtree(item) if os.path.isdir(item) else os.remove(item)
    print("Cleanup complete.")

    if test_type == "testexe":
        process = start_gui_exe_process()
    elif test_type == "testscript":
        process = start_gui_script_process()
    else:
        raise ValueError("Invalid test type. Use 'testexe' or 'testscript'.")

    time.sleep(30)  # Allow GUI to load


def test_scrape():
    """Automates the GUI interactions and runs the scraper test."""
    global process

    # Coordinates for GUI elements
    PAG_URL_CRD_WIN = (363, 246)
    FIRST_PAGE_CRD_WIN = (363, 283)
    LAST_PAGE_CRD_WIN = (363, 321)
    DETAIL_PGSEL_CRD_WIN = (363, 352)
    SCRAPE_BTN_CRD_WIN = (751, 625)

    inputs = {
        PAG_URL_CRD_WIN: "https://books.toscrape.com/catalogue/page-*.html",
        FIRST_PAGE_CRD_WIN: "1",
        LAST_PAGE_CRD_WIN: "1",
        DETAIL_PGSEL_CRD_WIN: "article > h3 > a"
    }

    for coords, text in inputs.items():
        pyautogui.click(coords)
        pyautogui.write(text, interval=0.1)
        time.sleep(0.5)

    pyautogui.click(SCRAPE_BTN_CRD_WIN)
    print("Scraping process initiated.")
    time.sleep(5 * 60)  # Wait for scraping to complete

    try:
        validate_scrape_results()
    except AssertionError as e:
        print(f"Test failed: {e}")
        raise


def validate_scrape_results():
    """Validates the scraper output."""
    log_file = os.path.join(base_dir, "skraepper.log")
    detail_pages_folder = os.path.join(base_dir, "detail_pages")
    target_file = os.path.join(detail_pages_folder, "pagesource_0018.html")

    expected_log_strings = [
        "INFO Scraping completed.",
        "INFO Starting browser.",
        "INFO Downloading page source to detail_pages",
        "INFO Loading URL:"
    ]

    assert os.path.exists(log_file), f"Log file '{log_file}' not found."

    with open(log_file, "r", encoding="utf-8") as log:
        log_content = log.read()

    for expected in expected_log_strings:
        assert expected in log_content, f"Log file missing expected entry: {expected}"

    assert os.path.exists(detail_pages_folder), f"Folder '{detail_pages_folder}' not found."

    detail_files = os.listdir(detail_pages_folder)
    assert len(detail_files) == 20, f"Expected 20 files, found {len(detail_files)}."

    assert os.path.exists(target_file), f"File '{target_file}' not found."

    file_size_kb = os.path.getsize(target_file) / 1024
    assert file_size_kb > 10, f"File '{target_file}' is too small ({file_size_kb:.2f} KB)."
    print("Scrape results validated successfully.")


def test_refine():
    refine_tab_crd_win = 300, 193
    files_crd_win = 275, 250
    skraeppex_crd_win = 300, 300
    output_crd_win = 233, 826

    pyautogui.click(refine_tab_crd_win)
    time.sleep(3)  # Wait for tab to render

    file_path = os.path.join(base_dir, "detail_pages", "pagesource_0010.html")

    # Click folder field and write path
    pyautogui.click(files_crd_win)
    pyautogui.write(file_path, interval=0.1)

    pyautogui.click(skraeppex_crd_win)
    code1 = """filldown: Title, Price, Prod-desc
dropna: yes
Title: div.col-sm-6:nth-child(2) > h1:nth-child(1)
Price:
   selector: .price_color
nodes: 1
"""
    pyautogui.write(code1, interval=0.05)
    pyautogui.press("backspace", presses=3, interval=0.1)

    code2 = """Prod-desc: .product_page > p:nth-child(3)"""

    pyautogui.write(code2, interval=0.05)
    time.sleep(3)  # Small delay to allow table to update
    pyautogui.click(output_crd_win)
    pyautogui.hotkey("ctrl", "c")  # Simulate Ctrl+C
    time.sleep(1)  # Small delay to allow clipboard to update
    copied_text = pyperclip.paste()  # Get clipboard content
    print(f"copied_text: {copied_text}")
    assert "£" in copied_text, "Copied output does not contain success token."


def test_extract():
    extract_tab_crd_win = 235, 200
    folder_crd_win = (360, 244)
    skraeppex_crd_win = (305, 300)
    extract_crd_win = (300, 946)

    folder_path = os.path.join(base_dir, "detail_pages")
    output_file = os.path.join(base_dir, "output.csv")

    print(f"output_file: {output_file}")

    pyautogui.click(extract_tab_crd_win)
    time.sleep(3)  # Wait for tab to render

    # Click folder field and write path
    pyautogui.click(folder_crd_win)
    pyautogui.write(folder_path, interval=0.1)

    # Click skraeppex field and write extraction rules
    pyautogui.click(skraeppex_crd_win)
    extraction_rules = """filldown: Title, Price, Prod-desc
dropna: yes
Title: div.col-sm-6:nth-child(2) > h1:nth-child(1)
Price:
   selector: .price_color
   nodes: 1
Prod-desc: .product_page > p:nth-child(3)"""
    pyautogui.write(extraction_rules, interval=0.05)

    # Click extract button
    pyautogui.click(extract_crd_win)
    print("Extraction process initiated.")

    time.sleep(10)  # Wait for extract to complete

    pyautogui.press("enter")  # Dismiss dialog

    time.sleep(1)  # Wait for UI to settle

    # Validate output file existence and size
    assert os.path.exists(output_file), "Output file 'output.csv' not found."
    assert os.path.getsize(output_file) > 25 * 1024, "Output file 'output.csv' is smaller than expected (>25 KB)."
    print("Extract results validated successfully.")


def teardown():
    """Handles post-test cleanup."""
    global process
    if process:
        process.terminate()
    if test_type == "testexe":
        result = subprocess.run(["taskkill", "/F", "/IM", exe_name], capture_output=True, text=True)
        print(result.stdout.strip(), result.stderr.strip())
    print("Test completed. Process terminated.")


if __name__ == "__main__":

    test_type = sys.argv[1]

    if test_type == "testexe":
        if len(sys.argv) != 4:
            print(f"Bad args.")
            sys.exit(1)
        else:
            exe_name = sys.argv[2]
            base_dir = sys.argv[3]
    elif test_type == "testscript":
        if len(sys.argv) != 3:
            print(f"Bad args.")
            sys.exit(1)
        else:
            base_dir = sys.argv[2]

    if os.getenv('TEST_SKRAEPPER'):
        setup(test_type)
        exit_code = 0
        try:
            test_scrape()
            test_extract()
            test_refine()
            print(f"Test passed.")
        except AssertionError as e:
            # Print the error message
            print(f"Test failed: {e}")
            # Return exit code 0
            exit_code = 1
        finally:
            teardown()
        sys.exit(exit_code)
