#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest

import utils

class UtilsTests(unittest.TestCase):

    maxDiff = None

    def test_parse_code(self):
        data = {
            'FMFI.KJP/1-MXX-151/00': '1-MXX-151_00',
            u'FMFI.KAMŠ/2-PMS-119/10': u'2-PMS-119_10',
            'FMFI.KI/1-INF-160/00': '1-INF-160_00'
        }
        for string, code in data.iteritems():
            self.assertEqual(utils.parse_code(string), code)

    def test_replace_codes(self):
        data = {
            'FMFI.KJP/1-MXX-151/00': '1-MXX-151_00',
            u'(FMFI.KMANM/1-MAT-150/00 alebo FMFI.KMANM/1-MMN-150/00 alebo FMFI.KAMŠ/1-EFM-130/00) , (FMFI.KAGDM/1-MAT-120/00 alebo FMFI.KAGDM/1-MMN-120/00)': u'(1-MAT-150_00 alebo 1-MMN-150_00 alebo 1-EFM-130_00) a (1-MAT-120_00 alebo 1-MMN-120_00)',
            None: '',
            '1-INF-210 Úvod do matematickej logiky a 1-AIN-411 Úvod do výpočtovej logiky': '1-INF-210 Úvod do matematickej logiky a 1-AIN-411 Úvod do výpočtovej logiky'
        }
        data_links = {
            u'(FMFI.KMANM/1-MAT-150/00 alebo FMFI.KMANM/1-MMN-150/00 alebo FMFI.KAMŠ/1-EFM-130/00) , (FMFI.KAGDM/1-MAT-120/00 alebo FMFI.KAGDM/1-MMN-120/00)': u'(<a href="https://sluzby.fmph.uniba.sk/infolist/SK/1-MAT-150_00.html">1-MAT-150_00</a> alebo <a href="https://sluzby.fmph.uniba.sk/infolist/SK/1-MMN-150_00.html">1-MMN-150_00</a> alebo <a href="https://sluzby.fmph.uniba.sk/infolist/SK/1-EFM-130_00.html">1-EFM-130_00</a>) a (<a href="https://sluzby.fmph.uniba.sk/infolist/SK/1-MAT-120_00.html">1-MAT-120_00</a> alebo <a href="https://sluzby.fmph.uniba.sk/infolist/SK/1-MMN-120_00.html">1-MMN-120_00</a>)'
        }
        data_links_courses = {
            u'(FMFI.KMANM/1-MAT-150/00 alebo FMFI.KMANM/1-MMN-150/00 alebo FMFI.KAMŠ/1-EFM-130/00) , (FMFI.KAGDM/1-MAT-120/00 alebo FMFI.KAGDM/1-MMN-120/00)': u'(<a href="https://sluzby.fmph.uniba.sk/infolist/SK/1-MAT-150_00.html">1-MAT-150_00 Matematická analýza (2)</a> alebo <a href="https://sluzby.fmph.uniba.sk/infolist/SK/1-MMN-150_00.html">1-MMN-150_00 Matematická analýza (2)</a> alebo <a href="https://sluzby.fmph.uniba.sk/infolist/SK/1-EFM-130_00.html">1-EFM-130_00 Matematická analýza (2)</a>) a (<a href="https://sluzby.fmph.uniba.sk/infolist/SK/1-MAT-120_00.html">1-MAT-120_00 Lineárna algebra a geometria (1)</a> alebo <a href="https://sluzby.fmph.uniba.sk/infolist/SK/1-MMN-120_00.html">1-MMN-120_00 Lineárna algebra a geometria (1)</a>)'
        }
        courses = {
            '1-MMN-150_00': u'Matematická analýza (2)',
            '1-MAT-150_00': u'Matematická analýza (2)',
            '1-EFM-130_00': u'Matematická analýza (2)',
            '1-MAT-120_00': u'Lineárna algebra a geometria (1)',
            '1-MMN-120_00': u'Lineárna algebra a geometria (1)'
        }

        for in_data, out_data in data.iteritems():
            self.assertEqual(utils.replace_codes(in_data, and_symbol='a'), out_data)

        for in_data, out_data in data_links.iteritems():
            self.assertEqual(utils.replace_codes(in_data, add_links=True, and_symbol='a'), out_data)

        for in_data, out_data in data_links_courses.iteritems():
            self.assertEqual(utils.replace_codes(in_data, courses=courses, add_links=True, and_symbol='a'), out_data)

    def test_get_url(self):
        data = {
            '1-MMN-150': 'https://sluzby.fmph.uniba.sk/infolist/SK/1-MMN-150.html',
            '1-MAT-150': 'https://sluzby.fmph.uniba.sk/infolist/SK/1-MAT-150.html'
        }

        for in_data, out_data in data.iteritems():
            self.assertEqual(utils.get_url(in_data, lang='sk'), out_data)

        self.assertFalse(utils.get_url('asdf', lang='es'))
        self.assertFalse(utils.get_url(''))

    def test_make_link_from_code(self):
        self.assertEqual(utils.make_link_from_code('test1', 'test2', lang='sk'), '<a href="https://sluzby.fmph.uniba.sk/infolist/SK/test1.html">test2</a>')
        self.assertEqual(utils.make_link_from_code('test1', 'test2', lang='en'), '<a href="https://sluzby.fmph.uniba.sk/infolist/EN/test1.html">test2</a>')

    def test_make_link(self):
        self.assertEqual(utils.make_link('test1', 'test2', title=''), '<a href="test1">test2</a>')
        self.assertEqual(utils.make_link('test1', 'test2', title='test3'), '<a href="test1" title="test3">test2</a>')

if __name__ == '__main__':
    unittest.main()
