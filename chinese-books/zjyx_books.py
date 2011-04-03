# -*- coding: utf-8 -*-

from html_to_epub import *

class ZJYSBook(Book):
    
    def __init__(self):
        Book.__init__(self)
        self.HAS_PAGE_HEAD = False
        self.PAGE_FOOT_LINE_TYPE = 'LTRect'
        self.PAGE_FOOT_LINE_INDEX = 0
        self.PAGE_BOUNDING_BOX = (111, 73, 487, 764)
        self.COMMON_SECTION_FIRST_LINE_LEFT = [135]
        self.USE_TOC_FILE = True
        self.ADJUST_LINE_LEFT_FOR_PUNCTUATION = False
        
    def adjustPages(self):
        for page in self.pages:
            for line in page.lines:
                if line.pagePos == PagePos.FOOT:
                    for ch in line.chars:
                        ch.text = ch.text.strip(' ')


class ANKLNN2(ZJYSBook):
    
    def __init__(self):
        ZJYSBook.__init__(self)
        self.title = '安娜·卡列尼娜2'
        self.outputFileName = '安娜·卡列尼娜2'
        self.authors = ['列夫·托尔斯泰']
        self.translators = ['草婴']
        self.dirName = 'D:\\pdfconv\\ANKLNN2'
        self.HAS_PAGE_FOOT = True
        self.excludedPages = []
        self.markChapter(8, 1, 1, '安娜·卡列尼娜')
        self.markChapter(533, 1, 1, '《安娜·卡列尼娜》各章内容概要')
        
    def adjustPages(self):
        ZJYSBook.adjustPages(self)
        for page in self.pages:
            if page.pageNum >= 533:
                for line in page.lines:
                    for ch in line.chars:
                        ch.text = ch.text.replace('□', '　')

def main():
    book = ANKLNN2()
    book.pageRange = (1, 10000)
    book.logFileName = 'D:\\epubconv\\log.txt'
    book.process()
    book.outputPages('D:\\epubconv\\pages.txt')
    book.outputChapters('D:\\epubconv\\chapters.txt')
    book.outputSections('D:\\epubconv\\sections.txt')
    book.outputCorruptedText('D:\\epubconv\\corrupted.txt')
    book.outputHeaders('D:\\epubconv\\header.txt')
    book.outputFooters('D:\\epubconv\\footer.txt')
    book.outputEPub('D:\\epubconv')
 
if __name__ == '__main__': 
    main()