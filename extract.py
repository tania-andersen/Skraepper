import warnings
from tkinter import messagebox

import pandas as pd
import yaml
from typing import List, Callable
import re
import numpy as np
import html as h
import os
import csv
import re
from bs4 import BeautifulSoup
from typing import List, Union, Pattern
from collections import OrderedDict

OUTPUT_CSV = 'output.csv'
DETAIL_PAGES = 'detail_pages'
NO_DUPLICATES = True
fillup = []
filldown = []
cfillup = []
dropna = False
_COLUMN_NAMES = []
FINAL_COLUMNS = None


def _extract_fields(data, fields):
    if not isinstance(data, dict):
        return
    for key, value in data.items():
        if key != "selector":
            fields[key] = None
        if isinstance(value, dict):
            _extract_fields(value, fields)


def _get_fieldnames(input_as_dict):
    fields = OrderedDict()
    _extract_fields(input_as_dict, fields)
    return list(fields.keys())


def _collect_text_between_tags(text):
    text = remove_newlines(text)
    text = re.sub(r'<[^>]*>', '<>', text)
    text_list = re.findall(r'<>([^<]*)', text)
    text_list = list(dict.fromkeys(text_list))
    text_list = [string for string in text_list if string.strip()]
    text_list = [element.strip() for element in text_list]
    text = ' '.join(text_list)
    return h.unescape(text)


def _replace_char_in_dict_value(d, char_to_replace, replacement_char):
    # Return immediately if d is not a dictionary
    if not isinstance(d, dict):
        return
    for k, v in d.items():
        if isinstance(v, dict):
            _replace_char_in_dict_value(v, char_to_replace, replacement_char)
        elif isinstance(v, str):
            d[k] = v.replace(char_to_replace, replacement_char)


def _find_matching_nodes(soup: BeautifulSoup, success_token: Union[str, Pattern]) -> List[str]:
    matching_nodes = []
    for node in soup.descendants:
        if isinstance(node, str):
            if node.strip() == "":
                continue
            if isinstance(success_token, str) and success_token in node:
                matching_nodes.append(node.strip())
            elif isinstance(success_token, Pattern) and re.search(success_token, node):
                matching_nodes.append(node.strip())
    return matching_nodes


def _input_to_dict(yaml_str: str, error_hook=None):
    forbidden_chars = ['¤', '§', '£']
    if any(char in yaml_str for char in forbidden_chars):
        raise ValueError("Input contains reserved characters '¤', '§', '£'.")
    yaml_str = yaml_str.replace("#", "¤")
    yaml_str = yaml_str.replace("[", "§")
    yaml_str = yaml_str.replace("]", "£")
    input_dict = yaml.load(yaml_str, Loader=yaml.FullLoader)
    _replace_char_in_dict_value(input_dict, "¤", "#")
    _replace_char_in_dict_value(input_dict, "§", "[")
    _replace_char_in_dict_value(input_dict, "£", "]")
    return input_dict


def _concatenate_unique_nodes(matching_nodes):
    unique_nodes = list(dict.fromkeys(matching_nodes))
    if len(unique_nodes) == 1:
        text = unique_nodes[0]
    else:
        i = 1
        text = ''
        for text_node in unique_nodes:
            text = remove_newlines(text)
            text = text + "\n<CUNODE " + str(i) + ">\n" + text_node  # duplicates?
            i += 1
    return text


def _raise_value_error_selectors_not_allowed():
    raise ValueError('Selectors not allowed with "contains" field.')


def create_column(col_name, df):
    df[col_name] = [None] * len(df.index)


def append_row(df):
    df.loc[len(df)] = [None] * len(df.columns)


def append_found_text(col_name, df, text):
    if len(df) > 0:
        row = len(df) - 1
    else:
        row = len(df)
    df.loc[row, col_name] = text


def remove_newlines(text):
    return text.replace('\n', '')


def extract_text(html_nodes, nodes=None):
    global NO_DUPLICATES
    text = ''
    if len(html_nodes) == 1:
        if NO_DUPLICATES:
            text = _collect_text_between_tags(str(html_nodes[0]))
        if text == '':
            text = '<EMPTY_NODE>'
    else:
        # More matches
        text_nodes = [node.text.strip() for node in html_nodes]
        i = 1
        text = ''
        for text_node in text_nodes:
            if nodes is not None and i == nodes:
                return remove_newlines(text_node)
            text = remove_newlines(text)
            text = text + "\n<NODE " + str(i) + ">\n" + text_node  # duplicates?
            i += 1
    return text


def get_keys_starting_with_dash(my_dict):
    result = []
    for key, value in my_dict.items():
        if isinstance(value, dict):
            result.extend(get_keys_starting_with_dash(value))
        if key.startswith("-"):
            result.append(key)
    return result


def _str_to_list(input_string):
    return [item.strip() for item in input_string.split(",")]


def extract_fields(fields, soup, df):
    for field_name in fields:
        if field_name == 'selector' or field_name == 'nodes':
            continue
        if field_name in ['fillup', 'filldown', 'cfillup']:
            global fillup, filldown, cfillup
            if field_name == 'fillup':
                fillup = _str_to_list(fields[field_name])
            elif field_name == 'filldown':
                filldown = _str_to_list(fields[field_name])
            elif field_name == 'cfillup':
                cfillup = _str_to_list(fields[field_name])
            continue
        if field_name == "dropna":
            global dropna
            if isinstance(fields[field_name], bool):
                dropna = fields[field_name]
            else:
                dropna = False
            continue
        selector_or_subsection = fields[field_name]
        if isinstance(selector_or_subsection, str):
            extract_selector_field(df, field_name, selector_or_subsection, soup)
        else:
            if not isinstance(selector_or_subsection, dict):
                raise ValueError(f"Only string or dicts accepted values for '{field_name}' ")
            if 'selector' not in selector_or_subsection:
                raise ValueError(f"Missing 'selector' field in block {field_name}")
            extract_block(df, field_name, selector_or_subsection, soup)
    append_row(df)


def extract_block(df, block_name, block, soup):
    html_nodes = soup.select(block['selector'])
    contains_filter = False
    if 'contains' in block:
        contains_filter = True
        success_token = block['contains']
        if not success_token:
            raise ValueError("No success token in contains directive")
        html_nodes = filter_nodes(html_nodes, success_token, negate=False)
    elif 'contains-not' in block:
        contains_filter = True
        failure_token = block['contains-not']
        html_nodes = filter_nodes(html_nodes, failure_token, negate=True)
    nodes = None
    if 'nodes' in block:
        nodes = block['nodes']
    if (not contains_filter) or (contains_filter and html_nodes):
        if not block_name.startswith("-"):  # only blocks can have '-'
            text = extract_text(html_nodes, nodes)  # <- nodes here
            append_found_text(block_name, df, text)  # not tested!
        for html_node in html_nodes:
            extract_fields(block, html_node, df)


def filter_nodes(html_nodes, token, negate=False):
    if not token or not isinstance(token, str):
        raise ValueError("Token must be a non-empty string.")
    filtered_nodes = []
    regex_pattern = None
    if token.startswith("regex!"):
        regex_pattern = token.split("!")[-1].strip()
    for html_node in html_nodes:
        if regex_pattern:
            match = re.search(regex_pattern, html_node.text)
        else:
            match = token.lower() in html_node.text.lower()
        if (match and not negate) or (not match and negate):
            filtered_nodes.append(html_node)
    return filtered_nodes


def _conditional_fill(df, cfillup):
    for col in cfillup:
        first_non_blank = df[col].ne('').idxmax()
        sub_col = df[col].iloc[first_non_blank:]
        sub_col_filled = sub_col.replace('', np.nan).bfill()
        df.loc[first_non_blank:, col] = sub_col_filled
    return df


def extract_selector_field(df, field_name, selector, soup):
    selector = selector.strip()
    assert field_name != "nodes", "field is nodes."
    if selector.startswith("contains!"):
        next_token = selector.split('!', 1)[-1].strip()
        if next_token.startswith("regex!"):
            regex_pattern = next_token.split("!")[-1].strip()
            matching_nodes = _find_matching_nodes(soup, re.compile(regex_pattern))
        else:
            matching_nodes = _find_matching_nodes(soup, next_token)
        text = _concatenate_unique_nodes(matching_nodes)
    elif selector.startswith("regex!"):
        regex = selector.split('!', 1)[-1].strip()

        try:
            pattern = re.compile(regex)
        except re.error as e:
            raise ValueError(f"Invalid regex: {e}") from e

        get_text = _collect_text_between_tags(str(soup))
        matches = pattern.findall(get_text)
        text = ''
        if len(matches) > 1:
            text = ''.join(f"<NODE {i + 1}>{match}" for i, match in enumerate(matches))
        elif len(matches) == 1:
            text = matches[0]
    else:
        html_nodes = soup.select(selector)
        text = extract_text(html_nodes)
    append_found_text(field_name, df, text)


def process_file(fields, filename, folder_path, write_out=True):
    global _COLUMN_NAMES, dropna, FINAL_COLUMNS
    file_path = os.path.join(folder_path, filename)

    #REFAC
    #with open(file_path, mode='r', encoding='utf-8') as file:
    #    html = file.read()

    try:
        with open(file_path, mode='r', encoding='utf-8') as file:
            html = file.read()
    except Exception as e:
        messagebox.showerror("Error", f"Failed to read file: {e}")
        return

    #REFAC SLUT

    soup = BeautifulSoup(html, 'html.parser')
    df = pd.DataFrame(columns=_COLUMN_NAMES)
    extract_fields(fields, soup, df)
    fields_with_dash = get_keys_starting_with_dash(fields)
    reserved_words = ['contains', 'nodes', 'fillup', 'filldown', 'cfillup', 'dropna']
    for word in reserved_words:
        fields_with_dash.append(word)
    for key in fields_with_dash:
        if key in df.columns:
            df = df.drop(key, axis=1)
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", FutureWarning)
            df = df.replace(r'^\s*$', np.nan, regex=True)
            df = df.dropna(how='all')
            df = df.apply(lambda col: col.ffill() if col.name in filldown else col)
            df = df.apply(lambda col: col.bfill() if col.name in fillup else col)
            pd.set_option('display.max_colwidth', 15)
            df = _conditional_fill(df, cfillup)
            if dropna:
                df = df.dropna()
            df.fillna("", inplace=True)
    except Exception as e:
        raise e
    df = df.drop_duplicates()
    FINAL_COLUMNS = list(df.columns)
    if write_out:
        with open(OUTPUT_CSV, 'a', encoding='utf-8', newline='') as f:
            df.to_csv(f, header=False, index=False, encoding='utf-8')
    else:
        return df


def extract(input_code, folders_or_files: List[str], no_duplicates=True, error_hook=None, testing=False
            , progress_callback: Callable[[float], None] = None):
    global NO_DUPLICATES, _COLUMN_NAMES, fillup, cfillup, filldown, dropna
    fillup = []
    filldown = []
    cfillup = []
    dropna = False
    _COLUMN_NAMES = _get_fieldnames(_input_to_dict(input_code, error_hook=error_hook))
    NO_DUPLICATES = no_duplicates
    if (not testing) and os.path.exists(OUTPUT_CSV):
        os.remove(OUTPUT_CSV)
    fields_as_dict = _input_to_dict(input_code)

    if not isinstance(fields_as_dict, dict):
        raise ValueError("Bad code: Cannot parse key-values.")

    if (not isinstance(folders_or_files, list)) and os.path.isdir(folders_or_files):
        folder_path = folders_or_files
        total_files = len(os.listdir(folders_or_files))
        if total_files == 0:
            return
        for i, filename in enumerate(os.listdir(folder_path)):
            process_file(fields_as_dict, filename, folder_path)
            progress_callback(i / total_files)
        with open(OUTPUT_CSV, 'r', encoding='utf-8') as f:
            content = f.read()
        with open(OUTPUT_CSV, 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(FINAL_COLUMNS)
            f.write(content)
    elif testing:
        concat_df = pd.DataFrame()
        for file_path in folders_or_files:
            dir_name, file_name = os.path.split(file_path)
            df = process_file(fields_as_dict, file_name, dir_name, write_out=False)
            concat_df = pd.concat([concat_df, df])
        return concat_df
