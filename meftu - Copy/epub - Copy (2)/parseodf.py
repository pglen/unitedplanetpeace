#!/usr/bin/env python

import os, sys, glob, getopt, time, string, signal, stat, shutil
import gobject, pango, math, traceback, subprocess
import gzip, zlib, zipfile, re

# ------------------------------------------------------------------------
# Simple parser to extract <text ... > </text ...> fields from XML
# and procuce HTML suitable for ebook publishing. A subset of html is 
# produced, and paragraphes are wrapped in <span>
#

output = ""
data = None
sdic = {}
   
# Class to hold parser state

class pdata():
    def __init__(self):
        self.flag = False; self.state = 0; 
        self.style = ""; self.span = False
        self.styles = []
        self.curr = {}
        self.para = False
        self.closed = False

# ------------------------------------------------------------------------

def dictize(strx):

    ddd = {}
    sss = string.split(strx)
    #print "dictize", sss
    for aa in sss:
        aaa = string.split(aa, "=") 
        if len(aaa) > 1:
            ddd[aaa[0]] = str(aaa[1]) # .replace('"', "")
        else:
            ddd[aaa[0]] = ""
    #print "dic", ddd
    return ddd
    
# ------------------------------------------------------------------------
# Main entry point

def parse(fname):

    global data, sdic, output
    
    data = pdata()
    strx = ""; cmd = ""; strs = "" 
    fh3 = open(aa.filename, "r")
    while 1:
        ssss = fh3.read(1) 
        if ssss == "": break
        
        # Branch on state machine
        if data.state == 0:
            if ssss == "<":
                data.state = 1;            
            else:     
                if data.flag == 1:
                    strx += ssss
                    #print ssss,
            continue;           
            
        elif data.state == 1:            
            if ssss == ">":
                data.state = 0;                
                #print "cmd", "<" + cmd + ">"
                
                # Start tags ---------------------------------------------
                if cmd.startswith("style"):
                    if cmd.startswith("style:style"):
                        #print "   start style", "[" + cmd + "]"
                        data.styles.append(cmd + " ")
                    if cmd.startswith("style:font"):
                        #print "   font style", "[" + cmd + "]"
                        pass
                    else:
                        data.styles[len(data.styles)-1] += cmd + " "
                        #print "   cont style", "[" + cmd + "]"
                    pass
                    
                if cmd.startswith("text"):
                    # By the time the first text occurs, styles are done, parse it
                    if  len(sdic) == 0:
                        build_styles()
                    if cmd.startswith("text:sequence-decl"):
                        pass
                    else:
                        #print "start text", cmd
                        if cmd.startswith("text:span"):
                            pass
                        elif cmd.startswith("text:p"):
                            if not data.para:
                                #output += "<p>&nbsp;&nbsp;&nbsp;"
                                output += "<p>"
                                data.para = True
                        # Put previous data
                        ddd = dictize(cmd)
                        if "text:style-name" in ddd:
                            data.style = ddd["text:style-name"]
                        #print "start text", cmd
                        data.flag = 1
                        strx = puttext(strx, data)                    
                        
                # End tags -----------------------------------------------
                if cmd.startswith("/style"):
                    #print "   end style", "[" + cmd + "]"
                    pass
                    
                if cmd.startswith("/text"):
                    if cmd.startswith("/text:sequence-decl"):
                        pass
                    elif cmd.startswith("/text:span"):
                        strx = puttext(strx, data)
                        #print "end text span", cmd
                    elif cmd.startswith("/text:s "):
                        strx = puttext(strx, data)
                        #print "end string", cmd
                    elif cmd.startswith("/text:p"):
                        strx = puttext(strx, data)
                        if data.para:
                            output += "</p>\n"
                            data.para = False
                        #print "end paragraph", cmd
                    else:
                        strx = puttext(strx, data)                        
                        #print "end text", cmd
                        data.flag = 0                   
                    data.style = ""
                cmd = ""
            else:
                cmd += ssss     
            continue
        else:
            pass
            
    # Force para end
    data.closed = True
    strx = " "
    strx = puttext(strx, data)                        
     
# Create a dictionary of the current styles
       
def build_styles():
    global sdic, data
    for aa in data.styles:
        sss = string.split(aa)
        name = ""
        for bb in sss:
            cc = string.split(bb, "=")
            if  cc[0] == "style:name":
                name = cc[1]
                sdic[name] = {}
                break
        for bbb in sss:
            ccc = string.split(bbb, "=")
            if len(ccc) > 1:
                #print ccc[0], ccc[1]
                sdic[name] [ccc[0]] = ccc[1]
            else:
                sdic[name] [ccc[0]] = ""
    
# Just to verify ....

def print_styles():
    global sdic
    for ddd in sdic.keys():
        print ddd, sdic[ddd]
        print
          
# ------------------------------------------------------------------------
# Output text from parser. Replace some HTML escapes and the unicode
# quotes. We are relying on minimal (ASCII) target platforms for world
# wide coverage.

def puttext(txt, data):

    global output, sdic
    
    # The parser will call us on every turn
    if txt == "":
        #print "[blank]"
        return ""
        
    txt = txt.replace("&lt;", "<")
    txt = txt.replace("&gt;", ">")        
    txt = txt.replace("&apos;", "'")        
    txt = txt.replace("&amp;", "&") 
    # The " codes:
    txt = txt.replace("\xe2\x80\x9c", '"')
    txt = txt.replace("\xe2\x80\x9d", '"')
    
    sss = data.style
    bold = False; italic= False; header = False 
    if sss != "":
        print #"data.style", sss
        if sss in sdic:
            #print "sdic[sss]", sdic[sss]
            if 'fo:font-size' in sdic[sss]:
                #print "fo:size", sdic[sss]['fo:font-size']
                nnn = sdic[sss]['fo:font-size'].replace('"', "")
                if int(nnn.replace("pt", "")) >= 18:
                    header = True
            if 'fo:font-weight' in sdic[sss]:
                #print "fo:weigth", "'" + sdic[sss]['fo:font-weight'] + "'"
                if sdic[sss]['fo:font-weight'].find("bold") >= 0:
                    bold = True
            if 'fo:font-style' in sdic[sss]:
                #print "fo:style", sdic[sss]['fo:font-style']
                if sdic[sss]['fo:font-style'].find("italic") >= 0:
                    italic = True
    #print "[" + txt + "]",
    pre = ""; post = ""
    if bold:
        pre = "<b>"; post = "</b>"
    if italic:
        pre = "<i>"; post = "</i>"
        
    # Output header / para      
    if header:
        pre = "<center><h2>"; post = "</h2></center>\n"
                   
    output += pre + txt + post
    
    data.style = ""   
    return ""

#  -----------------------------------------------------------------------
# Start of program:

if __name__ == '__main__':

    #global output 

    #args = conf.comline(sys.argv[1:])

    if len(sys.argv) < 2:
        print "Usage: parseodf.py [options] ebookfile"
        sys.exit(1)
        
    #fname = sys.argv[1]    
    for fname in sys.argv[1:]:
        if not os.path.isfile(fname):
            print "File:", "'" + fname + "'", "does not exist."
            continue
            #sys.exit(2)
        # Open archive
        try:
            zf = zipfile.ZipFile(fname)
        except:
            zf = None
            print "Cannot open odt file", "'" + fname + "'"
            sys.exit(3)
        print 
        for aa in zf.infolist():
            #print aa.filename, aa.file_size
            if aa.filename == "content.xml":
                #print "extracting ...", aa.filename
                fh  = zf.open(aa.filename)
                fh2 = open(aa.filename, "w+")
                while 1:
                    sss = fh.readline() 
                    if sss == "": break
                    fh2.write(sss)
                fh2.close()
                parse(aa.filename)           
                break     
        print; print
        print output
        print; print 
        
    os.remove("content.xml")
