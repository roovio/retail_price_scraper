import re

def _get_base_card(search_term: str) -> str:
    return search_term.replace('Ti', '').replace('LHR','').replace('Super','').strip()


def match_gpu_name_search_keyword(entry: str, search_term: str) -> bool:
    base_card = _get_base_card(search_term)
    is_lhr = 'LHR' in search_term
    is_ti = 'Ti' in search_term
    is_super = 'Super' in search_term

    base_card_regex_pattern = base_card.replace(r' ',r' *')
 
    if not re.search(base_card_regex_pattern, entry):
        return  False
    if is_lhr:
        if 'LHR' not in entry:
            return False
    else:
        if 'LHR' in entry:
            return False
    if is_ti:
        if not re.search(base_card_regex_pattern + r' *T[iI]', entry):
            return False
    else:
        if re.search(base_card_regex_pattern + r' *T[iI]', entry):
            return False
    if is_super:
        if not ( re.search(base_card_regex_pattern + r'S', entry) or re.search(base_card_regex_pattern + r' *Super', entry) ):
            return False
    else:
        if re.search(base_card_regex_pattern + r'S', entry) or re.search(base_card_regex_pattern + r' *Super', entry):
            return False
    return True


def get_query_string_for_search_keyword(search_term: str) -> str:
    return _get_base_card(search_term)


def matches_search_keyword(entry: str, search_term: str) -> bool:
    return match_gpu_name_search_keyword(entry, search_term)