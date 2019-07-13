import os
import csv
class RosterParser:

    def __init__ (self, ):
        pass

    def clean_file (self, source, destination):
        '''
        Reads a csv downloaded from Banners new student list and writes a new file to the destination that
        is just a single header line followed by students
        :param source:
        :param destination:
        :return:
        '''
        f = open(source, 'r')
        g = open(destination, 'w')
        omit_lines = True
        for line in f:
            if line.startswith('Student Name'):
                omit_lines = False
            if not omit_lines:
                g.write(line)
        f.close()
        g.close()









