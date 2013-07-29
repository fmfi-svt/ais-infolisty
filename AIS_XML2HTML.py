#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Convertor from AIS XML format to HTML.

Autor: Kristian Valentin <valentin.kristian@gmail.com>
Docs: see README

# TODO ak je predmet vo viacerych informacnych listoch, prepisuje sa viac krat
"""

from xml.dom import minidom
import xml.etree.ElementTree as ET
import re
from string import Template
import sys
import glob 
import os.path

import utils

SP = {'FYZ': u'Fyzika', 'BMF': u'Biomedicínska fyzika',
      'OZE': u'Obnoviteľné zdroje energie a environmentálna fyzika',
      'MAT': 'Matematika', 'EFM': u'EFM - ekonomická a finančná matematika',
      'MMN': u'Manažérska matematika', 'PMA': 'Poistná matematika',
      'INF': u'Informatika', 'AIN': u'Aplikovaná informatika',
      'UXX': u'Spoločný pedagogicko-psychologický základ',
      'UDG': u'Deskriptívna geometria','UFY': u'Fyzika','UIN': u'Informatika',
      'UMA': u'Matematika',
      # Mgr.
      'FMB': u'Biomedicínska fyzika','FAA': u'Astronómia a astrofyzika',
      'FBF': u'Biofyzika a chemická fyzika',
      'FOZ': u'Environmentálna fyzika a obnoviteľné zdroje energie',
      'FFP': u'Fyzika plazmy','FTP': u'Fyzika tuhých látok',
      'FFZ': u'Fyzika Zeme a planét','FJF': u'Jadrová a subjadrová fyzika',
      'FMK': u'Meteorológia a klimatológia',
      'FOL': u'Optika, lasery a optická spektroskopia',
      'FTF': u'Teoretická fyzika',
      'PMS': u'Pravdepodobnosť a matematická štatistika',
      'MPG': u'mAIN - aplikovaná informatika','IKV': u'Kognitívna veda'
      }

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
                '_Z_', 'garantiPredmetu', '_L_', '_P_', '_O_', '_S_',
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

        # pridavam -- (pomlcka) ak je prazdna hodnota
        #for k in d.iterkeys():
        #    if d[k] == '':
        #        d[k] = '&nbsp;&ndash;'

	# niektore polia sa maju schovat ak su prazdne
	hide = {'podmienujucePredmety': u'Podmieňujúce predmety',
                'vylucujucePredmety': u'Vylučujúce predmety',
                '_O_': u'Obsahová prerekvizita',
                '_S_': 'Sylabus predmetu'}
        for e in hide.iterkeys():
            if not (d[e].strip() == '' or d[e] == None):
                d[e] = u"""
            <tr>
                <td colspan="3"><strong>%s</strong>: %s</td>
            </tr>""" % (hide[e], d[e])
        
        # uprava _VH_
        if not d['_VH_'] == '':
            d['_VH_'] = d['_VH_'] + u' (priebežné/záverečné)'

        data.append(d)

    # nacitanie HTML sablony
    tpl = open(os.path.join(sys.path[0], 'template_table.html'), 'r')
    html_tpl = Template(tpl.read().decode('utf8'))
    tpl.close()

    # zapis do suborov
    for i in xrange(len(data)):
        kod_predmetu = data[i]['kod']

        html = html_tpl.safe_substitute(data[i])

	filename = '%s.html' % kod_predmetu
        if output_path is not None:
	    path = os.path.join(output_path, filename)
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
