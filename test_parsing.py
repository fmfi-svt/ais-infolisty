#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest

import AIS_XML2HTML

class ParsingTests(unittest.TestCase):

    def test_parsing(self):
        filename = 'test.xml'

        data = AIS_XML2HTML.extract_infolists(filename, lang='sk', verbose=False)

        self.assertEqual(data[0]['priebezneHodnotenie'], 'test')
        self.assertEqual(data[0]['zaverecneHodnotenie'], u'sk\xfa\u0161ka')
        self.assertEqual(data[0]['jazyk'], [u'slovensk\xfd'])
        self.assertEqual(data[0]['studijnyProgram'], [u'obnovite\u013en\xe9 zdroje energie a environment\xe1lna fyzika', u'biomedic\xednska fyzika'])

if __name__ == '__main__':
    unittest.main()

