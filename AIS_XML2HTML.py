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
import pprint


# translations
trans = {'sk': {'a': 'a'}, 'en': {'a': 'and'}}

def extract_courses(filename, courses):
    """Extract names and codes of all courses from an XML file containing infolists.

    Params:
        filename: path to the XML file
        courses: dict to write into

    Returns:
        dict of courses
    """
    try:
        xmldoc = ET.parse(filename)
        root = xmldoc.getroot()
        ilisty = root.find('informacneListy')

        for il in ilisty.findall('informacnyList'):
            if il.find('kod') is not None:
                kod = il.find('kod').text
                nazov = il.find('nazov').text

                kod = utils.parse_code(kod)
                courses[kod] = nazov
    except:
        print("Error: ", sys.exc_value)
    finally:
        return courses


def extract_infolists(filename, lang='sk', mode='regular', year='xxx', verbose=True):
    """Extract all infolists with all of their courses from a study program XML file.

    Params:
        filename: path to the XML file
        lang: language

    Returns:
        list of infolists with cou dics
    """
    xmldoc = ET.parse(filename)
    root = xmldoc.getroot()
    organizacnaJednotka = root.find('organizacnaJednotka').text
    vysokaSkola = root.find('vysokaSkola').text
    fakulta = root.find('fakulta').text
    ilisty = root.find('informacneListy')
    if verbose:
        print("  Nasiel som %d informacnych listov." % len(ilisty.findall('informacnyList')))

    # elementy, ktore sa budu parsovat z XML-ka
    # kluc => XPath (kluc sa pouziva neskor v template)
    elements = {'kod': 'kod',
                'nazov': 'nazov',
                'kredit': 'kredit',
                'sposobVyucby': 'sposobVyucby',
                'rozsahTyzdenny': 'rozsahTyzdenny',
                'rozsahSemestranly': 'rozsahSemestranly',
                'rokRocnikStudPlan': 'rokRocnikStudPlan',
                'kodSemesterStudPlan': 'kodSemesterStudPlan',
                'sposobUkoncenia': 'sposobUkoncenia',
                'studijneProgramy': 'studijneProgramy/studijnyProgram',
                'stupenPredmetu': 'stupenPredmetu',
                'studijnyProgram': 'studijneProgramy/studijnyProgram/popis',
                'podmienujucePredmety': 'podmienujucePredmety',
                'vylucujucePredmety': 'vylucujucePredmety',
                'doplujuceUdaje': 'doplujuceUdaje',
                'zabezpecuju': 'zabezpecuju',
                'strucnaOsnova': '_SO_/texty',
                'webstranka': '_URL_/texty/p',
                'ciel': '_C_/texty',
                'zaverecneHodnotenie': '_Z_/texty/p',
                'literatura': '_L_/texty',
                'priebezneHodnotenie': '_P_/texty/p',
                'obsahovaPrerekvizita': '_O_/texty',
                'sylabus': '_S_/texty',
                'datumSchvalenia': 'datumSchvalenia', 
                'vahaHodnotenia': '_VH_/texty/p',
                'garanti': 'garanti/garant/plneMeno',
                'jazyk': '_PJ_/texty/p',
                'obsahovaNapln': '_ON_/texty',
                'podmienkyAbsolvovania': '_PA_/texty',
                'vysledkyVzdelavania': '_VV_/texty',
                'poznamky': '_PZ_/texty',
                'hodnotenia': 'hodnoteniaPredmetu/hodnoteniePredmetu',
                'pocetHodnoteni': 'hodnoteniaPredmetu/celkovyPocetHodnotenychStudentov',
                'vyucujuci': 'vyucujuciAll/vyucujuci',
    }
    data = []

    # spracovanie informacnych listov jednotlivych predmetov
    for il in ilisty.findall('informacnyList'):
        # preskocime statne skusky, tie sa spracuvaju inym skriptom
        if mode=='regular' and (il.find('_ON_') is not None):
            continue
        if mode=='statnice' and (il.find('_ON_') is None):
            continue

        d = {'lang' : lang, 
             'organizacnaJednotka': organizacnaJednotka,
             'vysokaSkola': vysokaSkola,
             'fakulta': fakulta }
        for key, path in elements.iteritems():
            if il.find(path) is not None:
                if key != 'vahaHodnotenia' and path.startswith('_'):
                    d[key] = utils.get_text(il.find(path))
                elif key in ['studijneProgramy','hodnotenia','vyucujuci']:
                    d[key]=[]
                    for el in il.findall(path):
                        strct = {}
                        for subel in el:
                            strct[subel.tag]=subel.text
                        d[key].append(strct)
                elif key in ['studijnyProgram', 'jazyk', 'studijneProgramy']:
                    d[key] = [el.text for el in il.findall(path)]
                    if key == 'jazyk':
                        d[key] = list(set(d[key]))
                else:
                    d[key] = il.find(path).text
            else:
                d[key] = ''

        # uprava kodov predmetov
        d['kod'] = utils.parse_code(d['kod'])
        d['year'] = year

        # uprava URL
        if d['webstranka']:
            d['webstranka'] = utils.make_link(d['webstranka'],d['webstranka'])

        # URL pre vyucujucich
        for v in d['vyucujuci']:
            email = v.get('pridelenyEmail')
            if email!=None:
                login = re.search('^(.*)\@uniba\.sk$',email)
                if login!=None:
                    v['url']='https://sluzby.fmph.uniba.sk/ludia/'+login.group(1)
            
        data.append(d)

    return data


def render_HTML(data, tpl_name, output_path=None, courses=None, lang='sk', mode='regular', year='xxx'):
    """Render the course data into separate HTML files named by the course codes.

    Params:
        data: list of dicts
        output_path:
        courses: dict of all courses uses for creating cross-document links
    """
    # nacitanie HTML sablony
    script_abs_path = os.path.dirname(os.path.abspath(__file__))
    env = Environment(loader=FileSystemLoader(script_abs_path))
    html_tpl = env.get_template(tpl_name)

    # zapis do HTML suborov
    for course in data:
        kod_predmetu = course['kod']

        course['podmienujucePredmety'] = utils.replace_codes(course['podmienujucePredmety'], lang, add_links=True, courses=courses, and_symbol=trans[lang]['a'])
        course['vylucujucePredmety'] = utils.replace_codes(course['vylucujucePredmety'], lang, add_links=True, courses=courses)
        course['obsahovaPrerekvizita'] = utils.replace_codes(course['obsahovaPrerekvizita'], lang, add_links=True, courses=courses)

        html = html_tpl.render(course)

        filename = '%s.html' % kod_predmetu
        filename = filename.replace("/","_")
        if output_path is not None:
            path = os.path.join(output_path, filename)
            if not os.path.exists(output_path):
                os.mkdir(output_path)
        else:
            path = filename
        with open(path, 'w') as f:
            f.write(html.encode('utf8'))


def main(filenames, tpl_name, output_path=None, lang='sk', mode='regular', year='xxx', verbose=True):
    if verbose:
        print("Extrahujem nazvy predmetov...",)
    courses = {}
    # extrahuj vsetky predmety
    for f in filenames:
        courses = extract_courses(f, courses)
    if verbose:
        print("Hotovo.")

    for f in filenames:
        if verbose:
            print("Spracuvam subor '%s'..." % f)
        data = extract_infolists(f, lang=lang, mode=mode, year=year, verbose=verbose)
        render_HTML(data, tpl_name, output_path, courses, mode=mode, lang=lang, year=year)
    if verbose:
        print("Hotovo.")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Converts AIS XMLs into HTMLs.')
    parser.add_argument('input_path', metavar='input-path', help='path to input XMLs')
    parser.add_argument('output_path', metavar='output-path', help='path for HTML files to be stored')
    parser.add_argument('tpl_name', metavar='tpl-name', help='file with template')
    parser.add_argument('--lang', dest='lang', nargs='?', default='sk', help='language')
    parser.add_argument('--year', dest='year', nargs='?', default='2022-2023', help='academic year')
    parser.add_argument('--mode', dest='mode', nargs='?', default='regular', help='mode of work regular/statnice')

    args = parser.parse_args()

    xml_path = os.path.join(args.input_path, '*.xml')
    filenames = glob.glob(xml_path)
    main(filenames, args.tpl_name, args.output_path, lang=args.lang, mode=args.mode, year=args.year)

