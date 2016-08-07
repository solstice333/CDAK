#!/usr/bin/env python
import csv
import argparse

class CDAK:
   @staticmethod
   def _is_all_values_are_empty(line):
      return ''.join([s for s in line.values()]) == ''

   @staticmethod
   def _get_blank(blk):
      blanks = [float(blk[0]['10']), float(blk[0]['11']), float(blk[0]['12'])]
      return float(sum(blanks)/len(blanks))

   def __init__(self, cdak_file):
      self.name = cdak_file
      self.file = open(self.name, 'r')
      self.csvreader = csv.DictReader(self.file)
      self.cursor = None
      self.blk = []

   def __enter__(self):
      return self

   def __iter__(self):
      self.cursor = iter(self.csvreader)
      return self

   def __next__(self):
      self.blk = []

      for line in self.cursor:
         if CDAK._is_all_values_are_empty(line):
            return CDAK._get_blank(self.blk)
         self.blk.append(line)
      raise StopIteration

   def __exit__(self, exc_type, exc_value, traceback):
      self.file.close()

def main():
   parser = argparse.ArgumentParser(description="Cathepsin D Assay Kinetics data converter")
   parser.add_argument('CSV', help='path to csv file to parse')

   with CDAK(parser.parse_args().CSV) as cdak:
      for line in cdak:
         print(line)

if __name__ == '__main__':
   main()
