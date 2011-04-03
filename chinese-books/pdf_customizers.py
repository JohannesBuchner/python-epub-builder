# -*- coding: utf-8 -*-
import os
import types
from pdfminer.converter import PDFPageAggregator
from pdfminer.utils import translate_matrix
from pdf_converter import Controller


class JTCSJJ_PDFPageAggregator(PDFPageAggregator):

    def __init__(self, rsrcmgr, pageno=1, laparams=None):
        PDFPageAggregator.__init__(self, rsrcmgr, pageno, laparams)

    # Overriding PDFTextDevice.render_string_horizontal()
    def render_string_horizontal(self, seq, matrix, (x,y), font, fontsize, scaling, charspace, wordspace, rise, dxscale):
        needcharspace = False
        for obj in seq:
            if isinstance(obj, int) or isinstance(obj, float):
                x -= obj*dxscale
                needcharspace = True
            else:
                try:
                    text = unicode(obj, 'cp936')
                except UnicodeDecodeError:
                    text = ''.join('\\x%X' % ord(ch) for ch in obj)
                    print 'OOPS: %s' % text
                text = text.rstrip(' ')
                if text != '':
                    cid = ord(text[0])
                    if needcharspace:
                        x += charspace
                    x += self.render_char(translate_matrix(matrix, (x,y)),
                                          font, fontsize, scaling, rise, cid, text)
                    if cid == 32 and wordspace:
                        x += wordspace
                    needcharspace = True
        return (x, y)


class JTCSJJ_Controller(Controller):
    
    def extractToc(self, pdfFile):
        pdfFile.toc = []
        for (level, title, dest, a, se) in pdfFile.getDoc().get_outlines():
            o = a.resolve()
            f = o.get('F', '')
            if f.upper() == os.path.basename(pdfFile.fileName).upper():
                d = o.get('D', [])
                if isinstance(d, types.ListType) and len(d) > 0:
                    pageId = d[0] + 1
                    pdfFile.toc.append((level, title, pageId))
    
    def getDevice(self, resourceManager):
        return JTCSJJ_PDFPageAggregator(resourceManager)


class ZJYX_Controller(Controller):

    def extractToc(self, pdfFile):
        pdfFile.toc = []
        for (level, title, dest, a, se) in pdfFile.getDoc().get_outlines():
            o = a.resolve()
            d = o.get('D', []) 
            if isinstance(d, types.ListType) and len(d) > 0:
                pageId = pdfFile.getPageId(d[0].objid)
                if pageId > 0:
                    pdfFile.toc.append((level, title, pageId))