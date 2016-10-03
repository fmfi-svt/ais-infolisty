import re

# code_regexp = r'[\w+-\.]+/([^/]*/[\d]{2})'
code_regexp = r'[^/]+/([^/]*/[\d]{2})'

def parse_code(code):
    """
    Get the short course code from the full course code.
    """
    if re.search(r'/.+/', code):
        # ak obsahuje FMFI, tak skracuj
        m=re.match(r'[^/]*FMFI[^/]*/([^/]+/[\d]{2})',code)
        if m:
            return m.group(1)
        else:
            return code
    else:
        return False


def replace_codes(text, lang='sk', add_links=False, courses={}, and_symbol=', '):
    """
    Replace all occurences of full course codes with short course codes.
    """

    if not text:
        return ""
    
    m=re.split('([()\s]+)',text,flags=re.UNICODE)
    result=""
    for w in m:
        shortcode = parse_code(w)
        if shortcode:
            if add_links:
                title = '%s %s' % (shortcode, courses[shortcode]) if shortcode in courses else shortcode
                result+=make_link_from_code(shortcode, lang=lang, title=title)
            else:
                result+=shortcode
        else:
            result+=w

    return result


def get_text(node):
    """
    Get text from elements with multiple <p> tags.
    """
    if not node.findall('p'):
        return node.text
    return ''.join('<p>'+n.text+'</p>' for n in node.findall('p'))

def get_url(code, lang='sk'):
    if code == '' or not lang in ['sk', 'en']:
        return False
    # return "https://sluzby.fmph.uniba.sk/infolist/%s/%s.html" % (lang, code)
    link = code.replace("/","_")
    return "%s.html" % (link)

def make_link_from_code(code, title='', lang='sk'):
    url = get_url(code, lang)
    return make_link(url, text=title)

def make_link(href, text, title=''):
    if not title == '':
        title = ' title="%s"' % title
    return '<a href="%s"%s>%s</a>' % (href, title, text)

