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
               vals.append(str(float(self.box[row][col]) - self.blank))
         return vals

      def __str__(self):
         return ','.join(self.get_diff())

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

def main():
   parser = argparse.ArgumentParser(
      description="Cathepsin D Assay Kinetics data converter")
   parser.add_argument('-c', '--config-file', 
      help='path to config file. Defaults to ./config.ini')
   parser.add_argument('CSV', help='path to input csv file to parse')
   args = parser.parse_args()

   if not args.config_file:
      args.config_file = 'config.ini'

   configs = ConfigParser(args.config_file).get_groups()

   for filename, group in configs.items():
      if re.match(r'\s*stdout\d*$', filename, re.I):
         fh = sys.stdout
         closable = False
      else:
         fh = open(filename, 'w')
         closable = True

      with CDAK(args.CSV, group) as cdak:
         for line in cdak:
            fh.write("{}\n".format(line))

      if closable:
         fh.close()

if __name__ == '__main__':
   main()






