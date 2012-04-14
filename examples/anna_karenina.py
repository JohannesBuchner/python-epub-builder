# -*- coding: utf-8 -*-

# Copyright (c) 2012, Bin Tan
# This file is distributed under the BSD Licence. See python-epub-builder-license.txt for details.

import re
import ez_epub

def formatParagraph(paragraph):
    paragraph = paragraph.replace('--', '—')
    paragraph = re.sub(r' +', ' ', paragraph)
    paragraph = re.sub(r'_(.+?)_', r'<i>\1</i>', paragraph)
    return segmentParagraph(paragraph)

def segmentParagraph(paragraph):
    segments = []
    textStart = 0
    style = []
    nesting = 0
    for match in re.finditer(r'<(/?)([^>]+)>', paragraph):
        if match.start() > textStart:
            segments.append((paragraph[textStart : match.start()], ' '.join(style)))
        if match.group(1) == '':
            style.append(match.group(2))
            nesting += 1
        else:
            style.remove(match.group(2))
            nesting -= 1
        textStart = match.end()
    if textStart < len(paragraph):
        segments.append((paragraph[textStart :], ' '.join(style)))
    if nesting != 0:
        print 'oops:', paragraph
    return segments
    
def parseBook(path, startLineNum, endLineNum):
    PART_PATTERN = re.compile(r'Part \d+$')
    CHAPTER_PATTERN = re.compile(r'Chapter \d+$')
    parts = []
    paragraph = ''
    fin = open(path)
    lineNum = 0
    for line in fin:
        lineNum += 1
        if lineNum < startLineNum:
            continue
        if endLineNum > 0 and lineNum > endLineNum:
            break
        line = unicode(line, 'utf-8')
        line = line.strip()
        if PART_PATTERN.match(line):
            part = ez_epub.Section()
            part.title = line
            parts.append(part)
        elif CHAPTER_PATTERN.match(line):
            chapter = ez_epub.Section()
            chapter.title = line
            part.subsections.append(chapter)
        elif line == '':
            if paragraph != '':
                chapter.text.append(formatParagraph(paragraph))
                paragraph = ''
        else:
            if paragraph != '':
                paragraph += ' '
            paragraph += line
    if paragraph != '':
        chapter.text.append(formatParagraph(paragraph))
    return parts

if __name__ == '__main__':
    book = ez_epub.Book()
    book.title = 'Anna Karenina'
    book.authors = ['Leo Tolstoy']
    book.sections = parseBook(r'D:\epub\pg1399.txt', 44, 43219)
    book.make(r'D:\epub\%s' % book.title)

            
