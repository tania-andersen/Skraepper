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

# Coordinates for GUI elements
PAG_URL_CRD_WIN = (324, 246)
FIRST_PAGE_CRD_WIN = (385, 283)
LAST_PAGE_CRD_WIN = (347, 321)
DETAIL_PGSEL_CRD_WIN = (406, 352)
SCRAPE_BTN_CRD_WIN = (716, 625)


def stream_output(process):
    """Continuously reads process output without blocking."""
    for line in iter(process.stdout.readline, ''):
        print(f"[GUI Output] {line.strip()}")
    process.stdout.close()


BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))  # Go up one level


def start_gui_process():
    """
    Launches the main_gui.pyw script in test mode and captures its output non-blocking.
    """

    python_path = os.path.join(BASE_DIR, ".venv", "Scripts", "pythonw.exe")
    script_path = os.path.join(BASE_DIR, "main_gui.pyw")

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
        cwd=BASE_DIR  # Run subprocess in the parent directory
    )

    # Start a separate thread to capture and print output
    threading.Thread(target=stream_output, args=(process,), daemon=True).start()

    print(f"Started '{script_path}' with PID {process.pid}")
    return process


def automate_scraping_process():
    import os
    import shutil

    for item in [os.path.join(BASE_DIR, "pagination_pages"), os.path.join(BASE_DIR, "detail_pages"),
                 os.path.join(BASE_DIR, "components_state.json")]:
        (shutil.rmtree(item) if os.path.isdir(item) else os.remove(item)) if os.path.exists(item) else None

    print("Cleanup complete.")

    """
    Automates GUI interactions after launching the application.
    """
    process = start_gui_process()

    # Add a delay to allow the GUI to load
    time.sleep(5)  # Adjust based on GUI startup time

    inputs = {
        PAG_URL_CRD_WIN: "https://books.toscrape.com/catalogue/page-*.html",
        FIRST_PAGE_CRD_WIN: "1",
        LAST_PAGE_CRD_WIN: "1",
        DETAIL_PGSEL_CRD_WIN: "article > h3 > a"
    }

    # Click and type input values
    for coords, text in inputs.items():
        pyautogui.click(coords)
        pyautogui.write(text, interval=0.1)
        time.sleep(0.5)

    # Click the scrape button to initiate scraping
    pyautogui.click(SCRAPE_BTN_CRD_WIN)
    print("Scraping process initiated.")
    # Run validation after waiting for scrape to complete
    time.sleep(5 * 60)

    try:
        validate_scrape_results()
        process.terminate()
    except AssertionError as e:
        print(f"Test failed: {e}")
        process.terminate()
        sys.exit(1)  # Exit with error so GH Actions marks it as failed


def validate_scrape_results():
    """Validates that the scrape process completed successfully."""

    log_file = os.path.join(BASE_DIR, "skraepper.log")
    detail_pages_folder = os.path.join(BASE_DIR, "detail_pages")
    target_file = os.path.join(BASE_DIR, "detail_pages/pagesource_0018.html")

    expected_log_strings = [
        "INFO Scraping completed.",
        "INFO Starting browser.",
        "INFO Downloading page source to detail_pages",
        "INFO Loading URL:"
    ]

    # Check if log file contains expected strings
    if not os.path.exists(log_file):
        raise AssertionError(f"Log file '{log_file}' not found.")

    with open(log_file, "r", encoding="utf-8") as log:
        log_content = log.read()

    for expected in expected_log_strings:
        assert expected in log_content, f"Log file missing expected entry: {expected}"

    print("Log file contains all expected entries.")

    # Check if detail_pages contains 19 files
    if not os.path.exists(detail_pages_folder):
        raise AssertionError(f"Folder '{detail_pages_folder}' not found.")

    detail_files = os.listdir(detail_pages_folder)
    assert len(detail_files) == 20, f"Expected 20 files in '{detail_pages_folder}', found {len(detail_files)}."

    print("Correct number of files found in detail_pages.")

    # Check if detail_pages/pagesource_0018.html is larger than 10 KB
    if not os.path.exists(target_file):
        raise AssertionError(f"File '{target_file}' not found.")

    file_size_kb = os.path.getsize(target_file) / 1024
    assert file_size_kb > 10, f"File '{target_file}' is too small ({file_size_kb:.2f} KB)."

    print("pagesource_0018.html is larger than 10 KB.")


if __name__ == "__main__":
    if os.getenv('TEST_SKRAEPPER'):
        automate_scraping_process()
