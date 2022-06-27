#!/usr/bin/env python

import os, sys, glob, getopt, time, string, signal, stat, shutil
import gobject, pango, math, traceback, subprocess
import gzip, zlib, zipfile, re

navitem = \
  '''<navPoint class="chapter" playOrder="1" id="navPoint-1">
      <navLabel><text>Apple</text></navLabel>
      <content src="MEFTU/apple.html"></content> 
    </navPoint>'''
    

#  -----------------------------------------------------------------------
# Start of program:

if __name__ == '__main__':

    print "Generating ebook TOC"
    fp = open("flist.txt")
    
    while True:
        line = fp.readline()
        if line == "": break
        line = line.rstrip()
        print line
    
    fp.close()


