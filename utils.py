import re

def parse_code(code):
    """
    Get the shor course code from the full course code.
    """
    m = re.match(r'.*/(.*)/.*', code)
    if m:
        return m.group(1)
    else:
        return ''

def replace_codes(text, lang='sk', add_links=False, courses={}, glue=', '):
    """
    Replace all occurences of full course codes with short course codes.
    """
    if len(text) == 0:
        return ''
    parts = text.split(' ')
    new_parts = []
    for p in parts:
        np = parse_code(p)
        if np is not '':
            if add_links:
                title = '%s %s' % (np, courses[np]) if np in courses else np
                np = make_link_from_code(np, lang=lang, title=title)
            new_parts.append(np)

    return glue.join(new_parts)

def get_text(node):
    """
    Get text from elements with multiple <p>.
    """
    t = []
    for n in node.findall('p'):
        if node.tag == '_VH_':
            t.append(n.text)
        else:
            t.append('<p>'+n.text+'</p>')
    return ''.join(t)

def get_url(code, lang='sk'):
    lang = lang.upper()
    if code == '' or not lang in ['SK', 'EN']:
        return false
    return "https://sluzby.fmph.uniba.sk/infolist/%s/%s.html" % (lang, code)

def make_link_from_code(code, title='', lang='sk'):
    url = get_url(code, lang)
    return make_link(url, text=title)

def make_link(href, text, title=''):
    if not title == '':
        title = ' title="%s"' % title
    return '<a href="%s"%s>%s</a>' % (href, title, text)
