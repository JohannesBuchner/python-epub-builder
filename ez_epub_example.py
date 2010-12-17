# -*- coding: utf-8 -*-

import re
import ez_epub

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
                section.text.append(paragraph)
                paragraph = ''
        else:
            if paragraph != '':
                paragraph += ' '
            paragraph += line
    if paragraph != '':
        section.text.append(paragraph)
    return sections

if __name__ == '__main__':
    book = ez_epub.Book()
    book.title = 'Pride and Prejudice'
    book.authors = ['Jane Austen']
    book.sections = parseBook(r'D:\epub\1342.txt', 38, 13061)
    book.make(r'D:\epub\%s' % book.title)
