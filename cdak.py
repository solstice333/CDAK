#!/usr/bin/env python
import csv
import argparse
import re
import sys

class ConfigParser:
   def __init__(self, config_file):
      self.config_file = config_file

   def get_groups(self):
      groups = {}
      filename = ''

      with open(self.config_file, 'r') as configs:
         for line in configs:
            line = re.sub(r'#.*$', '', line)

            if re.match(r'\s*#|\s*\n', line):
               continue
            else:
               if re.match(r'\s*None\s*', line, re.I):
                  node = None
               else:
                  m = re.match(r'(\"|\')(.*)\1\s*$', line)
                  if m:
                     filename = m.group(2)
                     groups[filename] = []
                     continue

                  pair = re.split(r'\s*,\s*', line)
                  if len(pair) != 2:
                     raise ValueError(
                        "Error: Bad value '{}' in config file".format(
                           line.rstrip()))
                  node = (int(pair[0]), int(pair[1].rstrip()))

               groups[filename].append(node)
      return groups

class CDAK:
   @staticmethod
   def _is_all_values_are_empty(line):
      return ''.join([s for s in line.values()]) == ''

   @staticmethod
   def _is_eof(line):
      return line['Time(hh:mm:ss)'] == '~End'

   @staticmethod
   def _get_blank(blk):
      blanks = [float(blk[0]['10']), float(blk[0]['11']), float(blk[0]['12'])]
      return float(sum(blanks)/len(blanks))

   @staticmethod
   def _convert_blk_to_mdim(blk):
      mdim = []
      for row in blk:
         mdim.append([row[str(col)] for col in range(1, 13)])
      return mdim

   class Fibro:
      WIDTH = 3
      def __init__(self, config, blk, blank):
         self.cfig = config
         self.b = blk
         self.box = self.init_box()
         self.blank = blank

      def init_box(self):
         box = [[],[],[]]
         i = 0
         for pair in self.cfig:
            value = None if pair is None else self.b[int(pair[0])][int(pair[1])]
            box[i].append(value)
            i = i + 1 if i < 2 else 0
         return box 

      def get_diff(self):
         vals = []
         for col in range(CDAK.Fibro.WIDTH): 
            for row in range(CDAK.Fibro.WIDTH):
               vals.append(str(float(self.box[row][col]) - self.blank) \
                  if self.box[row][col] else None)
         return vals

      def __str__(self):
         return ','.join(map(lambda d: d or '', self.get_diff()))

   def __init__(self, cdak_file, group):
      self.name = cdak_file
      self.file = open(self.name, 'r')
      self.csvreader = csv.DictReader(self.file)
      self.cursor = None
      self.blk = []
      self.group = group

   def __enter__(self):
      return self

   def __iter__(self):
      self.cursor = iter(self.csvreader)
      return self

   def __next__(self):
      self.blk = []

      for line in self.cursor:
         if CDAK._is_all_values_are_empty(line):
            mdim = CDAK._convert_blk_to_mdim(self.blk)
            avg = CDAK._get_blank(self.blk)
            return CDAK.Fibro(self.group, mdim, avg)
         elif CDAK._is_eof(line):
            break
         self.blk.append(line)
      raise StopIteration

   def __exit__(self, exc_type, exc_value, traceback):
      self.file.close()

def generate_config_file(filename):
   template = \
"""# comments ignored, newlines ignored

'stdout' # print to stdout
0, 0 # trailing comments allowed
1, 0
2, 0
0, 3
1, 3
2, 3
0, 6
1, 6
2, 6

'stdout2' # print to stdout without overriding the previous stdout
# required syntax below:
1,9   # A, 0.5 ug
2,9   # B, 0.5 ug
3,9   # C, 0.5 ug

4,9   # A, 1 ug
5,9   # B, 1 ug
6,9   # C, 1 ug

6,0   # A, 2 ug
6,1   # B, 2 ug
6,2   # C, 2 ug

'pep.csv' # write to a file called pep.csv
None # None is an empty well and is ignored
None
None
None
None
None
7,0
7,1
7,2
"""

   with open(filename, 'w') as example:
      example.write(template)

class FH:
   def __init__(self, filename):
      self._filename = filename

      if re.match(r'\s*stdout\d*$', self._filename, re.I):
         self._fh = sys.stdout
         self._closable = False
      else:
         self._fh = open(self._filename, 'w')
         self._closable = True

   def __enter__(self):
      return self

   @property
   def name(self):
      return self._filename

   @property
   def handle(self):
      return self._fh

   @property
   def is_file(self):
      return self._closable

   def __exit__(self, exc_type, exc_value, traceback):
      if self._closable:
         self._fh.close()

def main():
   parser = argparse.ArgumentParser(
      description="Cathepsin D Assay Kinetics data converter. " +
         "BLANK must be in the three upper right corner wells for each " +
         "time block. The following header is required at the top of " +
         "the input csv  -- " +
         "\"Time(hh:mm:ss),Temperature(C),1,2,3,4,5,6,7,8,9,10,11,12\". " +
         "config.ini must be in the format specified in the generated " +
         "sample using -g.")
   parser.add_argument('-c', '--config-file', 
      help='specify a config file to use. Defaults to ./config.ini')
   parser.add_argument('CSV', nargs='?', 
      help='path to input csv file to parse')
   parser.add_argument('-g', '--generate-config-file',
      nargs='?', const='config.ini', metavar='CONFIG_FILE',
      help='generate a sample config file. ' + 
         'Defaults to config.ini if argument value is not given')
   args = parser.parse_args()

   if args.generate_config_file:
      generate_config_file(args.generate_config_file)
      exit(0)

   if not args.config_file:
      args.config_file = 'config.ini'

   configs = ConfigParser(args.config_file).get_groups()

   for filename, group in configs.items():
      with FH(filename) as fh:
         if not fh.is_file:
            print("\n{}:".format(fh.name))

         with CDAK(args.CSV, group) as cdak:
            for line in cdak:
               fh.handle.write("{}\n".format(line))


if __name__ == '__main__':
   main()
