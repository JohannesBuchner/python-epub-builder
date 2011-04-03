# -*- coding: utf-8 -*-
import getopt
import os
import sys
import StringIO
from xml.sax.saxutils import escape
from pdfminer.converter import PDFPageAggregator
from pdfminer.layout import LTContainer, LTText, LTImage
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfparser import PDFParser, PDFDocument
from pdfminer.pdftypes import LITERALS_DCT_DECODE
import pdf_customizers


class PDFFile:
    
    def __init__(self, controller, fileName):
        self.controller = controller
        self.fileName = fileName
        self.doc = None
        self.toc = None
        self.pageObjMap = None
        self.pageCount = 0
        self.pageOffset = 0
        
    def getDoc(self):
        if not self.doc:
            fin = open(self.fileName, 'rb')
            parser = PDFParser(fin)
            self.doc = PDFDocument()
            parser.set_document(self.doc)
            self.doc.set_parser(parser)
            password = ''
            self.doc.initialize(password)
            if not self.doc.is_extractable:
                raise Exception("Unable to extract PDF")
        return self.doc
    
    def getPageId(self, objid):
        if not self.pageObjMap:
            self.pageObjMap = {}
            pageId = 0
            for page in self.getDoc().get_pages():
                pageId += 1
                self.pageObjMap[page.pageid] = pageId
        return self.pageObjMap.get(objid, 0);
    
    def getPageCount(self):
        if self.pageCount == 0:
            for _ in self.getDoc().get_pages():
                self.pageCount += 1
        return self.pageCount
    
    def getToc(self):
        if not self.toc:
            self.controller.extractToc(self)
        return self.toc


class Controller:
    
    def __init__(self, pdfFileNames):
        self.pdfFiles = []
        pageOffset = 0
        for fileName in pdfFileNames:
            pdfFile = PDFFile(self, fileName)
            pdfFile.pageOffset = pageOffset
            pageOffset += pdfFile.getPageCount()
            self.pdfFiles.append(pdfFile)
            
    def extractToc(self, pdfFile):
        pdfFile.toc = []
        for (level, title, dest, a, se) in pdfFile.getDoc().get_outlines():
            print level, title, dest, a, se
            pdfFile.toc.append((level, title, 1))

    def getDevice(self, resourceManager):
        return PDFPageAggregator(resourceManager)
    
    def output(self, handler, pageLimit = 0):
        handler.beginCollection(self.pdfFiles)
        for pdfFile in self.pdfFiles:
            resourceManager = PDFResourceManager()
            device = self.getDevice(resourceManager)
            interpreter = PDFPageInterpreter(resourceManager, device)
            handler.beginFile(pdfFile)
            for i, page in enumerate(pdfFile.getDoc().get_pages()):
                if pageLimit > 0 and i >= pageLimit:
                    break
                interpreter.process_page(page)
                ltPage = device.get_result()
                handler.doPage(ltPage)
            handler.endFile()
        handler.endCollection()


class PDFHandler:
    
    def __init__(self):
        pass
    
    def beginCollection(self, pdfFiles):
        self.pdfFiles = pdfFiles
        self.pageId = 0
        self.imageId = 0
        self.totalPageCount = 0
        for pdfFile in pdfFiles:
            self.totalPageCount += pdfFile.getPageCount()
    
    def endCollection(self):
        pass
    
    def beginFile(self, pdfFile):
        self.pdfFile = pdfFile
    
    def endFile(self):
        pass
    
    def doPage(self, ltPage):
        self.pageId += 1
        print self.pageId

        
class TextOutputHandler(PDFHandler):
    
    def __init__(self, outputFileName, lineLength = 50):
        PDFHandler.__init__(self)
        self.outputFileName = outputFileName
        self.lineLength = lineLength
        
    def beginCollection(self, pdfFiles):
        PDFHandler.beginCollection(self, pdfFiles)
        self.sout = StringIO.StringIO()
    
    def endCollection(self):
        PDFHandler.endCollection(self)
        fout = open(self.outputFileName, 'w')
        for pdfFile in self.pdfFiles:
            for level, title, pageId in pdfFile.getToc():
                fout.write('%s%s PAGE %d\n' % (' ' * (2 * level - 2), title.encode('utf-8'), pdfFile.pageOffset + pageId))
        fout.write(self.sout.getvalue())
        fout.close()
        
    def doPage(self, ltPage):
        PDFHandler.doPage(self, ltPage)
        self.sout.write('\nPAGE %d\n' % self.pageId)
        self.textPos = 0
        self.outputItem(ltPage)

    def outputItem(self, ltItem):
        if isinstance(ltItem, LTContainer):
            self.outputContainer(ltItem)
        elif isinstance(ltItem, LTText):
            self.outputText(ltItem)
        elif isinstance(ltItem, LTImage):
            self.outputImage(ltItem)
    
    def outputContainer(self, ltContainer):
        self.sout.write('\n')
        for child in ltContainer:
            self.outputItem(child)
        self.sout.write('\n')
    
    def outputText(self, ltText):
        text = ltText.get_text()
        self.incTextPos(len(text))
        self.sout.write(text.encode('utf-8'))
        
    def outputImage(self, ltImage):
        self.imageId += 1
        self.sout.write('IMAGE %s\n' % self.imageId)

    def incTextPos(self, k):
        self.textPos += k
        if self.textPos > self.lineLength:
            self.sout.write('\n')
            self.textPos = k    


class HTMLOutputHandler(PDFHandler):
    
    class FontRegistry:
        
        def __init__(self):
            self.fontMap = {}
            self.cssClassMap = {}
            self.chCount = {}
            self.chWidthSum = {}
            
        def getCSSClass(self, fontName, fontSize):
            fontSize = int(round(fontSize))
            fontId = self.fontMap.setdefault(fontName, len(self.fontMap) + 1)
            cssClass = 'f%d_%d' % (fontId, fontSize) 
            self.cssClassMap.setdefault((fontName, fontSize), cssClass)
            return cssClass
            
        def countChar(self, cssClass, chWidth):
            self.chCount[cssClass] = self.chCount.get(cssClass, 0) + 1
            self.chWidthSum[cssClass] = self.chWidthSum.get(cssClass, 0) + chWidth
        
        def getFonts(self):
            l = []
            for (fontName, fontSize), cssClass in self.cssClassMap.iteritems():
                chCount = self.chCount.get(cssClass, 0)
                chWidthSum = self.chWidthSum.get(cssClass, 0)
                l.append((cssClass, fontName, self.fontMap[fontName], fontSize, chCount, chWidthSum))
            l.sort(cmp = lambda x, y: cmp(x[3], y[3]) if x[2] == y[2] else cmp(x[2], y[2]))
            return l
    
    def __init__(self, outputDirName, scale = 1.0):
        PDFHandler.__init__(self)
        self.outputDirName = outputDirName
        try:
            os.makedirs(os.path.join(self.outputDirName, 'images'))
        except OSError:
            pass
        self.scale = scale
        
    def beginCollection(self, pdfFiles):
        PDFHandler.beginCollection(self, pdfFiles)
        self.fontRegistry = HTMLOutputHandler.FontRegistry()
        
    def endCollection(self):
        PDFHandler.endCollection(self)
        fout = open(os.path.join(self.outputDirName, 'toc.htm'), 'w')
        fout.write("""<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN" "http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
<meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
<title>Table of Contents</title>
<link rel="stylesheet" type="text/css" href="main.css" />
</head>
<body>
<div id="toc">
""")
        for pdfFile in self.pdfFiles:
            for level, title, pageId in pdfFile.getToc():
                fout.write('<div style="text-indent:%dem;"><a href="%d.htm">%s</a></div>\n' %
                           (level * 2 - 2, pdfFile.pageOffset + pageId, title.encode('utf-8')))
        fout.write("""</div>
</body>
</html>
""")
        fout.close()
        
        fout = open(os.path.join(self.outputDirName, 'main.css'), 'w')
        fout.write("""#toc a { text-decoration:none; }
.nav a { text-decoration:none; }
""")
        for cssClass, fontName, fontId, fontSize, chCount, chWidthSum in self.fontRegistry.getFonts():
            avgWidth = int(round(chWidthSum / chCount)) if chCount > 0 else 0
            fout.write('.%s { font-size:%dpx; } /* %d %s */\n' % (cssClass, fontSize * self.scale, avgWidth, fontName))
        fout.close()
    
    def doPage(self, ltPage):
        PDFHandler.doPage(self, ltPage)
        self.sout = StringIO.StringIO()
        self.maxy = ltPage.y1

        self.outputItem(ltPage)
        left, top, right, bottom, width, height = self.getDimensions(ltPage)
        if self.pageId > 1:
            self.sout.write('<div class="nav" style="position:absolute; left:0; top:0"><a href="%d.htm">&lt;</a></div>\n' % (self.pageId - 1))
        if self.pageId < self.totalPageCount: 
            self.sout.write('<div class="nav" style="position:absolute; right:0; top:0"><a href="%d.htm">&gt;</a></div>\n' % (self.pageId + 1))
            self.sout.write('<div class="nav" style="position:absolute; right:0; bottom:0"><a href="%d.htm">&gt;</a></div>\n' % (self.pageId + 1))
        self.sout.write('<div class="nav" style="position:absolute; left:0; bottom:0"><a href="toc.htm">=</a></div>\n')       
        fout = open(os.path.join(self.outputDirName, '%d.htm' % self.pageId), 'w')
        fout.write("""<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN" "http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
<meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
<title>Page %d</title>
<link rel="stylesheet" type="text/css" href="main.css" />
</head>
<body>
<div style="position:relative; width:%dpx; height:%dpx">
%s</div>
</body>
</html>
"""  % (self.pageId, width, height, self.sout.getvalue()))
        fout.close()
        
    def getDimensions(self, ltItem):
        left = ltItem.x0 * self.scale
        top = (self.maxy - ltItem.y1) * self.scale
        right = ltItem.x1 * self.scale
        bottom = (self.maxy - ltItem.y0) * self.scale
        width = ltItem.width * self.scale
        height = ltItem.height * self.scale
        return (left, top, right, bottom, width, height)
        
    def outputRect(self, ltItem, color, label):
        left, top, right, bottom, width, height = self.getDimensions(ltItem)
        self.sout.write('<!-- %s %d %d %d %d --><div style="position:absolute; border:%s 1px solid; left:%dpx; top:%dpx; width:%dpx; height:%dpx;"></div>\n' %
                         (label, left, top, right, bottom, color, left, top, width, height))
    
    def outputItem(self, ltItem):
        if isinstance(ltItem, LTContainer):
            self.outputRect(ltItem, 'Lavender', type(ltItem).__name__)
            for child in ltItem:
                self.outputItem(child)
        elif isinstance(ltItem, LTText):
            self.outputText(ltItem)
        elif isinstance(ltItem, LTImage):
            self.outputImage(ltItem)
        else:
            self.outputRect(ltItem, 'Lavender', type(ltItem).__name__)
    
    def outputText(self, ltText):
        left, top, right, bottom, width, height = self.getDimensions(ltText)
        cssClass = self.fontRegistry.getCSSClass(ltText.fontname, ltText.size * 0.8)
        self.fontRegistry.countChar(cssClass, width)
        text = ltText.text.encode('utf-8')
        text = escape(text)
        if text.startswith('\\x'): # flag for garbled text
            text = '□<!-- %s -->' % text
        self.sout.write('<!-- %d %d %d %d --><span class="%s" style="position:absolute; left:%dpx; top:%dpx;">%s</span>\n' %
                        (left, top, right, bottom, cssClass, left, top, text))

    def outputImage(self, ltImage):
        self.imageId += 1
        stream = ltImage.stream
        filters = stream.get_filters()
        data = None
        if len(filters) == 1 and filters[0] in LITERALS_DCT_DECODE:
            ext = '.jpg'
            data = stream.get_rawdata()
        else:
            ext = '.img'
            print 'OOPS: NON JPEG'
        fileName = '%d%s' % (self.imageId, ext)
        if data:
            path = os.path.join(self.outputDirName, 'images', fileName)
            fout = file(path, 'wb')
            fout.write(data)
            fout.close()

        left, top, right, bottom, width, height = self.getDimensions(ltImage)
        self.sout.write('<!-- %d %d %d %d --><img style="position:absolute; left:%dpx; top:%dpx;" width="%d" height="%d" src="images/%s" alt="%s"/>\n' %
                        (left, top, right, bottom, left, top, width, height, fileName, fileName))            

        
def main(inputFileNames, outputName, mode, format, txtLineLength, htmlScale, pageLimit):
    if format == 'txt':
        handler = TextOutputHandler(outputName + '.txt', txtLineLength)
    elif format == 'html':
        handler = HTMLOutputHandler(outputName, htmlScale)
    else:
        raise Exception('Invalid format: %s' % format)
    if mode == 'jtcsjj':
        controller = pdf_customizers.JTCSJJ_Controller(inputFileNames)
    elif mode == 'zjyx':
        controller = pdf_customizers.ZJYX_Controller(inputFileNames)
    else:
        controller = Controller(inputFileNames)
    controller.output(handler, pageLimit)
    
def main0():
    def usage():
        print 'Usage: python pdf_converter.py [--format=html|txt] [--mode=...] [--line=50] [--scale=1.25] [--pagelimit=0] input1 input2 ... output'
    try:
        opts, args = getopt.getopt(sys.argv[1:], 'h', ['help', 'format=', 'mode=', 'line=', 'scale=', 'pagelimit='])
    except getopt.GetoptError, err:
        print str(err)
        usage()
        sys.exit(1)
    format = 'html'
    mode = ''
    txtLineLength = 50
    htmlScale = 1.25
    pageLimit = 0
    for o, a in opts:
        if o in ('-h', '--help'):
            usage()
            sys.exit()
        elif o in ('--mode'):
            mode = a
        elif o in ('--format'):
            format = a
        elif o in ('--line'):
            try:
                txtLineLength = int(a)
            except ValueError:
                usage()
                sys.exit(1)
        elif o in ('--scale'):
            try:
                htmlScale = float(a)
            except ValueError:
                usage()
                sys.exit(1)
        elif o in ('--pagelimit'):
            try:
                pageLimit = int(a)
            except ValueError:
                usage()
                sys.exit(1)
    if format not in ['txt', 'html']:
        usage()
        sys.exit(1)
    if len(args) < 2:
        usage()
        sys.exit(1)
    inputs = args[:-1]
    output = args[-1]
    main(inputs, output, mode, format, txtLineLength, htmlScale, pageLimit)
    
def main1():
    fileNames = [r'K:\Reference\JTCSJJ\外国文学\L65.pdf']
    fileNames = [unicode(x).encode('cp936') for x in fileNames]
    main(fileNames, 'D:\\pdfconv\\ZXSQJ', 'jtcsjj', 'html', 40, 1, 0)
    
if __name__ == '__main__':
    main1()