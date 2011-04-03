# -*- coding: utf-8 -*-

import os
import re
import sys
from genshi.template import TemplateLoader
import epub

book = None

class Char:
    
    HALF_WIDTH_PUNCTUATIONS = u'.?!,;:"\'()-<>[]'
    FULL_WIDTH_PUNCTUATIONS = u'。？！，、；：“ ”‘ ’（）─…—·《 》〈 〉'
    
    def __init__(self):
        self.index = 0
        self.left = 0
        self.right = 0
        self.top = 0
        self.bottom = 0
        self.fontId = 0
        self.fontSize = 0
        self.text = ''
        self.corruptedText = None
        
    def isPunctuation(self):
        return Char.HALF_WIDTH_PUNCTUATIONS.find(self.text) != -1 or Char.FULL_WIDTH_PUNCTUATIONS.find(self.text) != -1
    
    def normalize(self):
        if book.REPLACE_FULL_WIDTH_ALNUM:
            o = ord(self.text[0])
            if 0xFF10 <= o <= 0xFF19:
                self.text = chr(ord('0') + o - 0xFF10)
            elif 0xFF21 <= o <= 0xFF3A:
                self.text = chr(ord('A') + o - 0xFF21)
            elif 0xFF41 <= o <= 0xFF5A:
                self.text = chr(ord('a') + o - 0xFF41)
                
    def isFootnoteAnchor(self):
        o = ord(self.text[0])
        return 0x2460 <= o <= 0x24FF or self.text[0] == 'B'

              
class PagePos:
    
    HEAD = 0
    BODY = 1
    FOOT = 2
    
    DESCRIPTIONS = ['HEAD', 'BODY', 'FOOT']

        
class Line:
    
    def __init__(self, page):
        self.lineNum = 0
        self.page = page
        self.chars = []
        self.footnotes = []
        self.pagePos = PagePos.BODY
        
    def getLineIndex(self):
        i = 0
        while i < len(self.page.lines):
            if self.page.lines[i] == self:
                return i
            i += 1
        return -1
        
    def getLeft(self, skipLeadingWhiteSpaces = False, adjustForPunctuation = False):
        k = self.countLeadingWhiteSpaces() if skipLeadingWhiteSpaces else 0
        if k == len(self.chars):
            book.log('OOPS: whitespace line %d.%d' % (self.page.pageNum, self.lineNum))
            return self.getRight()
        if book.ADJUST_LINE_LEFT_FOR_PUNCTUATION and adjustForPunctuation and self.chars[k].isPunctuation():
            return (self.chars[k].left + self.chars[k].right) / 2
        return self.chars[k].left
    
    def getRight(self):
        if ord(self.chars[-1].text[0]) < 128 or self.chars[-1].isPunctuation():
            return (self.chars[-1].left + self.chars[-1].right) / 2
        else:
            return self.chars[-1].right
        
    def getTop(self):
        return min(ch.top for ch in self.chars)
    
    def getBottom(self):
        return max(ch.bottom for ch in self.chars)
        
    def getText(self):
        return ''.join(ch.text for ch in self.chars)
        
    def getMinFontSize(self):
        return min(ch.fontSize for ch in self.chars)
    
    def getMaxFontSize(self):
        return max(ch.fontSize for ch in self.chars)
    
    def countLeadingWhiteSpaces(self):
        k = 0
        while k < len(self.chars) and self.chars[k].text == '　':
            k += 1
        return k
    
    
class TextFormatSnippet:
    
    def __init__(self):
        self.text = ''
        self.format = ''

        
class Section:
    
    def __init__(self):
        self.lines = []
        self.matcher = None
        self.cssClass = ''
        self.snippets = None
        
    def output(self, out):
        footnotes = []
        for line in self.lines:
            out.write(line.getText().encode('utf-8') + '\n')
            footnotes.extend(line.footnotes)
        out.write('\n\n')
        for footnote in footnotes:
            footnote.output(out)
            
    def getFootnotes(self):
        footnotes = []
        for line in self.lines:
            footnotes.extend(line.footnotes)
        return footnotes
            
    def getTextFormatSnippets(self):
        if self.snippets != None:
            return self.snippets
        snippets = []
        existingIndentation = self.lines[0].countLeadingWhiteSpaces()
        neededIndentation = 0 if book.REMOVE_INDENTATIONS else self.getIndentation()
        if neededIndentation > existingIndentation:
            snippet = TextFormatSnippet()
            snippet.text = '　' * (neededIndentation - existingIndentation)
            snippets.append(snippet)
        k = neededIndentation
        lastFormat = None
        for line in self.lines:
            for ch in line.chars:
                if k < existingIndentation:
                    k += 1
                    continue
                format = book.getFormat(line, ch)
                if format != lastFormat:
                    snippet = TextFormatSnippet()
                    snippet.format = ' '.join(format)
                    snippets.append(snippet)
                    lastFormat = format
                snippet.text += ch.text
        return snippets
    
    def getIndentation(self):
        if self.lines[0].pagePos != PagePos.BODY:
            return 0
        if len(self.lines) < 2:
            if self.matcher:
                return self.matcher.getIndentation()
            return 0
        fontSize = self.lines[0].getMaxFontSize()
        indentation = (self.lines[0].getLeft() - self.lines[1].getLeft()) / float(fontSize) + self.lines[0].countLeadingWhiteSpaces() - self.lines[1].countLeadingWhiteSpaces()
        return int(round(indentation))

        
class Chapter:
    
    def __init__(self):
        self.title = ''
        self.level = 1
        self.pageNum = 0
        self.lineNum = 0
        self.lines = []
        self.sections = []
        
    def output(self, out, lineMode = True):
        levelIndicator = '#' * (2 + self.level)
        out.write('%s %s %s\n\n' % (levelIndicator, self.title.encode('utf-8'), levelIndicator))
        if lineMode:
            for line in self.lines:
                out.write(line.getText().encode('utf-8') + '\n')
        else:
            for section in self.sections:
                section.output(out)
        out.write('\n')
        
    def makeSections(self):
        beginLineIndex  = 0
        while beginLineIndex < len(self.lines):
            if self.lines[beginLineIndex].chars == []:
                beginLineIndex += 1
                continue
            endLineIndex = -1
            matcher = None
            for sectionMatcher in book.sectionMatchers:
                endLineIndex = sectionMatcher.match(self, beginLineIndex)
                if endLineIndex != -1:
                    matcher = sectionMatcher
                    break
            if endLineIndex < beginLineIndex:
                endLineIndex = beginLineIndex
            section = Section()
            section.lines = self.lines[beginLineIndex : endLineIndex + 1]
            section.matcher = matcher
            if matcher:
                section.cssClass = matcher.cssClass
            self.sections.append(section)
            beginLineIndex = endLineIndex + 1
    
    def getAllSections(self):
        sections = []
        for section in self.sections:
            sections.append(section)
            sections.extend(section.getFootnotes())
        return sections
    

class SectionMatcher:
    
    def __init__(self):
        self.cssClass = ''
        
    def match(self, chapter, beginLineIndex):
        return -1
    

class AlignedSectionMatcher(SectionMatcher):
    
    def __init__(self):
        SectionMatcher.__init__(self)
        self.ALLOW_DIFFERENT_MAX_FONT_SIZE = True
    
    def getIndentation(self):
        return 0
    
    def getLeftAlign(self, beginLine, line):
        return line.getLeft(True, line == beginLine)
    
    def match(self, chapter, beginLineIndex):
        beginLine = chapter.lines[beginLineIndex]
        endLineIndex = beginLineIndex
        lineIndex = beginLineIndex + 1
        prevLine = beginLine
        while lineIndex < len(chapter.lines):
            if (len(prevLine.chars) < book.MIN_SECTION_LINE_SIZE \
                and (prevLine.getRight() - prevLine.getLeft()) < book.MIN_SECTION_LINE_PROPORTION * (prevLine.page.right - prevLine.page.left)) \
                or prevLine.getRight() < prevLine.page.right - book.MAX_SECTION_LINE_RIGHT_MARGIN:
                break
            curLine = chapter.lines[lineIndex]
            if not self.ALLOW_DIFFERENT_MAX_FONT_SIZE and prevLine.getMaxFontSize() != curLine.getMaxFontSize():
                break
            if curLine.page == prevLine.page and curLine.getTop() - prevLine.getBottom() > book.MAX_SECTION_LINE_Y_DIFF:
                break
            if curLine.getRight() - prevLine.getRight() > book.MAX_SECTION_LINE_X_DIFF:
                break
            if abs(self.getLeftAlign(beginLine, curLine) - self.getLeftAlign(beginLine, prevLine)) > book.MAX_SECTION_LINE_X_DIFF:
                break
            endLineIndex = lineIndex
            if prevLine.getRight() - curLine.getRight() > book.MAX_SECTION_LINE_X_DIFF:
                break
            lineIndex += 1
            prevLine = curLine
        return endLineIndex


class IndentedSectionMatcher(AlignedSectionMatcher):
    
    def __init__(self, indentation_count):
        AlignedSectionMatcher.__init__(self)
        self.indentation_count = indentation_count
        self.RE_ADJUST_INDENTATION = True
    
    def getIndentation(self):
        return self.indentation_count
    
    def getLeftAlign(self, beginLine, line):
        if line == beginLine:
            fontSize = beginLine.getMaxFontSize()
            return beginLine.getLeft(True, True) - fontSize * self.indentation_count
        return line.getLeft(True)
    
    def match(self, chapter, beginLineIndex):
        beginLine = chapter.lines[beginLineIndex]
        endLineIndex = AlignedSectionMatcher.match(self, chapter, beginLineIndex)
        if beginLineIndex == endLineIndex:
            for pos in book.COMMON_SECTION_FIRST_LINE_LEFT:
                if abs(beginLine.getLeft(True, True) - pos) <= 3:
                    return beginLineIndex
            return -1
        elif self.RE_ADJUST_INDENTATION:
            temp = self.indentation_count
            self.indentation_count = 2
            lineIndex = self.match(chapter, endLineIndex)
            self.indentation_count = temp
            if lineIndex > endLineIndex:
                book.log("OOPS: re-adjusting indentation: %d-%d" % (beginLine.page.pageNum, beginLine.lineNum))
                return endLineIndex - 1
        return endLineIndex

        
class Block:
    
    def __init__(self):
        self.left = 0
        self.right = 0
        self.top = 0
        self.bottom = 0
        self.blockType = ''
        
    def equals(self, other):
        return self.left == other.left and self.right == other.right and self.top == other.top and self.bottom == other.bottom and self.blockType == other.blockType

    
class Page:
    
    def __init__(self, book):
        self.pageNum = 0
        self.book = book
        self.fileName = ''
        self.chars = []
        self.blocks = []
        self.lines = []
        self.left = 0
        self.right = 0
        self.top = 0
        self.bottom = 0
        self.footnotes = []
        
    def getLine(self, lineNum):
        for line in self.lines:
            if line.lineNum == lineNum:
                return line
        return None
        
    def getBlock(self, blockType, blockIndex, minBlockWidth = 30):
        k = 0
        for block in self.blocks:
            if block.blockType == blockType:
                if k == blockIndex and block.right - block.left > minBlockWidth:
                    return block
                k += 1
        return None
        
    def parseHTML(self):
        fin = open(self.fileName)
        pat1 = re.compile(r'<!-- (.+) (\d+) (\d+) (\d+) (\d+) --><div')
        pat2 = re.compile(r'<!-- (\d+) (\d+) (\d+) (\d+) --><span class="f(\d+)_(\d+)"[^>]*>([^<]*)(<!-- (.+) -->)?</span>')
        for line in fin:
            match = pat1.match(line)
            if match:
                block = Block()
                block.blockType = match.group(1)
                block.left = int(match.group(2))
                block.top = int(match.group(3))
                block.right = int(match.group(4))
                block.bottom = int(match.group(5))
                foundDuplicate = False
                for b in self.blocks:
                    if block.equals(b):
                        foundDuplicate = True
                if foundDuplicate:
                    book.log("OOPS: duplicate found")
                    break
                if block.blockType == 'LTUnderline':
                    line = '<!-- %d %d %d %d --><span class="f0_10" style="position:absolute; left:%dpx; top:%dpx;">＿＿</span>' % (block.left, block.top, block.right, block.bottom, block.left, block.top)
                else:
                    self.blocks.append(block)
                    continue
            match = pat2.match(line)
            if match:
                ch = Char()
                ch.index = len(self.chars)
                ch.left = int(match.group(1))
                ch.top = int(match.group(2))
                ch.right = int(match.group(3))
                ch.bottom = int(match.group(4))
                ch.fontId = int(match.group(5))
                ch.fontSize = int(match.group(6))
                ch.text = unicode(match.group(7), 'utf-8')
                if ch.text == '':
                    book.log('OOPS: empty text')
                    continue 
                if match.group(9):
                    ch.corruptedText = match.group(9).replace('\\x', '')
                    if ch.corruptedText.endswith('20'):
                        ch.corruptedText = ch.corruptedText[:-2]
                ch.normalize()
                if ch.corruptedText:
                    book.replaceCorruptedText(self, ch)
                self.chars.append(ch)

    def output(self, out):
        out.write('[%s]\n\n' % os.path.basename(self.fileName))
        lastPagePos = None
        for line in self.lines:
            if line.pagePos != lastPagePos:
                out.write('(%s)\n' % PagePos.DESCRIPTIONS[line.pagePos])
            out.write(line.getText().encode('utf-8') + '\n')
            lastPagePos = line.pagePos
        out.write('\n')
        
    def makeLines(self):
        line = None
        for ch in self.chars:
            if line == None or (abs(line.chars[-1].bottom - ch.bottom) > book.NEW_LINE_Y_DIFF and abs(line.chars[-1].top - ch.top) > book.NEW_LINE_Y_DIFF):
                line = Line(self)
                self.lines.append(line)
            line.chars.append(ch)
            
        self.markHeadFoot()

        self.lines.sort(key = lambda line : line.chars[0].bottom)
        lines = []
        lastLine = None
        for line in self.lines:
            if lastLine != None and line.pagePos == lastLine.pagePos and line.chars[0].bottom - lastLine.chars[0].bottom <= book.NEW_LINE_Y_DIFF:
                lastLine.chars.extend(line.chars)
            else:
                lines.append(line)
                lastLine = line
        self.lines = lines
        for line in self.lines:
            line.chars.sort(cmp = lambda ch1, ch2: ch1.left - ch2.left if ch1.left != ch2.left else ch1.bottom - ch2.bottom)
            
        self.adjustTitleFootnote()
            
        lineNum = 1
        for line in self.lines:
            if line.pagePos == PagePos.BODY:
                line.lineNum = lineNum
                lineNum += 1
            
    def adjustTitleFootnote(self):
        k = 0
        while k < len(self.lines):
            if self.lines[k].pagePos == PagePos.BODY:
                break
            k += 1
        if k < len(self.lines) and len(self.lines[k].chars) == 1 and self.lines[k].chars[0].isFootnoteAnchor():
            self.lines[k + 1].chars.extend(self.lines[k].chars)
            del self.lines[k]
            book.log("OOPS: placing footnote after title: %d" % self.pageNum)

    def markHeadFoot(self):
        if len(self.chars) == 0:
            return
        book.markHeadFoot(self)
                        
        footnote = None
        for line in self.lines:
            if line.pagePos == PagePos.FOOT:
                k = 0
                while k < len(line.chars):
                    if line.chars[k].text not in ['　', ' ']:
                        break
                    k += 1
                if k == len(line.chars):
                    continue
                if line.chars[k].isFootnoteAnchor():
                    footnote = Section()
                    self.footnotes.append((line.chars[k].text, footnote))
                elif footnote == None:
                    footnote = Section()
                    self.footnotes.append(('', footnote))
                footnote.lines.append(line)
        self.anchorFootnotes()
                
    def anchorFootnotes(self):
        if book.IGNORE_FOOTNOTES or self.footnotes == []:
            return
        anchors = []
        used = set()
        lastLine = None
        for line in self.lines:
            if line.pagePos == PagePos.BODY:
                lastLine = line
                for ch in line.chars:
                    if ch.isFootnoteAnchor():
                        anchors.append((ch, line))
        for anchor, footnote in self.footnotes:
            found = False
            for ch, line in anchors:
                if ch not in used and anchor == ch.text:
                    line.footnotes.append(footnote)
                    used.add(ch)
                    found = True
                    break
            if not found:
                lastLine.footnotes.append(footnote)
        if len(anchors) != len(self.footnotes) or len(anchors) != len(used):
            book.log('OOPS: footnote anchoring: %d' % self.pageNum)

class TOCEntry:
    
    def __init__(self):
        self.pageNum = 0
        self.lineNum = 0
        self.level = 1
        self.title = ''

            
class Book:
    
    def __init__(self):
        global book
        book = self
        
        self.REPLACE_FULL_WIDTH_ALNUM = True
        
        self.NEW_LINE_Y_DIFF = 6

        self.PAGE_BOUNDING_BOX_INDEX = 1
        self.PAGE_BOUNDING_BOX = None

        self.HAS_PAGE_HEAD = True
        self.PAGE_HEAD_LINE_INDEX = 0
        self.PAGE_HEAD_LINE_TYPE = 'LTLine'
        self.PAGE_HEAD_MARGIN = 10
        self.HAS_PAGE_FOOT = False
        self.PAGE_FOOT_LINE_INDEX = 1
        self.PAGE_FOOT_LINE_TYPE = 'LTLine'
        self.PAGE_FOOT_MARGIN = 10
        self.IGNORE_FOOTNOTES = False
        
        self.FONT_SIZE_FOR_CHAPTER = 16
        self.CHAPTER_TITLE_PATTERNS = [unicode(r'[一二三四五六七八九十百○]+$'), unicode(r'[　\s]*第[　\s]*[一二三四五六七八九十百]+[　\s]*[回章节部幕]([　\s]|\Z)')]
        self.USE_TOC_FILE = False
        self.CENTER_ALIGN_DIFF_FOR_CHAPTER = 0
        self.CENTER_ALIGN_MARGIN_FOR_CHAPTER = 100
        
        self.ADJUST_LINE_LEFT_FOR_PUNCTUATION = True
        self.MIN_SECTION_LINE_SIZE = 20
        self.MIN_SECTION_LINE_PROPORTION = 0.8
        self.MAX_SECTION_LINE_Y_DIFF = 15
        self.MAX_SECTION_LINE_X_DIFF = 10
        self.MAX_SECTION_LINE_RIGHT_MARGIN = 50
        self.COMMON_SECTION_FIRST_LINE_LEFT = [101]
        
        self.REMOVE_INDENTATIONS = True
        
        self.MAIN_TEXT_FONT_SIZE = 12
        
        self.TITLE_PAGE_TEMPLATE = 'jtcsjj-title.html'
        self.PAGE_TEMPLATE = 'jtcsjj.html'

        self.pages = []
        self.sections = []
        self.chapters = []
        self.dirName = ''
        self.outputFileName = ''
        self.fileNames = []
        self.imagePaths = []
        self.pageRange = None
        self.excludedPages = {}
        self.markedChapters = {}
        self.tocChapters = {}
        self.corruptedTextReplacement = {}

        self.authors = []
        self.translators = []

        self.sectionMatchers = [IndentedSectionMatcher(2), IndentedSectionMatcher(0)]
        
        self.logFileName = ''
        self.logFile = None
        
    def log(self, str):
        print str
        if self.logFileName != '' and not self.logFile:
            self.logFile = open(self.logFileName, 'w')
        if self.logFile:
            self.logFile.write(str + '\n')

    def parseTOCFile(self):
        self.tocChapters = {}
        fin = open(os.path.join(self.dirName, 'toc.htm'))
        pat = re.compile(r'<div style="text-indent:(\d+)em;"><a href="(\d+).htm">(.*)</a></div>')
        for line in fin:
            match = pat.match(line)
            if match:
                entry = TOCEntry()
                entry.level = int(match.group(1)) / 2
                if entry.level < 1:
                    continue
                entry.pageNum = int(match.group(2))
                entry.title = unicode(match.group(3))
                self.tocChapters.setdefault(entry.pageNum, []).append(entry)
        
    def parseHTML(self):
        pat = re.compile(r'(\d+).htm')
        l = []
        for fileName in os.listdir(self.dirName):
            match = pat.match(fileName)
            if match:
                l.append(int(match.group(1)))
        self.fileNames = ['%d.htm' % x for x in sorted(l)]
        pageNum = 1
        if self.pageRange:
            self.fileNames = self.fileNames[self.pageRange[0] - 1 : self.pageRange[1]]
            pageNum = self.pageRange[0]
        for fileName in self.fileNames:
            self.log(fileName)
            page = Page(self)
            page.pageNum = pageNum
            pageNum += 1
            page.fileName = os.path.join(self.dirName, fileName)
            page.parseHTML()
            boundingBox = self.getPageBoundingBox(page)
            if boundingBox:
                page.left, page.top, page.right, page.bottom = boundingBox 
            self.pages.append(page)
            
    def listImages(self):
        imgDirName = os.path.join(self.dirName, 'images')
        pat = re.compile(r'(\d+).jpg')
        l = []
        for fileName in os.listdir(imgDirName):
            match = pat.match(fileName)
            if match:
                l.append(int(match.group(1)))
        self.imagePaths = [os.path.join(imgDirName, '%d.jpg') % x for x in sorted(l)]

    def getPageBoundingBox(self, page):
        if book.PAGE_BOUNDING_BOX_INDEX >= 0:
            block = page.getBlock('LTRect', book.PAGE_BOUNDING_BOX_INDEX)
            if block:
                return (block.left, block.top, block.right, block.bottom)
        if book.PAGE_BOUNDING_BOX:
            return book.PAGE_BOUNDING_BOX
        return None
    
    def adjustPages(self):
        pass
    
    def adjustSections(self):
        pass
    
    def process(self):
        if self.USE_TOC_FILE:
            self.parseTOCFile()
        self.listImages()
        self.parseHTML()
        for page in self.pages:
            if page.pageNum in self.excludedPages:
                continue
            page.makeLines()
        self.adjustPages()
        self.makeChapters()
        for chapter in self.chapters:
            chapter.makeSections()
        self.adjustSections()

    def getTitlePageLines(self):
        lines = []
        lines.append(('title', self.title))
        lines.append(('author', '　 '.join(self.authors) + '　著'))
        if len(self.translators) > 0:
            lines.append(('translator', '　 '.join(self.translators) + '　译'))
        return lines
                
    def replaceCorruptedText(self, page, ch):
        if ch.corruptedText in self.corruptedTextReplacement:
            ch.text = self.corruptedTextReplacement[ch.corruptedText]

    def getFormat(self, line, ch):
        format = []
        if ch.fontSize > book.MAIN_TEXT_FONT_SIZE:
            format.append('larger')
        elif ch.fontSize < book.MAIN_TEXT_FONT_SIZE:
            format.append('smaller')
        return format

    def markNoChapter(self, pageNum, lineNum):
        self.markChapter(pageNum, lineNum, -1, None)
                        
    def markChapter(self, pageNum, lineNum, level, title):
        self.markedChapters[(pageNum, lineNum)] = (title, level)
        
    def markHeadFoot(self, page):
        if self.HAS_PAGE_HEAD:
            if self.PAGE_HEAD_LINE_INDEX >= 0:
                block = page.getBlock(self.PAGE_HEAD_LINE_TYPE, self.PAGE_HEAD_LINE_INDEX)
                if block:
                    for line in page.lines:
                        if line.chars[0].top < block.top:
                            line.pagePos = PagePos.HEAD
            else:
                for line in page.lines:
                    if line.chars[0].top < page.top + self.PAGE_HEAD_MARGIN:
                        line.pagePos = PagePos.HEAD
        if self.HAS_PAGE_FOOT:
            if self.PAGE_FOOT_LINE_INDEX >= 0:
                block = page.getBlock(self.PAGE_FOOT_LINE_TYPE, self.PAGE_FOOT_LINE_INDEX)
                if block:
                    for line in page.lines:
                        if line.chars[0].bottom > block.bottom:
                            line.pagePos = PagePos.FOOT
            else:
                for line in page.lines:
                    if line.chars[0].bottom > page.bottom - self.PAGE_FOOT_MARGIN:
                        line.pagePos = PagePos.FOOT
        
    def makeChapters(self):
        chapterTitlePatterns = [re.compile(x) for x in book.CHAPTER_TITLE_PATTERNS]
        chapter = None
        for page in self.pages:
            if page.pageNum in self.excludedPages:
                continue
            for line in page.lines:
                if line.pagePos != PagePos.BODY:
                    continue
                if line.chars == []:
                    continue
                lineText = line.getText()
                title, level = self.markedChapters.get((page.pageNum, line.lineNum), (None, None))
                if level == None and self.USE_TOC_FILE:
                    tocEntries = self.tocChapters.get(page.pageNum)
                    if tocEntries:
                        for tocEntry in tocEntries:
                            if tocEntry.title == lineText:
                                title = tocEntry.title
                                level = tocEntry.level
                                break
                if level == None:
                    foundChapter = False
                    if self.chapters == []:
                        foundChapter = True
                    elif book.FONT_SIZE_FOR_CHAPTER > 0 and line.getMaxFontSize() >= book.FONT_SIZE_FOR_CHAPTER:
                        foundChapter = True
                    elif book.CENTER_ALIGN_DIFF_FOR_CHAPTER > 0:
                        if abs(line.getLeft() + line.getRight() - page.left - page.right) < book.CENTER_ALIGN_DIFF_FOR_CHAPTER:
                            if line.getLeft() > page.left + book.CENTER_ALIGN_MARGIN_FOR_CHAPTER:
                                foundChapter = True
                    else:
                        for chapterTitlePattern in chapterTitlePatterns:
                            if chapterTitlePattern.match(lineText):
                                foundChapter = True
                                break
                    level = self.getChapterLevel(page, line) if foundChapter else - 1
                if level != -1:
                    if title == None:
                        title = self.getChapterTitle(page, line)
                    chapter = Chapter()
                    chapter.pageNum = page.pageNum
                    chapter.lineNum = line.lineNum
                    chapter.title = title
                    chapter.level = level
                    self.chapters.append(chapter)
                if chapter:
                    chapter.lines.append(line)
    
    def getChapterTitle(self, page, line):
        return line.getText()
    
    def getChapterLevel(self, page, line):
        return 1
    
    def outputPages(self, fileName):
        fout = open(fileName, 'w')
        for page in self.pages:
            page.output(fout)
            
    def outputChapters(self, fileName):
        fout = open(fileName, 'w')
        for chapter in self.chapters:
            fout.write('%d %d %d %s\n' % (chapter.pageNum, chapter.lineNum, chapter.level, chapter.title))
        fout.write('\n')
        for chapter in self.chapters:
            chapter.output(fout, True)
            
    def outputSections(self, fileName):
        fout = open(fileName, 'w')
        indentations = {}
        for chapter in self.chapters:
            for section in chapter.sections:
                left = section.lines[0].getLeft(True, True)
                indentation = section.getIndentation()
                indentations.setdefault((left, indentation), []).append(section)
        for (left, indentation), sections in sorted(indentations.iteritems()):
            if len(sections) < 10:
                continue
            fout.write('%d %d %d\n  ' % (left, indentation, len(sections)))
            pageNumSet = set()
            for section in sections:
                if section.lines[0].page.pageNum not in pageNumSet:
                    fout.write('%d.%d ' % (section.lines[0].page.pageNum, section.lines[0].lineNum))
                    pageNumSet.add(section.lines[0].page.pageNum)
                    if len(pageNumSet) >= 10:
                        break
            fout.write('\n')
        fout.write('\n')
        for chapter in self.chapters:
            chapter.output(fout, False)
            
    def outputHeaders(self, fileName):
        fout = open(fileName, 'w')
        for page in self.pages:
            lines = [line for line in page.lines if line.pagePos == PagePos.HEAD and line.chars != []]
            if lines != []:
                fout.write('%d> ' % page.pageNum)
                for line in lines:
                    fout.write('%s\n' % line.getText())
                    
    def outputFooters(self, fileName):
        fout = open(fileName, 'w')
        for page in self.pages:
            lines = [line for line in page.lines if line.pagePos == PagePos.FOOT and line.chars != []]
            if lines != []:
                fout.write('%d> ' % page.pageNum)
                for line in lines:
                    fout.write('%s\n' % line.getText())
            
    def outputCorruptedText(self, fileName):
        corrupted = {}
        firstOccurrence = {}
        for page in self.pages:
            for line in page.lines:
                for ch in line.chars:
                    if ch.corruptedText:
                        corrupted.setdefault(ch.corruptedText, []).append(line)
                        firstOccurrence.setdefault(ch.corruptedText, (line.page.pageNum, line.lineNum))
        fout = open(fileName, 'w')
        for corruptedText, _ in sorted(firstOccurrence.iteritems(), key = lambda x: x[1]):
            correctText = book.corruptedTextReplacement.get(corruptedText, '')
            fout.write("self.corruptedTextReplacement['%s'] = '%s'\n" % (corruptedText, correctText))
        fout.write('\n')
        for corruptedText, _ in sorted(firstOccurrence.iteritems(), key = lambda x: x[1]):
            lines = corrupted[corruptedText]
            correctText = book.corruptedTextReplacement.get(corruptedText, '')
            fout.write('%s %s\n' % (corruptedText, correctText))
            for line in lines:
                fout.write(line.getText() + '\n')
            fout.write('\n')
            
    def outputEPub(self, rootDir):
        ep = epub.EpubBook()
        ep.setLang('zh-CN')
        ep.setTitle(self.title)
        for author in self.authors:
            ep.addCreator(author)
        for translator in self.translators:
            ep.addCreator(translator, 'trl');

        loader = TemplateLoader('templates')
        tmpl = loader.load(self.TITLE_PAGE_TEMPLATE)
        stream = tmpl.generate(lines = self.getTitlePageLines())
        html = stream.render('xhtml', doctype='xhtml11', drop_xml_decl=False)
        ep.addTitlePage(html)
        
        ep.addTocPage()
        ep.addCover(self.imagePaths[0])
        
        tmpl = loader.load(self.PAGE_TEMPLATE)
        for i, imagePath in enumerate(self.imagePaths):
            imageItem = ep.addImage(imagePath, 'img%d.jpg' % (i + 1))
            htmlItem = ep.addHtmlForImage(imageItem)
            ep.addSpineItem(htmlItem)
        for k, chapter in enumerate(self.chapters):
            stream = tmpl.generate(chapter = chapter)
            html = stream.render('xhtml', doctype='xhtml11', drop_xml_decl=False)
            item = ep.addHtml('', 'ch%d.html' % (k + 1), html)
            ep.addSpineItem(item)
            if chapter.title != '':
                ep.addTocMapNode(item.destPath, chapter.title, chapter.level)
        
        if self.outputFileName == '':
            self.outputFileName = self.title
        outputDir = os.path.join(rootDir, self.outputFileName.encode('cp936'))
        outputFile = os.path.join(rootDir, self.outputFileName.encode('cp936') + '.epub')
        ep.createBook(outputDir)
        ep.createArchive(outputDir, outputFile)
        ep.checkEpub('epubcheck-1.1.jar', outputFile)