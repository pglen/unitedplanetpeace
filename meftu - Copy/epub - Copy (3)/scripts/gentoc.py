#!/usr/bin/env python

import os, sys, glob, getopt, time, string, signal, stat, shutil
import gobject, pango, math, traceback, subprocess
import gzip, zlib, zipfile, re

# Create EBOOK spine files from master list in file flist.txt
# the file is a text file listing html files to process and 
# the title of the page. The two fields are separated by '--'

tochead = '''<?xml version='1.0' encoding='UTF-8'?>
<!DOCTYPE ncx PUBLIC '-//NISO//DTD ncx 2005-1//EN' 'http://www.daisy.org/z3986/2005/ncx-2005-1.dtd'>
<ncx xml:lang="en-US" version="2005-1" xmlns="http://www.daisy.org/z3986/2005/ncx/">
  <head>
     <meta name="dtb:uid" content="9781406951936"></meta>
     <meta name="dtb:depth" content="0"></meta>
     <meta name="dtb:totalPageCount" content="0"></meta>
     <meta name="dtb:maxPageNumber" content="0"></meta>
  </head>
  <docTitle><text>Messages from the Universe</text></docTitle>
  <docAuthor><text>Peter Glen</text></docAuthor>
'''  

tocfoot = '''</ncx>
'''

navitem = '''<navPoint class="chapter" playOrder="1" id="navPoint-1">
      <navLabel><text>Apple</text></navLabel>
      <content src="MEFTU/apple.html"></content> 
    </navPoint>'''
    
content = '''<?xml version='1.0' encoding='UTF-8'?>
<package version="2.0" unique-identifier="isbn" xmlns="http://www.idpf.org/2007/opf">
  <metadata xmlns:opf="http://www.idpf.org/2007/opf" xmlns:dc="http://purl.org/dc/elements/1.1/">
      <dc:title>MEFTU/</dc:title>
      <dc:creator opf:role="aut">Peter Glen</dc:creator>
      <dc:language>en</dc:language>
      <dc:rights>Public Domain</dc:rights>
      <dc:description>Messages From the Universe</dc:description>
  </metadata>
'''
content2 = '''    

  <guide>
    <reference type="cover" title="MEFTU/" href="MEFTU/__Title.html"></reference>
  </guide>
</package>

'''

#  -----------------------------------------------------------------------
# Start of program:

if __name__ == '__main__':

    #print "Generating ebook TOC"
    
    # Read in file data
    flist = []; tlist = []
    fp = open("flist.txt")
    while True:
        line = fp.readline()
        if line == "": break
        line = line.rstrip()
        if line == "": break
        aa = line.split("--")
        aa[0] = aa[0].lstrip().rstrip()
        if len(aa) < 2:
            aa.append(aa[0])
        aa[1] = aa[1].lstrip()
        
        try:
            if not aa[0].startswith("_"):    
                aa[1] = aa[0].split(".")[0] + " - " + aa[1]
        except: pass
        flist.append(aa[0]); tlist.append(aa[1])
    fp.close()
     
    #print "\nflist:", flist; print "\ntlist:", tlist
    #sys.exit(0)
    
    # Do content
    contfp = open("../content.opf", "w")
    contfp.write(content)
    mani = "\n<manifest>\n" \
    '\t<item id="ncx" href="toc.ncx" media-type="application/x-dtbncx+xml"></item>\n'
    
    for aa in range(len(flist)):
        mline = \
        '\t<item id="%s" href="MEFTU/%s" media-type="application/x-dtbncx+xml"></item>\n' \
         % (tlist[aa], flist[aa])
        mani += mline
    mani += "</manifest>\n"
    contfp.write(mani);
  
    # --------------------------------------------------------------------
    # Create toc
       
    tocstr = '''\n<spine toc="ncx">\n'''
    for aa in range(len(flist)):
        tocstr += '\t<itemref linear="yes" idref="%s"></itemref>\n' % tlist[aa]
    tocstr += "\n</spine>\n"
    contfp.write(tocstr);
    contfp.write(content2)

    contfp.close()

    # --------------------------------------------------------------------
    # Do toc.ncx
    
    tocfmt = '''\t<navPoint class="chapter" playOrder="%d" id="navPoint-1">
    \t<navLabel><text>%s</text></navLabel>
      \t\t<content src="MEFTU/%s"></content> 
    \t</navPoint>\n'''

    tocfp = open("../toc.ncx", "w")
    tocfp.write(tochead)
    item = 0
    toc = "\n<navmap>\n" 
    
    for aa in range(len(flist)):
        mline = tocfmt % (item, tlist[aa], flist[aa])
        toc += mline
        item += 1
        
    toc += "</manifest>\n"
    tocfp.write(toc);
    tocfp.write(tocfoot);
    tocfp.close()
    
    
    



