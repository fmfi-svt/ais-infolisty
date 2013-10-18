#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Convertor from AIS XML format to HTML.

Author: Kristian Valentin <valentin.kristian@gmail.com>
Docs: see README

# TODO ak je predmet vo viacerych informacnych listoch, prepisuje sa viac krat
"""

from xml.dom import minidom
import xml.etree.ElementTree as ET
import re
from jinja2 import Template, Environment, FileSystemLoader
import sys
import glob
import os.path

import utils


# translations
trans = {'sk': {'a': 'a'}, 'en': {'a': 'and'}}

def extract_courses(filename, courses):
    xmldoc = ET.parse(filename)
    root = xmldoc.getroot()
    ilisty = root.find('informacneListy')

    for il in ilisty.findall('informacnyList'):
        if il.find('kod') is not None:
            kod = il.find('kod').text
            nazov = il.find('nazov').text

            kod = utils.parse_code(kod)
            courses[kod] = nazov

    return courses

def process_file(filename, output_path=None, courses=None, lang='sk'):
    xmldoc = ET.parse(filename)
    root = xmldoc.getroot()
    organizacnaJednotka = root.find('organizacnaJednotka').text
    ilisty = root.find('informacneListy')
    print "  Nasiel som %d informacnych listov." % len(ilisty.findall('informacnyList'))

    # elementy, ktore sa budu parsovat z XML-ka
    elements = ('kod', 'nazov', 'kredit', 'sposobUkoncenia', 'sposobVyucby',
                'rozsahTyzdenny', 'rozsahSemestranly', 'obdobie', 'jazyk',
                'studijnyProgram', 'podmienujucePredmety', 'doplujuceUdaje',
                'zabezpecuju', 'datumSchvalenia', '_VH_', '_SO_', '_C_',
                '_Z_', 'garanti', '_L_', '_P_', '_O_', '_S_',
                'vylucujucePredmety')
    data = []

    # spracovanie informacnych listov jednotlivych predmetov
    for il in ilisty.findall('informacnyList'):
        d = {'lang' : lang, 'organizacnaJednotka': organizacnaJednotka}
        for e in elements:
            if il.find(e) is not None:
                if e.startswith('_'):
                    d[e] = utils.get_text(il.find(e))
                else:
                    d[e] = il.find(e).text
            else:
                d[e] = ''

        # uprava kodov predmetov
        d['kod'] = utils.parse_code(d['kod'])
        d['podmienujucePredmety'] = utils.replace_codes(d['podmienujucePredmety'], lang, add_links=True, courses=courses, and_symbol=trans[lang]['a'])
        d['vylucujucePredmety'] = utils.replace_codes(d['vylucujucePredmety'], lang, add_links=True, courses=courses)
        d['_O_'] = utils.replace_codes(d['_O_'], lang, add_links=True, courses=courses)

        data.append(d)

    # nacitanie HTML sablony
    env = Environment(loader=FileSystemLoader('templates'))

    tpl_name = 'template_table_%s.html' % lang
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
    print "Extrahujem nazvy predmetov...",
    courses = {}
    for f in filenames:
        courses = extract_courses(f, courses)
    print "Hotovo."

    for f in filenames:
        print "Spracuvam subor '%s'..." % f
        process_file(f, output_path, courses, lang=lang)
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
