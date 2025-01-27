# Pagination options

This section describes the pagination options available in the program.

## Pagination url

Specifies the URL template to use for pagination. The template should include a placeholder for the page number, represented by an asterisk (`*`).

For example, if the pagination URLs for a website are of the form `https://example.com/page/1`, `https://example.com/page/2`, etc., then the pagination
URL template would be `https://example.com/page/*`.

## First page

Specifies the number of the first page to scrape.

## Last page

Specifies the number of the last page to scrape.

## Detail page selector

Specifies the CSS selector to use to extract detail URLs from each page

## Login/GDPR Page

Specifies a page where the scraper will wait for user interaction. Click
"proceed" in the dialog after user interaction, such as login or clicking a cookie button.

## With session

Saves the session cookies and state for multiple sessions. If a scrape takes login,
the session will most likely save a login-cookie.

## Headless

Will hide the browser window. Only for experienced users, and use with care.

## Success tokens

A comma-separated list of words that must be found on the pages.

## Failure tokens

A comma-separated list of words that must not be found on the pages.

## Speed

Time between scrapes. `Slow` is easiest on the server.

## Scrape

Click the button to start the scrape.

# Extract options

This section describes the extraction options available in the program.

## Folder

The folder to extract from, usually `detail_pages`.

## Extraction

The extraction Skraeppex code.

# Refine options

This section describes the options available for developing Skraeppex extraction code.

## Test pages<a name="Test">&nbsp;</a>

Test pages for developing Skraeppex code, usually one or two from `detail_pages`.
You can select more than one file by using Ctrl/Command and Shift keys.

## Extract

The Skraeppex code to use for extraction. The extracted data will be displayed in the
lower part of the window, as you type along. Red text in the bottom will tell you if
you have made a mistake in the code.


# About

About Scraepper version 0.9.

Copyright © Tania Andersen 2025.

License: Affero General Public License https://github.com/tania-andersen/Skraepper/blob/main/LICENSE

------------------------------------

Scraepper uses these fine softwares:


- Python

  License: https://docs.python.org/3/license.html


- Playwright

  License: https://github.com/microsoft/playwright/blob/main/LICENSE


- Beautifulsoup

  License: https://github.com/josepmartorell/BeautifulSoup4/blob/master/LICENSE


- Pandas

  License: https://github.com/pandas-dev/pandas/blob/main/LICENSE


- Pyinstaller

  License: https://github.com/pyinstaller/pyinstaller/blob/develop/COPYING.txt

-----------------------------

*Der Lachende<br>
Hat die furchtbare Nachricht</br>
Nur noch nicht empfangen.*

– Brecht

