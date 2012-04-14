# -*- coding: utf-8 -*-

# Copyright (c) 2012, Bin Tan
# This file is distributed under the BSD Licence. See python-epub-builder-license.txt for details.

import re
import ez_epub

def formatParagraph(paragraph):
    paragraph = paragraph.replace('--', '¡ª')
    paragraph = re.sub(r' +', ' ', paragraph)
    paragraph = re.sub(r'_(.+?)_', r'<em>\1</em>', paragraph)
    return segmentParagraph(paragraph)

def segmentParagraph(paragraph):
    segments = []
    textStart = 0
    style = []
    for match in re.finditer(r'<(/?)([^>]+)>', paragraph):
        if match.start() > textStart:
            segments.append((paragraph[textStart : match.start()], ' '.join(style)))
        if match.group(1) == '':
            style.append(match.group(2))
        else:
            style.remove(match.group(2))
        textStart = match.end()
    if textStart < len(paragraph):
        segments.append((paragraph[textStart :], ' '.join(style)))
    return segments
    
def parseBook(path, startLineNum, endLineNum):
    PATTERN = re.compile(r'Chapter \d+$')
    sections = []
    paragraph = ''
    fin = open(path)
    lineNum = 0
    for line in fin:
        lineNum += 1
        if lineNum < startLineNum:
            continue
        if endLineNum > 0 and lineNum > endLineNum:
            break
        line = line.strip()
        if PATTERN.match(line):
            section = ez_epub.Section()
            section.css = """.em { font-style: italic; }"""
            section.title = line
            sections.append(section)
        elif line == '':
            if paragraph != '':
                section.text.append(formatParagraph(paragraph))
                paragraph = ''
        else:
            if paragraph != '':
                paragraph += ' '
            paragraph += line
    if paragraph != '':
        section.text.append(formatParagraph(paragraph))
    return sections

if __name__ == '__main__':
    book = ez_epub.Book()
    book.title = 'Pride and Prejudice'
    book.authors = ['Jane Austen']
    book.sections = parseBook(r'D:\epub\1342.txt', 38, 13061)
    book.make(r'D:\epub\%s' % book.title)
