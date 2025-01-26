import json
import logging
import sys
import time
import tkinter as tk
from random import randint, uniform
from tkinter import ttk
from urllib.parse import urljoin
from playwright.sync_api import Page, sync_playwright
from folder_dialogues import show_file_management_dialog
import os
from typing import List, Union, Pattern
from bs4 import BeautifulSoup
from urllib.parse import urlparse

DETAIL_PAGES = "detail_pages"
PAGINATION_PAGES = "pagination_pages"
file_number = 0
SUCCESS_TOKENS = []
FAILURE_TOKENS = []
CONTEXT = None
PERSISTENT_SESSION = False
LONG_DELAY = False
SLEEP_MIN = 1.0
SLEEP_MAX = 2.0
SESSION_FILE = 'session.json'
SESSION_META_FILE = 'session_meta.txt'
FAILS_LOGNAME = 'fails.txt'
FAILS_LOG = None
PARENT = None
DOMAIN = None


def user_logged_in() -> bool:
    """
    Create a modal Toplevel dialog that stays on top and is centered on the screen.
    Uses the global PARENT variable as the parent window.
    Returns True if "Proceed" is clicked, or False if "Cancel" is clicked.
    """
    global PARENT

    dialog = tk.Toplevel(PARENT)
    dialog.title("Login Required")
    dialog.grab_set()  # Block interaction with the parent window
    dialog.transient(PARENT)  # Stay on top of the parent window
    message = "Login on the web page and click proceed."
    label = ttk.Label(dialog, text=message)
    label.pack(padx=20, pady=10)
    result = False

    def on_proceed():
        nonlocal result
        result = True
        dialog.destroy()  # Close the dialog

    def on_cancel():
        nonlocal result
        result = False
        dialog.destroy()  # Close the dialog

    button_frame = ttk.Frame(dialog)
    button_frame.pack(padx=20, pady=10)
    proceed_button = ttk.Button(button_frame, text="Proceed", command=on_proceed)
    proceed_button.pack(side=tk.LEFT, padx=5)
    cancel_button = ttk.Button(button_frame, text="Cancel", command=on_cancel)
    cancel_button.pack(side=tk.LEFT, padx=5)
    dialog.update_idletasks()
    screen_width = dialog.winfo_screenwidth()
    screen_height = dialog.winfo_screenheight()
    dialog_width = dialog.winfo_width()
    dialog_height = dialog.winfo_height()
    x = (screen_width // 2) - (dialog_width // 2)
    y = (screen_height // 2) - (dialog_height // 2)
    dialog.geometry(f"+{x}+{y}")
    PARENT.wait_window(dialog)
    return result


def _login(page, login_url: str, password_selector: str, username: str, login_selector: str = None,
           wait_for_login_interaction: bool = False, gui: bool = False) -> bool:
    page.goto(login_url)
    return user_logged_in()


def _log_warning_no_urls(url_selector: str):
    logging.warning("No URLs found for selector '%s'", url_selector)


def _process_extracted_urls(urls: List[str], url_selector: str, base_url: str) -> List[str]:
    if not urls:
        _log_warning_no_urls(url_selector)
    urls = [urljoin(base_url, url) for url in urls]
    urls = _filter_urls_by_domain(urls, base_url)
    return urls


def _extract_urls_from_html(html: str, url_selector: str, base_url: str = '') -> List[str]:
    soup = BeautifulSoup(html, 'html.parser')
    if not soup.select_one(url_selector):
        _log_warning_no_urls(url_selector)
        return []
    urls = [a.get('href') for a in soup.select(url_selector)]
    return _process_extracted_urls(urls, url_selector, base_url)


def _extract_urls(page, url_selector: str, base_url: str = '') -> List[str]:  # page is a playwright object
    if not page.query_selector(url_selector):
        _log_warning_no_urls(url_selector)
        return []
    urls = [a.get_attribute('href') for a in page.query_selector_all(url_selector)]
    return _process_extracted_urls(urls, url_selector, base_url)


def _create_page(p, headless):
    global CONTEXT, PERSISTENT_SESSION
    browser = p.chromium.launch(headless=headless)

    saved_domain = None
    if os.path.exists(SESSION_META_FILE):
        with open(SESSION_META_FILE, 'r') as f:
            saved_domain = f.read().strip()
    if PERSISTENT_SESSION and os.path.exists(SESSION_FILE) and DOMAIN == saved_domain:
        CONTEXT = browser.new_context(storage_state=SESSION_FILE)
        logging.info(f"Created new context with storage state {SESSION_FILE}")
    else:
        CONTEXT = browser.new_context()
        logging.info("Created new context")
    page = CONTEXT.new_page()
    return browser, page


def _create_folders_and_files():
    global FAILS_LOG
    if not os.path.exists(DETAIL_PAGES):
        os.mkdir(DETAIL_PAGES)
    if not os.path.exists(PAGINATION_PAGES):
        os.makedirs(PAGINATION_PAGES)
    if not os.path.exists(FAILS_LOGNAME):
        open(FAILS_LOGNAME, "w").close()
    FAILS_LOG = open(FAILS_LOGNAME, "a")


downloaded_detail_urls = set()


def _download_page(page, url):
    global file_number, downloaded_detail_urls
    if url in downloaded_detail_urls:
        logging.info(f"Already downloaded {url}. Skipping.")
        return

    downloaded_detail_urls.add(url)
    _goto_and_wait(url, page)
    file_name = os.path.join(DETAIL_PAGES, f"pagesource_{file_number:04d}.html")
    logging.info("Downloading page source to %s", file_name)
    with open(file_name, 'w', encoding='utf-8') as f:
        f.write(page.content())
    file_number += 1


_stop_program_flag = False


def _stop_program():
    global _stop_program_flag
    _stop_program_flag = True


def _goto_and_wait(detail_url: str, page: Page) -> None:
    global SUCCESS_TOKENS, FAILURE_TOKENS, FAILS_LOG, _stop_program_flag

    if _stop_program_flag:
        logging.info(f"Stopping program.")
        if PERSISTENT_SESSION:
            save_session(CONTEXT)
        sys.exit(-1)

    logging.info("Loading URL: %s", detail_url)
    try:
        page.goto(detail_url)
        _random_sleep(page)
        response = page.content()

        if SUCCESS_TOKENS == []:
            no_success_tokens = False
        else:
            no_success_tokens = SUCCESS_TOKENS is not None and not any(
                token.lower() in response.lower() for token in SUCCESS_TOKENS)
        if FAILURE_TOKENS == []:
            failure_tokens = False
        else:
            failure_tokens = FAILURE_TOKENS is not None and any(token in response.lower() for token in FAILURE_TOKENS)
        if no_success_tokens or failure_tokens:
            if PERSISTENT_SESSION:
                save_session(CONTEXT)
            logging.error("Failure tokens or no success tokens in source. URL: %s, written to error.html.", detail_url)
            with open("error.html", "w", encoding="utf-8") as f:
                f.write(response)
            sys.exit(-1)
    except Exception as e:
        logging.error("An error occurred while processing URL %s: %s", detail_url, str(e))
        print(detail_url, file=FAILS_LOG)
        _random_sleep(page)


def _scrape_paginated_pages(
        page,
        pagination_url_template: str,
        first_page: int,
        last_page: int,
        detail_url_selector: str
) -> None:
    for page_num in range(first_page, last_page + 1):
        page_url = pagination_url_template.replace('*', str(page_num))
        _goto_and_wait(page_url, page)
        page_filename = f"pagination_page_{page_num:04}.html"
        # TODO DUPLICATES ARE POSSIBLE
        with open(os.path.join(PAGINATION_PAGES, page_filename), "w", encoding="utf-8") as f:
            f.write(page.content())
        logging.info(f"Saved pagination page {page_num} to {os.path.join(PAGINATION_PAGES, page_filename)}")
        if detail_url_selector is not None:
            detail_urls = _extract_urls(page, detail_url_selector, base_url=page_url)
            for detail_url in detail_urls:
                _download_page(page, detail_url)


def _scrape_from_folder(page, pagination_url_folders: List[str], detail_url_selector: str, base_url: str):
    for folder in pagination_url_folders:
        for filename in os.listdir(folder):
            if not filename.endswith('.html'):
                continue
            file_path = os.path.join(folder, filename)
            if os.path.isfile(file_path):
                with open(file_path, 'r', encoding='utf-8') as file:
                    html = file.read()
                if detail_url_selector is not None:
                    detail_urls = _extract_urls_from_html(html, detail_url_selector, base_url)
                    for detail_url in detail_urls:
                        _download_page(page, detail_url)


def _random_sleep(page: Page) -> None:
    sleep_time = uniform(SLEEP_MIN, SLEEP_MAX)
    if (LONG_DELAY):
        if uniform(0.0, 1.0) < 0.05:  # 5% chance of delay
            delay_time = uniform(180, 360)  # 3 to 6 minutes
            logging.info(f"Long sleep for {delay_time:.2f} seconds")
            time.sleep(delay_time)

    logging.info(f"Sleeping for {sleep_time:.2f} seconds")
    time.sleep(sleep_time)
    viewport = page.viewport_size
    center_x = int(viewport["width"] / 2)
    center_y = int(viewport["height"] / 2)
    for _ in range(randint(2, 3)):
        x = center_x + randint(-100, 100)
        y = center_y + randint(-100, 100)
        page.mouse.move(x, y)
        time.sleep(uniform(0.1, 0.2))
    page.evaluate(
        '(async () => { await new Promise(resolve => { window.scrollTo(0, document.body.scrollHeight); setTimeout(resolve, 2000); }); })()')


def save_session(context):
    logging.info(f"Saving storage state.")
    state = context.storage_state()
    with open(SESSION_FILE, 'w') as sf, open(SESSION_META_FILE, 'w') as mf:
        json.dump(state, sf)  # Write session state to SESSION_FILE (as JSON)
        if DOMAIN:
            mf.write(DOMAIN)


def stop_program():
    global _stop_program_flag
    _stop_program_flag = True


# urls_to_scrape = []


def _crawl(page, follow_link_selector, start_page, follow_if_contains):
    logging.info(f"Crawling")
    # global urls_to_scrape
    urls_downloaded = []
    urls_to_scrape = [start_page]
    while urls_to_scrape:
        logging.info(f"urls to scrape: {urls_to_scrape}")

        url = urls_to_scrape.pop()

        logging.info(f"Processing: {url}")
        urls_downloaded.append(url)
        _download_page(page, url)
        urls = _extract_urls(page, follow_link_selector, url)
        if not urls:
            logging.warning("No URLs found")
        logging.info(f"Found raw urls: {urls}")
        filtered_urls = _filter_urls(urls, page.content(), follow_link_selector, follow_if_contains,
                                     base_url=start_page)
        logging.info(f"Filtered urls: {filtered_urls}")
        urls_to_scrape += filtered_urls
        logging.info(f"urls_to_scrape before removing duplicates: {len(urls_to_scrape)}")
        urls_to_scrape = [url for url in urls_to_scrape if url not in urls_downloaded]
        logging.info(f"urls_to_scrape: {len(urls_to_scrape)}")


def _filter_urls_by_domain(urls: List[str], base_url: str) -> List[str]:
    base_parsed = urlparse(base_url)
    base_domain = base_parsed.netloc
    filtered_urls = set()
    for url in urls:
        parsed = urlparse(url)
        if parsed.netloc == base_domain:
            filtered_urls.add(url)

    logging.info(f"Found {len(filtered_urls)} filtered urls by domain")
    return list(filtered_urls)


def _filter_urls(urls: List[str], page_content: str, follow_link_selector: str,
                 follow_if_contains: Union[str, Pattern[str]], base_url: str) -> List[str]:
    filtered_urls = []
    soup = BeautifulSoup(page_content, 'html.parser')
    nodes = soup.select(follow_link_selector)
    logging.info(f"Found {len(nodes)} nodes")
    for url in urls:
        for node in nodes:
            node_text = node.get_text()
            if isinstance(follow_if_contains, str):
                logging.info(f"Filter by string")
                if follow_if_contains.lower() in node_text.lower():
                    filtered_urls.append(url)
                    logging.info(f"Found {follow_if_contains} match for: {url}")
            else:
                if follow_if_contains.search(node_text):
                    filtered_urls.append(url)

    return _filter_urls_by_domain(filtered_urls, base_url)


def scrape(
        # URL Pagination Parameters
        pagination_url_template: str = None,  # Template for generating URLs for paginated pages
        first_page: int = None,  # First page number to start scraping
        last_page: int = None,  # Last page number to stop scraping
        detail_url_selector: str = None,  # Selector for extracting detail page URLs

        # pagination_url_folders
        pagination_url_folders: List[str] = None,
        base_url: str = None,

        # Follow Link Parameters
        # NEW: points to a set of nodes that contains hrefs.
        follow_link_selector: str = None,  # CSS selector for links to follow on each page
        start_page: str = None,  # URL of the starting page
        follow_if_contains: Union[str, Pattern[str]] = None,  # String or regex pattern to determine if a link should
        # be followed

        # Login Parameters
        login_url: str = None,  # URL for the login page
        username: str = None,  # Username for login
        username_selector: str = None,  # Selector for the username input field
        password_selector: str = None,  # Selector for the password input field
        wait_for_login_interaction: bool = False,  # Flag indicating whether to wait for login interaction after login

        # Logging Parameter
        log_file: str = None,  # File to log scraping output
        log_handler_emitter=None,

        # Browser Options
        headless: bool = False,  # Flag indicating whether to run the browser in headless mode

        # Session Persistence
        persistent_session: bool = False,  # Flag indicating whether to maintain the session across program executions

        # Success Tokens
        success_tokens: List[str] = None,  # List of strings where at least one must be in the pages

        # Failure Tokens
        failure_tokens: List[str] = None,  # List of strings that must not be in the pages

        # Speed
        speed: str = None,
        # Gui hook
        parent: tk.Tk = None

) -> None:
    global SUCCESS_TOKENS, FAILURE_TOKENS, CONTEXT, PERSISTENT_SESSION, PARENT, DOMAIN, SLEEP_MIN, SLEEP_MAX
    PARENT = parent
    SUCCESS_TOKENS = success_tokens
    FAILURE_TOKENS = failure_tokens

    if (pagination_url_template is not None and follow_link_selector is not None) or (
            pagination_url_template is None and follow_link_selector is None and pagination_url_folders is None):
        raise ValueError("Either pagination_url_template or follow_link must be set, but not both.")
    if pagination_url_folders is not None and (detail_url_selector is None or base_url is None):
        raise ValueError("detail_url_selector or base_url is missing.")
    PERSISTENT_SESSION = persistent_session
    if login_url:
        DOMAIN = urlparse(login_url).netloc.split('@')[-1].split(':')[0] if login_url else None
    logging.basicConfig(
        filename=log_file,
        filemode='w',
        level=logging.INFO,
        format='%(asctime)s %(levelname)s %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    if log_handler_emitter:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
        console_handler.setFormatter(formatter)
        logging.getLogger().addHandler(console_handler)
        logging.getLogger().handlers[1].emit = log_handler_emitter
    cancelled = False
    if os.path.exists(PAGINATION_PAGES) or os.path.exists(DETAIL_PAGES):
        cancelled = show_file_management_dialog(PARENT)
    if cancelled:
        logging.info("Scrape was cancelled.")
        return
    _create_folders_and_files()
    logging.info("Starting browser.")
    speed_delay_intervals_seconds = {
        "Fast": (1, 3),
        "Normal": (3, 5),
        "Slow": (5, 10)
    }
    sleep_int = speed_delay_intervals_seconds[speed]
    SLEEP_MIN = sleep_int[0]
    SLEEP_MAX = sleep_int[1]
    logging.info(f"Request delay: {SLEEP_MIN} to {SLEEP_MAX} seconds.")
    with sync_playwright() as p:
        browser, page = _create_page(p, headless)
        if login_url:
            if not username:
                logging.info("Waiting for login...")
                wait_for_login_interaction = True
            proceed = _login(page, login_url, password_selector, username, username_selector,
                             wait_for_login_interaction)
            if not proceed:
                logging.info("User cancelled scrape.")
                return
        logging.info("Starting scrape.")
        if pagination_url_template:
            _scrape_paginated_pages(page, pagination_url_template, first_page, last_page, detail_url_selector)
        elif pagination_url_folders:
            _scrape_from_folder(page, pagination_url_folders, detail_url_selector, base_url)
        else:
            _crawl(page, follow_link_selector, start_page, follow_if_contains)
        if persistent_session:
            save_session(CONTEXT)
        browser.close()
