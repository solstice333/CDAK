#!/usr/bin/env python
import csv
import argparse

class CDAK:
   def __init__(self, cdak_file):
      self.name = cdak_file
      self.file = open(self.name, 'r')

   def __enter__(self):
      return self.file

   def __iter__(self):
      return self.file

   def __next__(self):
      # put everything in here
      yield self.file.readline()

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
