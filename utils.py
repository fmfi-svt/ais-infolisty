import re

code_regexp = r'[\w]+\.[^/]+/([^/]*/[\d]{2})'

def parse_code(code):
    """
    Get the short course code from the full course code.
    """
    newcode = ''

    m = re.match(code_regexp, code)

    if m:
        newcode = m.group(1)
    else:
        newcode = ''

    newcode = newcode.replace("/","_")

    return newcode

def replace_codes(text, lang='sk', add_links=False, courses={}, and_symbol=', '):
    """
    Replace all occurences of full course codes with short course codes.
    """
    def repl(m):
        code = m.group(1)
        if not add_links:
            return code
        title = '%s %s' % (code, courses[code]) if code in courses else code
        return make_link_from_code(code, lang=lang, title=title)

    if text is None or len(text) == 0:
        return ''

    return re.sub(code_regexp, repl, text).replace(',', and_symbol)

def get_text(node):
    """
    Get text from elements with multiple <p> tags.
    """
    if not node.findall('p'):
        return node.text
    return ''.join('<p>'+n.text+'</p>' for n in node.findall('p'))

def get_url(code, lang='sk'):
    lang = lang.upper()
    if code == '' or not lang in ['SK', 'EN']:
        return False
    return "https://sluzby.fmph.uniba.sk/infolist/%s/%s.html" % (lang, code)

def make_link_from_code(code, title='', lang='sk'):
    url = get_url(code, lang)
    return make_link(url, text=title)

def make_link(href, text, title=''):
    if not title == '':
        title = ' title="%s"' % title
    return '<a href="%s"%s>%s</a>' % (href, title, text)

