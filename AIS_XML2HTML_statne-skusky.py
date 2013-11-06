#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Convertor from AIS XML format to HTML.

Author: Kristian Valentin <valentin.kristian@gmail.com>
Docs: see README

"""

from xml.dom import minidom
import xml.etree.ElementTree as ET
from jinja2 import Template, Environment, FileSystemLoader
import sys
import glob
import os.path

import utils

def process_file(filename, output_path=None, lang='sk'):
    xmldoc = ET.parse(filename)
    root = xmldoc.getroot()
    organizacnaJednotka = root.find('organizacnaJednotka').text
    ilisty = root.find('informacneListy')
    print "  Nasiel som %d informacnych listov." % len(ilisty.findall('informacnyList'))

    # elementy, ktore sa budu parsovat z XML-ka
    elements = ('kod', 'nazov', 'kredit', 'sposobUkoncenia', 'studijnyProgram',
                'datumSchvalenia', '_ON_', '_VH_', 'garanti', 'jazyk')
    data = []

    # spracovanie informacnych listov jednotlivych predmetov
    for il in ilisty.findall('informacnyList'):
        d = {'lang' : lang, 'organizacnaJednotka': organizacnaJednotka}
        for e in elements:
            if il.find(e) is not None:
                if e.startswith('_'):
                    if e == '_VH_':
                        d[e] = il.find(e).findtext('texty')
                    else:
                        d[e] = ET.tostring(il.find(e).find('texty/*'))
                else:
                    d[e] = il.find(e).text
            else:
                d[e] = ''

        # jazyk
        if d['jazyk'] == '':
            d['jazyk'] = u'slovenský'

        # uprava kodov predmetov
        d['kod'] = utils.parse_code(d['kod'])

        data.append(d)

    # nacitanie HTML sablony
    script_abs_path = os.path.dirname(os.path.abspath(__file__))
    tpl_path = os.path.join(script_abs_path, 'templates')
    env = Environment(loader=FileSystemLoader(tpl_path))

    tpl_name = 'template_statne-skusky_table_%s.html' % lang
    html_tpl = env.get_template(tpl_name)

    # zapis do suborov
    for i in xrange(len(data)):
        kod_predmetu = data[i]['kod']

        html = html_tpl.render(data[i])

	filename = '%s.html' % kod_predmetu
        if output_path is not None:
	    path = os.path.join(output_path, filename)
            if not os.path.exists(output_path):
                os.mkdir(output_path)
        else:
	    path = filename
        f = open(path, 'w')
        f.write(html.encode('utf8'))
        f.close()

def main(filenames, output_path=None, lang='sk'):
    for f in filenames:
        print "Spracuvam subor '%s'..." % f
        process_file(f, output_path, lang=lang)
    print "Hotovo."


if __name__ == "__main__":

    import argparse

    parser = argparse.ArgumentParser(description='Coverts AIS XMLs into HTMLs.')
    parser.add_argument('input_path', metavar='input-path', help='path to input XMLs')
    parser.add_argument('output_path', metavar='output-path', help='path for HTML files to be stored')
    parser.add_argument('--lang', dest='lang', nargs='?', default='sk', help='language')

    args = parser.parse_args()

    xml_path = os.path.join(args.input_path, '*.xml')
    filenames = glob.glob(xml_path)
    main(filenames, args.output_path, lang=args.lang)
