# Copyright Tania Andersen 2025 @taniaandersen.bsky.social
# Licence: GNU AFFERO GENERAL PUBLIC LICENSE Version 3 https://www.gnu.org/licenses/agpl-3.0.en.html

import re

SYNTAX_ERROR_COLOR = "indianred"


def handle_syntax_error(e, update_status_bar):
    error_message = (type(e).__name__ + ". " + str(e)).replace("\n", " ")

    # Handle ConstructorError (YAML error)
    constructor_error_pattern = r"constructor for the tag '([!]\w+)'.*line (\d+), column (\d+):"
    constructor_error_match = re.search(constructor_error_pattern, error_message)

    if constructor_error_match:
        bad_token = constructor_error_match.group(1)  # Extracts the bad token (e.g., '!hygge')
        line_number = int(constructor_error_match.group(2))  # Extracts the line number
        column_number = int(constructor_error_match.group(3))  # Extracts the column number

        # Strip whitespace from the bad token (optional)
        bad_token_stripped = bad_token.strip()

        # Update the status bar with the error message
        user_error_msg = f'Invalid selector "{bad_token_stripped}" at line:col {line_number}:{column_number}.'
        update_status_bar(user_error_msg, SYNTAX_ERROR_COLOR)

    # Handle ValueError (invalid value type)
    elif "Only string or dicts accepted values for" in error_message:
        # Extract the key from the error message
        key_pattern = r"Only string or dicts accepted values for '(\w+)'"
        key_match = re.search(key_pattern, error_message)

        if key_match:
            key = key_match.group(1)  # Extracts the key (e.g., 'test')
            user_error_msg = f'Missing value or block indent after: "{key}".'
            update_status_bar(user_error_msg, SYNTAX_ERROR_COLOR)

    # Handle ScannerError (YAML syntax error - missing colon)
    elif "while scanning a simple key" in error_message and "could not find expected ':'" in error_message:
        # Extract the token, line, and column from the error message
        scanner_error_pattern = r"line (\d+), column (\d+):\s+(\S+)\s+\^"
        scanner_error_match = re.search(scanner_error_pattern, error_message)

        if scanner_error_match:
            line_number = int(scanner_error_match.group(1))  # Extracts the line number
            column_number = int(scanner_error_match.group(2))  # Extracts the column number
            token = scanner_error_match.group(3)  # Extracts the token (e.g., "dyt")
            user_error_msg = f'Missing ":" after field "{token}" at line:col {line_number}:{column_number}.'
            update_status_bar(user_error_msg, SYNTAX_ERROR_COLOR)

    # Handle SelectorSyntaxError (CSS selector syntax error)
    elif "SelectorSyntaxError" in error_message and "line" in error_message:
        # Extract the bad token from the error message\s*\^"
        selector_error_pattern = r"line \d+:\s*(.*?)\s*\^"
        selector_error_match = re.search(selector_error_pattern, error_message)

        if selector_error_match:
            bad_token = selector_error_match.group(1)  # Extracts the bad token (e.g., ">")
            user_error_msg = f'Invalid CSS selector: "{bad_token}".'
            update_status_bar(user_error_msg, SYNTAX_ERROR_COLOR)

    # Handle custom ValueError (missing 'selector' field)
    elif "ValueError." in error_message and "Missing 'selector' field in block" in error_message:
        # Extract the part after "ValueError."
        error_detail = error_message.split("ValueError.", 1)[-1].strip()
        update_status_bar(error_detail, SYNTAX_ERROR_COLOR)

    # Handle ParserError (YAML parsing error)
    elif "ParserError." in error_message and "while parsing a block mapping" in error_message:
        # Extract all line and column matches
        parser_error_pattern = r"line (\d+), column (\d+):"
        parser_error_matches = re.findall(parser_error_pattern, error_message)

        if parser_error_matches:
            # Get the last match (line and column)
            line_number, column_number = parser_error_matches[-1]

            # Extract the unexpected character (e.g., ">")
            # Look for the character after the last "line X, column Y:" occurrence
            unexpected_char_pattern = rf"line {line_number}, column {column_number}:\s*([^\s]+)"
            unexpected_char_match = re.search(unexpected_char_pattern, error_message)

            if unexpected_char_match:
                unexpected_char = unexpected_char_match.group(1)  # Extract the unexpected character
                user_error_msg = f'Block end or new field expected, found "{unexpected_char}" at line:col {line_number}:{column_number}'
                update_status_bar(user_error_msg, SYNTAX_ERROR_COLOR)

    # Handle ScannerError (YAML scanning error)
    elif "ScannerError." in error_message and "while scanning a block scalar" in error_message:
        # Extract the line and column where the error occurred
        scanner_error_pattern = r"line (\d+), column (\d+):"
        scanner_error_matches = re.findall(scanner_error_pattern, error_message)

        if scanner_error_matches:
            # Get the last match (line and column)
            line_number, column_number = scanner_error_matches[-1]

            # Extract the unexpected character (e.g., ">")
            unexpected_char_pattern = rf"line {line_number}, column {column_number}:\s*([^\s]+)"
            unexpected_char_match = re.search(unexpected_char_pattern, error_message)

            if unexpected_char_match:
                unexpected_char = unexpected_char_match.group(1)  # Extract the unexpected character
                user_error_msg = f'Block end or new field expected, found "{unexpected_char}" at line:col {line_number}:{column_number}'
                update_status_bar(user_error_msg, SYNTAX_ERROR_COLOR)

    elif "AttributeError. 'NoneType' object has no attribute 'replace'" in error_message:
        user_error_msg = "Selector is missing."
        update_status_bar(user_error_msg, SYNTAX_ERROR_COLOR)

    elif "ScannerError." in error_message and "mapping values are not allowed here" in error_message:
        # Extract line, column, and the bad token
        error_pattern = r"line (\d+), column (\d+):\s*([^\s]+)"
        match = re.search(error_pattern, error_message)

        if match:
            line_number, column_number, bad_token = match.groups()
            user_error_msg = f"Field not allowed here: '{bad_token}' at line:col {line_number}:{column_number}"
            update_status_bar(user_error_msg, SYNTAX_ERROR_COLOR)

    elif "Bad code: Cannot parse key-values." in error_message:
        update_status_bar("Incomplete directive.", SYNTAX_ERROR_COLOR)

    elif "No success token in contains directive" in error_message:
        update_status_bar("Success token missing after contains.", SYNTAX_ERROR_COLOR)

    else:
        print(f"Unhandled error: {error_message}")
        raise e