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
        if lineNum > endLineNum:
            break
        line = line.strip()
        if PATTERN.match(line):
            section = ez_epub.Section()
            section.title = line
            sections.append(section)
        elif line == '':
            if paragraph != '':
                section.paragraphs.append(paragraph)
                paragraph = ''
        else:
            paragraph += ' ' + line
    if paragraph != '':
        section.paragraphs.append(paragraph)
    return sections

if __name__ == '__main__':
    title = 'Pride and Prejudice'
    author = 'Jane Austen'
    sections = parseBook(r'D:\epub\1342.txt', 38, 13061)
    ez_epub.makeBook(title, [author], sections, r'D:\epub\%s' % title)
            