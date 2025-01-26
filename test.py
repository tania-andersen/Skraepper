from playwright.sync_api import sync_playwright

def run_test():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)  # Launch Chromium in headless mode
        page = browser.new_page()
        page.goto("https://example.com")
        print("Title of the page:", page.title())  # Print the page title
        browser.close()

if __name__ == "__main__":
    run_test()
