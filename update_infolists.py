#!/usr/bin/env python
from datetime import date
import requests
import os
import os.path
import re

def current_season():
  today = date.today()
  start_year = today.year
  if today.month <= 8:
    start_year -= 1
  return '{}-{}'.format(start_year, start_year + 1)
  
def download_tree(source, dest):
  resp = requests.get(source)
  pattern = r'href="({}/([^"/]+\.xml))"'.format(re.escape(source.replace('https://', 'http://')))
  for url in re.finditer(pattern, resp.text):
    with open(os.path.join(dest, url.group(2)), 'wb') as f:
      resp = requests.get(url.group(1), stream=True)
      for chunk in resp.iter_content(8192):
        f.write(chunk)

def download(source, season, faculty, lang, dest):
  real_source = '{}/{}/{}/{}'.format(source, season, faculty, lang.upper())
  real_dest = os.path.join(dest, faculty, 'xml_files_{}'.format(lang.lower()))
  if not os.path.isdir(real_dest):
    os.makedirs(real_dest)
  return download_tree(real_source, real_dest)

if __name__ == '__main__':
  import argparse
  
  parser = argparse.ArgumentParser()
  parser.add_argument('--faculty', default='FMFI')
  parser.add_argument('--download-only', action='store_true')
  parser.add_argument('--data-dir', default='.')
  parser.add_argument('--source', default='http://ais2.uniba.sk/repo2/repository/default/ais/informacnelisty')
  parser.add_argument('--season', default=current_season())
  parser.add_argument('--lang', default='sk')
  
  args = parser.parse_args()
  
  download(args.source, args.season, args.faculty, args.lang, args.data_dir)