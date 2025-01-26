# Pagination Options

This section describes the pagination options available in the program.

## Pagination URL Template

Specifies the URL template to use for pagination. The template should include a placeholder for the page number, represented by an asterisk (`*`).

For example, if the pagination URLs for a website are of the form `https://example.com/page/1`, `https://example.com/page/2`, etc., then the pagination 
URL template would be `https://example.com/page/*`.

## First Page

Specifies the number of the first page to scrape.

## Last Page

Specifies the number of the last page to scrape.

## Detail URL Selector<a name="Detail%20URL%20Selector"></a> 

Specifies the CSS selector to use to extract detail URLs from each page

# Login/GDPR Page

Specifies a page where the scraper will wait for user interaction. Click 
"proceed" in the dialog after user interaction, such as login or a cookie button.

# With session

Saves the session cookies and state for multiple sessions. If a scrape takes login,
the session might save a login-cookie. 

# Headless

Will hide the browser window. Only for experienced users, and use with care.