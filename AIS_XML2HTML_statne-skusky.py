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


def process_file(filename, output_path=None, lang='sk', verbose=True):
    xmldoc = ET.parse(filename)
    root = xmldoc.getroot()
    organizacnaJednotka = root.find('organizacnaJednotka').text
    ilisty = root.find('informacneListy')
    if verbose:
        print "  Nasiel som %d informacnych listov." % len(ilisty.findall('informacnyList'))

    # elementy, ktore sa budu parsovat z XML-ka
    # kluc => XPath (kluc sa pouziva neskor v template)
    elements = {'kod': 'kod', 'nazov': 'nazov', 'kredit': 'kredit',
                'sposobUkoncenia': 'sposobUkoncenia',
                'studijnyProgram': 'studijneProgramy/studijnyProgram/popis',
                'datumSchvalenia': 'datumSchvalenia', 'obsahovaNapln': '_ON_/texty',
                'vahaHodnotenia': '_VH_/texty', 'garanti': 'garanti/garant/plneMeno'}
    data = []

    # spracovanie informacnych listov jednotlivych predmetov
    for il in ilisty.findall('informacnyList'):
        # preskocime predmety, ktore nie su statne skusky
        if il.find('_ON_') is None:
            continue
        d = {'lang' : lang, 'organizacnaJednotka': organizacnaJednotka}
        for key, path in elements.iteritems():
            if il.find(path) is not None:
                if path.startswith('_'):
                    d[key] = utils.get_text(il.find(path))
                elif key == 'studijnyProgram':
                    d[key] = [el.text for el in il.findall(path)]
                else:
                    d[key] = il.find(path).text
            else:
                d[key] = ''

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
    for course in data:
        kod_predmetu = course['kod']

        html = html_tpl.render(course)

	filename = '%s.html' % kod_predmetu
        if output_path is not None:
	    path = os.path.join(output_path, filename)
            if not os.path.exists(output_path):
                os.mkdir(output_path)
        else:
	    path = filename
        with open(path, 'w') as f:
            f.write(html.encode('utf8'))


def main(filenames, output_path=None, lang='sk', verbose=True):
    if verbose:
        print "=== Spracuvam statne skusky ==="
    for f in filenames:
        if verbose:
            print "Spracuvam subor '%s'..." % f
        process_file(f, output_path, lang=lang, verbose=verbose)
    if verbose:
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
