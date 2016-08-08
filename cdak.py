#!/usr/bin/env python
import csv
import argparse
import re

class ConfigParser:
   def __init__(self, config_file):
      self.config_file = config_file

   def get_groups(self):
      groups = [[]]
      group = 0

      with open(self.config_file, 'r') as configs:
         for line in configs:
            if re.match(r'\s*\n', line):
               group += 1
               groups.append([])
            elif re.match(r'\s*#', line):
               continue
            else:
               if re.match(r'\s*None\s*', line, re.I):
                  node = None
               else:
                  pair = re.split(r'\s*,\s*', line)
                  if len(pair) != 2:
                     raise ValueError(
                        "Error: Bad value '{}' in config file".format(line.rstrip()))
                  node = (int(pair[0]), int(pair[1].rstrip()))
               groups[group].append(node)

      return [l for l in groups if len(l) != 0]

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
      def __init__(self, config, blk):
         self.cfig = config
         self.b = blk
         self.box = self.init_box()

      def init_box(self):
         box = [[],[],[]]
         i = 0
         for pair in self.cfig:
            value = None if pair is None else self.b[int(pair[0])][int(pair[1])]
            box[i].append(value)
            i = i + 1 if i < 2 else 0
         return box 

      def __str__(self):
         return str(self.box)

   def __init__(self, cdak_file, config_file):
      self.name = cdak_file
      self.file = open(self.name, 'r')
      self.csvreader = csv.DictReader(self.file)
      self.cursor = None
      self.blk = []
      self.configs = ConfigParser(config_file).get_groups()

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
            fibro = CDAK.Fibro(self.configs[0], mdim)
            return CDAK._get_blank(self.blk)
         elif CDAK._is_eof(line):
            break
         self.blk.append(line)
      raise StopIteration

   def __exit__(self, exc_type, exc_value, traceback):
      self.file.close()

def main():
   parser = argparse.ArgumentParser(description="Cathepsin D Assay Kinetics data converter")
   parser.add_argument('-f', '--config-file', required=True, help='path to config file')
   parser.add_argument('CSV', help='path to csv file to parse')
   args = parser.parse_args()

   with CDAK(args.CSV, args.config_file) as cdak:
      for line in cdak:
         print(line)


if __name__ == '__main__':
   main()
