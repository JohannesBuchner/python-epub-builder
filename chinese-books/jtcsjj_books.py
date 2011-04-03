# -*- coding: utf-8 -*-

from html_to_epub import *

class ANKLNN1(Book):
    
    def __init__(self):
        Book.__init__(self)
        self.title = '安娜·卡列尼娜'
        self.authors = ['列夫·托尔斯泰']
        self.translators = ['周扬']
        self.dirName = 'D:\\pdfconv\\ANKLNN1'
        self.HAS_PAGE_FOOT = True
        self.excludedPages = [1, 2, 10, 644]
        self.markChapter(11, 1, 1, '')
        self.corruptedTextReplacement['BE'] = '綷'
    
    def getChapterTitle(self, page, line):
        return line.getText().replace('　', '')
    
    def getChapterLevel(self, page, line):
        if re.match(self.CHAPTER_TITLE_PATTERNS[0], line.getText()):
            return 2
        return 1
    
    
class SHQZ(Book):
    
    def __init__(self):
        Book.__init__(self)
        self.title = '水浒全传'
        self.authors = ['施耐庵', '罗贯中']
        self.dirName = 'D:\\pdfconv\\SHQZ'
        self.excludedPages = [1, 2, 17, 18, 19, 20]
        self.markChapter(21, 1, 1, '')
        
        self.corruptedTextReplacement['AFA7'] = '磁'
        self.corruptedTextReplacement['AEDC'] = '㨄'
        self.corruptedTextReplacement['AAF8'] = '犴'
        self.corruptedTextReplacement['ADB6'] = '（月荅）'
        self.corruptedTextReplacement['AFBD'] = '凫'
        self.corruptedTextReplacement['AFC4'] = '焠'
        self.corruptedTextReplacement['AFC5'] = '（巾贯）'
        self.corruptedTextReplacement['AFC6'] = '跷'
        self.corruptedTextReplacement['ACAE'] = '（足垔）'
        self.corruptedTextReplacement['FE80'] = '䜣 '
        self.corruptedTextReplacement['AEEE'] = '祯'
        self.corruptedTextReplacement['92'] = '抃'
        
    def getTitlePageLines(self):
        lines = Book.getTitlePageLines(self)
        lines.append(('editor', '李希凡　前言'))
        lines.append(('editor', '唐富龄　标点'))
        return lines
    
    def getChapterTitle(self, page, line):
        title = line.getText()
        if title.find('回') == -1:
            title = title.replace('　', '')
        return title
    
    def getChapterLevel(self, page, line):
        if re.match(self.CHAPTER_TITLE_PATTERNS[0], line.getText()):
            return 2
        return 1
    

class SGYY(Book):
    
    def __init__(self):
        Book.__init__(self)
        self.title = '三国演义'
        self.authors = ['罗贯中']
        self.dirName = 'D:\\pdfconv\\SGYY'
        self.excludedPages = [1, 2, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26]
        self.markNoChapter(15, 11)
        self.markChapter(27, 1, 1, '')
        self.COMMON_SECTION_FIRST_LINE_LEFT = [101, 105]
        
        self.corruptedTextReplacement['FE8B'] = '䦆'
        self.corruptedTextReplacement['F8B5'] = '（犭票）'
        self.corruptedTextReplacement['F8B7'] = '蹙'
        self.corruptedTextReplacement['F8B0'] = '（舟冓）'
        self.corruptedTextReplacement['F8B1'] = '（舟鹿）'
        self.corruptedTextReplacement['F8AF'] = '㪍'
        self.corruptedTextReplacement['F8B6'] = '（马宛）'
        self.corruptedTextReplacement['F8AD'] = '拘'
        self.corruptedTextReplacement['F8AC'] = '濦'
        self.corruptedTextReplacement['F8B2'] = '虢'
        self.corruptedTextReplacement['F8B3'] = '（青彡）'
        self.corruptedTextReplacement['F8B4'] = '（雨单）'
        
    def getTitlePageLines(self):
        lines = Book.getTitlePageLines(self)
        lines.append(('editor', '聂绀弩　前言'))
        lines.append(('editor', '朱正　标点'))
        return lines
    
    def getChapterLevel(self, page, line):
        if line.getText().find('回') != -1:
            secondLine = page.lines[line.getLineIndex() + 1]
            line.chars[-1].text += '　'
            line.chars.extend(secondLine.chars)
            secondLine.chars = []
        return 1
    
    def getChapterTitle(self, page, line):
        title = line.getText()
        if title.find('回') == -1:
            title = title.replace('　', '')
        return title
     
    def getFormat(self, line, ch):
        if line.page.pageNum <= 15 and ch.fontSize == 14:
            return []
        return Book.getFormat(self, line, ch)
    
    
class XYJ(Book):
    
    def __init__(self):
        Book.__init__(self)
        self.title = '西游记'
        self.authors = ['吴承恩']
        self.dirName = 'D:\\pdfconv\\XYJ'
        self.PAGE_HEAD_LINE_INDEX = -1
        self.excludedPages = [1, 2, 12, 13, 14, 15]
        self.markNoChapter(11, 9)
        
        self.corruptedTextReplacement['FE6A'] = '㳠'
        self.corruptedTextReplacement['FDEC'] = '咪'
        self.corruptedTextReplacement['EB'] = '骘'
        self.corruptedTextReplacement['FEBE'] = '埵'
        self.corruptedTextReplacement['FEE0'] = '跨'
        self.corruptedTextReplacement['B022'] = '狍'
        self.corruptedTextReplacement['B02E'] = '（矢犮）'
        self.corruptedTextReplacement['B334'] = '（山兜）'
        
    def getChapterTitle(self, page, line):
        title = line.getText()
        if title.find('回') == -1:
            title = title.replace('　', '')
        else:
            title = title.replace('　　', '　')
        return title
    
    def getChapterLevel(self, page, line):
        if re.match(self.CHAPTER_TITLE_PATTERNS[0], line.getText()):
            return 2
        return 1
    
    def getTitlePageLines(self):
        lines = Book.getTitlePageLines(self)
        lines.append(('editor', '何满子　前言'))
        lines.append(('editor', '劼父　标点'))
        return lines


class HLM(Book):
    
    def __init__(self):
        Book.__init__(self)
        self.title = '红楼梦'
        self.authors = ['曹雪芹', '高鹗']
        self.dirName = 'D:\\pdfconv\\HLM'
        self.HAS_PAGE_FOOT = True
        self.PAGE_FOOT_LINE_INDEX = -1
        self.IGNORE_FOOTNOTES = True
        self.excludedPages = [2, 22, 23, 24, 25, 26]
        self.markNoChapter(21, 16)
        self.markChapter(27, 1, 1, '')
        
        self.corruptedTextReplacement['AEDB'] = '（扌层）'
        self.corruptedTextReplacement['AEDA'] = '㩙'
        self.corruptedTextReplacement['AEF0'] = '（火敝）'
        self.corruptedTextReplacement['F8C9'] = '福'
        self.corruptedTextReplacement['F8C8'] = '卐'
        self.corruptedTextReplacement['AEF4'] = '（木靠）'
        self.corruptedTextReplacement['AEF5'] = '飺'
        self.corruptedTextReplacement['AEF7'] = '犟'
        self.corruptedTextReplacement['AFB3'] = '（走佥）'
        self.corruptedTextReplacement['AFB2'] = '（走真）'
        self.corruptedTextReplacement['AFB4'] = '䰖'
        self.corruptedTextReplacement['FE72'] = '紬'
        self.corruptedTextReplacement['ABD0'] = '蘼'
        self.corruptedTextReplacement['ACF2'] = '（毛几）'
        self.corruptedTextReplacement['ACF3'] = '（毛巴）'
        self.corruptedTextReplacement['AFAC'] = '籤'
        self.corruptedTextReplacement['AEE6'] = '（纟蒙）'
        self.corruptedTextReplacement['FED9'] = '縠'
        self.corruptedTextReplacement['AEEB'] = '㻞'
        self.corruptedTextReplacement['AEED'] = '玕'
        self.corruptedTextReplacement['AFC0'] = '碌'
        self.corruptedTextReplacement['AFC1'] = '（口留）'
        self.corruptedTextReplacement['AFC2'] = '（口邦）'
        self.corruptedTextReplacement['AFA8'] = '（台皿）'
        self.corruptedTextReplacement['AFA9'] = '（分瓜）'
        self.corruptedTextReplacement['AFA4'] = '匵'
        self.corruptedTextReplacement['AFBC'] = '鶒'
        #self.corruptedTextReplacement['AFBE'] = ''
        self.corruptedTextReplacement['ABC4'] = '簦'
        self.corruptedTextReplacement['F8CA'] = '寿'
        self.corruptedTextReplacement['AEFE'] = '（乌刂）'
    
    def getChapterTitle(self, page, line):
        title = line.getText()
        if title.find('回') == -1:
            title = title.replace('　', '')
        return title
    
    def getChapterLevel(self, page, line):
        if re.match(self.CHAPTER_TITLE_PATTERNS[0], line.getText()):
            return 2
        return 1
    
    def getTitlePageLines(self):
        lines = Book.getTitlePageLines(self)
        lines.append(('editor', '舒芜　前言'))
        lines.append(('editor', '李全华　标点'))
        return lines
        
   
class QHYY(Book):
    
    def __init__(self):
        Book.__init__(self)
        self.title = '前汉演义'
        self.authors = ['蔡东藩']
        self.dirName = 'D:\\pdfconv\\QHYY'
        self.excludedPages = [2, 55, 66, 67, 68, 536, 537, 548, 549, 550]
        
        #self.corruptedTextReplacement['ACA9'] = ''
        self.corruptedTextReplacement['F9E2'] = '緤'
        self.corruptedTextReplacement['FDB7'] = '叨'
        #self.corruptedTextReplacement['FCB3'] = ''
        self.corruptedTextReplacement['FBA5'] = '娙'
        #self.corruptedTextReplacement['F9C8'] = ''
        self.corruptedTextReplacement['FE80'] = '䜣'
        #self.corruptedTextReplacement['F9D3'] = ''
        self.corruptedTextReplacement['AAA4'] = '幵'
        self.corruptedTextReplacement['FABA'] = '狦'
        self.corruptedTextReplacement['FDD6'] = '毹'
        self.corruptedTextReplacement['BF'] = '麻'
        
    def getChapterLevel(self, page, line):
        if re.match(self.CHAPTER_TITLE_PATTERNS[0], line.getText()):
            return 2
        if page.pageNum >= 69 and line.lineNum == 1:
            secondLine = page.getLine(2)
            if re.match(self.CHAPTER_TITLE_PATTERNS[1], secondLine.getText()):
                k = 0
                while k < len(secondLine.chars):
                    if secondLine.chars[k].text == '　':
                        break
                    k += 1
                line.chars[-1].text += '　'
                line.chars[0:0] = secondLine.chars[: k + 1]
                line.chars.extend(secondLine.chars[k + 1 :])
                secondLine.chars = []
        return 1
    
    def getChapterTitle(self, page, line):
        title = line.getText()
        if title.find('回') == -1:
            title = title.replace('　', '')
        return title
    
    def getTitlePageLines(self):
        lines = Book.getTitlePageLines(self)
        lines.insert(0, ('series', '中国历代通俗演义'))
        return lines


class YSJH(Book):
    
    def __init__(self):
        Book.__init__(self)
        self.title = '雅舍菁华'
        self.authors = ['梁实秋']
        self.dirName = 'D:\\pdfconv\\YSJH'
        self.excludedPages = [2, 3, 4, 5, 6]
        self.HAS_PAGE_FOOT = True
        
        self.corruptedTextReplacement['EE'] = '頫'
        #self.corruptedTextReplacement['FDD7'] = ''
        
    def getChapterTitle(self, page, line):
        title = line.getText().replace('　', '')
        if line.chars[-1].isFootnoteAnchor():
            title = title[:-1]
        return title   
    
    def getTitlePageLines(self):
        lines = Book.getTitlePageLines(self)
        lines.append(('editor', '李宽全　选编'))
        return lines  

            
class JGRS(Book):
    
    def __init__(self):
        Book.__init__(self)
        self.title = '静观人生'
        self.authors = ['丰子恺']
        self.dirName = 'D:\\pdfconv\\JGRS'
        self.HAS_PAGE_FOOT = True
        self.excludedPages = [1, 2, 3, 4, 5, 6, 7]
        self.CHAPTER_TITLE_PATTERNS = []
        
        #self.corruptedTextReplacement['FDA1'] = ''
        self.corruptedTextReplacement['FDAE'] = '斫'
        
    def getChapterLevel(self, page, line):
        if page.pageNum in [8, 361] and line.lineNum == 1 or re.match(unicode(r'[一二三四五六七八九十百]+　'), line.getText()):
            return 1
        return 2
        
    def getChapterTitle(self, page, line):
        title = line.getText()
        if not re.match(unicode(r'[一二三四五六七八九十百]+　'), title):
            title = title.replace('　', '')
        if line.chars[-1].isFootnoteAnchor():
            title = title[:-1]      
        return title
    
    def getTitlePageLines(self):
        lines = Book.getTitlePageLines(self)
        lines.append(('editor', '熊一林　段高　选编'))
        return lines


class LDJ(Book):
    
    def __init__(self):
        Book.__init__(self)
        self.title = '鹿鼎记'
        self.authors = ['金庸']
        self.dirName = 'D:\\pdfconv\\LDJ'
        self.excludedPages = [1, 2, 8, 423, 424, 831, 832, 1256, 1257, 1688, 1689]
        self.markChapter(2113, 1, 1, '附录　康熙朝的机密奏折')
        self.markChapter(2123, 1, 1, '后记')

        self.corruptedTextReplacement['EE'] = '頫'
        self.corruptedTextReplacement['FDA3'] = '扫'
        self.corruptedTextReplacement['FDA6'] = '徬'
        self.corruptedTextReplacement['239E'] = '弥'
        self.corruptedTextReplacement['FCDC'] = '飏'
        self.corruptedTextReplacement['FDB1'] = '隙'
        #self.corruptedTextReplacement['F8D7'] = ''
        #self.corruptedTextReplacement['FDBB'] = ''
        #self.corruptedTextReplacement['FDA2'] = ''
        self.corruptedTextReplacement['FDA5'] = '钺'
        self.corruptedTextReplacement['FDB2'] = '佑'
        self.corruptedTextReplacement['FDAE'] = '趟'
        
    def replaceCorruptedText(self, page, ch):
        prevCh = page.chars[ch.index - 1] if ch.index > 0 else None
        if ch.corruptedText == 'F8D7':
            ch.text = '闤' if prevCh.text == '知' else '闠'
        elif ch.corruptedText == 'FDBB':
            ch.text = '塽' if prevCh.text == '克' else '跷'
        else:
            Book.replaceCorruptedText(self, page, ch)
            
    def getChapterLevel(self, page, line):
        if line.getText().find('回') != -1:
            secondLine = page.lines[line.getLineIndex() + 1]
            line.chars[-1].text += '　'
            line.chars.extend(secondLine.chars)
            secondLine.chars = []
        if 2113 <= page.pageNum < 2123:
            return 2
        return 1


class JHYY(Book):
    
    def __init__(self):
        Book.__init__(self)
        self.title = '京华烟云'
        self.authors = ['林语堂']
        self.translators = ['张振玉']
        self.dirName = 'D:\\pdfconv\\JHYY'
        self.excludedPages = [1, 2, 3, 6, 7, 8, 423, 424, 427, 428, 429]
        self.markChapter(11, 1, 1, '译者序')
        self.markChapter(13, 1, 1, '关于《京华烟云》')
        self.CHAPTER_TITLE_PATTERNS = [u'(上|中|下)卷', u'·第(一|二|三|四|五|六|七|八|九|十|百)+章·']
        self.corruptedTextReplacement['EE'] = '頫'
        
    def getTitlePageLines(self):
        lines = Book.getTitlePageLines(self)
        lines.append(('editor', '寇晓伟　编'))
        return lines
    
    def getChapterLevel(self, page, line):
        if line.getText().find('章') != -1:
            secondLine = page.lines[line.getLineIndex() + 1]
            thirdLine = page.lines[line.getLineIndex() + 2]
            line.chars[-1].text += '　'
            line.chars.extend(secondLine.chars)
            secondLine.chars = []
            line.chars[-1].text += '　'
            line.chars.extend(thirdLine.chars)
            thirdLine.chars = []
            return 2
        return 1

    def getChapterTitle(self, page, line):
        title = line.getText()
        if title.find('卷') != -1:
            title = title.replace('　　', '　')
        elif title.find('章') != -1:
            title = title.replace('·', '')
        else:
            title = title.replace('　', '')
        return title

    
class WC(Book):
    
    def __init__(self):
        Book.__init__(self)
        self.title = '围城'
        self.authors = ['钱锺书']
        self.dirName = 'D:\\pdfconv\\WC'
        self.HAS_PAGE_FOOT = True
        self.excludedPages = [1, 2, 3]
        
        self.corruptedTextReplacement['FDA8'] = '庵'
        self.corruptedTextReplacement['FDAC'] = '叆'
        self.corruptedTextReplacement['FDAB'] = '叇'
        self.corruptedTextReplacement['FDB0'] = '（口苏）'
        self.corruptedTextReplacement['FDB6'] = '騃'
        
        
class ZALWJ(Book):
    
    class CustomSectionMatcher(AlignedSectionMatcher):
    
        def getLeftAlign(self, beginLine, line):
            if line == beginLine:
                k = 0
                while k < len(line.chars) - 1:
                    if line.chars[k].text == '：':
                        return line.chars[k + 1].left
                    k += 1
                return line.getRight()
            return line.getLeft(True)
        
        def match(self, chapter, beginLineIndex):
            if 1831 <= chapter.lines[beginLineIndex].page.pageNum <= 1845:
                return AlignedSectionMatcher.match(self, chapter, beginLineIndex)
            return -1
    
    def __init__(self):
        Book.__init__(self)
        self.title = '张爱玲文集'
        self.authors = ['张爱玲']
        self.dirName = 'D:\\pdfconv\\ZALWJ'
        self.HAS_PAGE_FOOT = True
        self.FONT_SIZE_FOR_CHAPTER = 15
        self.excludedPages = [1, 2, 3, 353, 354, 355, 822, 823, 824, 1359, 1360, 1361, 1362, 1363]
        
        #self.corruptedTextReplacement['FCD1'] = ''
        self.corruptedTextReplacement['EF'] = '揾'
        self.corruptedTextReplacement['BE'] = '綷'
        
        self.markChapter(197, 1, 1, '殷宝滟送花楼会')
        self.markNoChapter(197, 2)
        self.markChapter(1790, 1, 1, "海上花的几个问题——英译本序")
        self.markNoChapter(1790, 2)
        
        self.sectionMatchers = [ZALWJ.CustomSectionMatcher(), IndentedSectionMatcher(2), IndentedSectionMatcher(0)]
        
    def getTitlePageLines(self):
        lines = []
        lines.append(('title', self.title))
        lines.append(('editor', '顾问 　柯灵'))
        lines.append(('editor', '编者　金宏达　于青'))
        return lines
    
    def getChapterLevel(self, page, line):
        if re.match(unicode('[12345]'), line.getText()):
            return 3
        if page.pageNum == 1368 and line.lineNum != 1 \
            or 1369 <= page.pageNum <= 1370 \
            or 1464 <= page.pageNum <= 1471 \
            or 1496 <= page.pageNum <= 1513 \
            or page.pageNum == 1605 and line.lineNum != 1 \
            or 1606 <= page.pageNum <= 1609:
            return 2
        if page.pageNum >= 1830:
            if page.pageNum in [1830, 1846, 1866, 1878, 1921] and line.lineNum == 1:
                return 1
            return 2
        if re.match(self.CHAPTER_TITLE_PATTERNS[0], line.getText()):
            return 2
        return 1
    
    def getChapterTitle(self, page, line):
        title = line.getText()
        if re.match(unicode(r'[一二三四五六七八九十]　[^八]'), title) or re.match(unicode(r'第[一二三四五六七八九十]章'), title) or title.find('沉香屑') != -1 or title.find('桂花蒸') != -1:
            pass
        else:
            title = title.replace('　', '')
        if line.chars[-1].isFootnoteAnchor():
            title = title[:-1]
        return title
    
    
class LZZY(Book):
    
    def __init__(self):
        Book.__init__(self)
        self.title = '聊斋志异'
        self.authors = ['蒲松龄']
        self.dirName = 'D:\\pdfconv\\LZZY'
        self.excludedPages = [1, 2, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27]
        self.CENTER_ALIGN_DIFF_FOR_CHAPTER = 50
        
        self.markNoChapter(14, 1)
        
        self.corruptedTextReplacement['F8A6'] = '闬'
        self.corruptedTextReplacement['ADE5'] = '䃜'
        self.corruptedTextReplacement['F8CF'] = '（黑曷）'
        self.corruptedTextReplacement['AAB3'] = '㑌'
        self.corruptedTextReplacement['F8D0'] = '㔍'
        self.corruptedTextReplacement['F8C5'] = '騭'
        self.corruptedTextReplacement['F8D1'] = '躧'
        self.corruptedTextReplacement['F8D2'] = '（田鹿）'
        self.corruptedTextReplacement['F8BB'] = '懎'
        self.corruptedTextReplacement['F8D3'] = '（亻蜀）'
        self.corruptedTextReplacement['F8D4'] = '（月函）'
        #self.corruptedTextReplacement['F8D5'] = ''
        self.corruptedTextReplacement['BD'] = '絓'
        self.corruptedTextReplacement['AAFC'] = '哳'
        self.corruptedTextReplacement['AEAD'] = '濇'
        self.corruptedTextReplacement['F8D6'] = '胹'
        self.corruptedTextReplacement['F8D7'] = '鱄'
        self.corruptedTextReplacement['ADEC'] = '䍠'
        self.corruptedTextReplacement['AAB0'] = '（亻达）'
        self.corruptedTextReplacement['84'] = '刓'
        self.corruptedTextReplacement['ADD9'] = '幢'
        self.corruptedTextReplacement['F8A1'] = '（厂贝贝）'
        self.corruptedTextReplacement['F8A2'] = '（厂贝贝贝）'
        self.corruptedTextReplacement['AEFA'] = '（厂贝贝贝贝）'
        self.corruptedTextReplacement['AEA7'] = '逦'
        
    def getTitlePageLines(self):
        lines = Book.getTitlePageLines(self)
        lines.append(('editor', '蓝翎　前言'))
        lines.append(('editor', '张式铭　标点'))
        return lines
    
    def getChapterLevel(self, page, line):
        if page.pageNum == 3 and line.lineNum == 1 or page.pageNum == 15:
            return 1
        if line.chars[0].text == '卷':
            return 1
        return 2
        
    def getChapterTitle(self, page, line):
        title = line.getText()
        return title.replace('　', '')
    
    
class SSBYQJ(Book):
    
    class CustomSectionMatcher(AlignedSectionMatcher):
        
        def __init__(self):
            AlignedSectionMatcher.__init__(self)
            self.cssClass = 'no-indent'
    
        def getLeftAlign(self, beginLine, line):
            if line == beginLine:
                return 101
            else:
                return line.getLeft(True)
        
        def match(self, chapter, beginLineIndex):
            beginLine = chapter.lines[beginLineIndex]
            if abs(beginLine.getLeft() - 77) <= 3 and beginLine.getMaxFontSize() == 12 and beginLine.getText().strip('　').find('　') != -1:
                return AlignedSectionMatcher.match(self, chapter, beginLineIndex)
            return -1
    
    def __init__(self):
        Book.__init__(self)
        self.title = '莎士比亚全集'
        self.authors = ['莎士比亚']
        self.translators = ['朱生豪等']
        self.dirName = 'D:\\pdfconv\\SSBYQJ'
        self.PAGE_HEAD_LINE_INDEX = -1
        self.HAS_PAGE_FOOT = True
        self.excludedPages = [1, 2, 3, 19, 20, 21, 22, 746, 747, 748, 1427, 1428, 1429, 2185, 2186, 2187, 2876, 2877, 2878, 3536, 3537, 3538]
        
        self.sectionMatchers = [SSBYQJ.CustomSectionMatcher(), IndentedSectionMatcher(2)]
        self.sectionMatchers[0].ALLOW_DIFFERENT_MAX_FONT_SIZE = False
        self.sectionMatchers[0].RE_ADJUST_INDENTATION = False
        self.sectionMatchers[1].ALLOW_DIFFERENT_MAX_FONT_SIZE = False
        self.sectionMatchers[1].RE_ADJUST_INDENTATION = False
        self.COMMON_SECTION_FIRST_LINE_LEFT = [101]
        
        self.markChapter(3891, 1, 2, '')
        self.markNoChapter(3891, 2)
        self.markNoChapter(3891, 3)
        self.markChapter(3892, 1, 2, '')
        self.markNoChapter(3892, 2)
        self.markChapter(3949, 1, 2, '')
        self.markNoChapter(3949, 2)
        self.markNoChapter(3949, 3)
        self.markChapter(3950, 1, 2, '')
        self.markChapter(3952, 1, 2, '')
        self.markChapter(4199, 1, 1, '情女怨　爱情的礼赞　乐曲杂咏　凤凰和斑鸠')
        self.markNoChapter(4199, 2)
        self.markChapter(4200, 1, 1, '情女怨')
        self.markChapter(4216, 1, 1, '爱情的礼赞')
        self.markChapter(4228, 1, 1, '乐曲杂咏')
        self.markChapter(4239, 1, 1, '凤凰和斑鸠')
        
        self.corruptedTextReplacement['ED'] = '缰'
        
    def markHeadFoot(self, page):
        if page.pageNum in [2317, 2340, 2364, 3062, 3950, 4216]:
            self.PAGE_FOOT_LINE_INDEX = 0
        else:
            self.PAGE_FOOT_LINE_INDEX = 1
        Book.markHeadFoot(self, page)
            
    def getChapterLevel(self, page, line):
        if re.match(self.CHAPTER_TITLE_PATTERNS[0], line.getText()) or line.getText().find('幕') != -1:
            return 2
        return 1
        
    def getChapterTitle(self, page, line):
        title = line.getText()
        return title.replace('　', '').replace('○', '〇')
    
    def adjustSections(self):
        for chapter in self.chapters:
            for section in chapter.sections:
                if section.lines != []:
                    line = section.lines[0]
                    if line.page.pageNum == 3869 and line.lineNum == 15:
                        snippet = TextFormatSnippet()
                        snippet.text = '拉西马卡斯　我没有想到你竟有这样动人的口才；这真是出我意料之外，即使我抱着一颗邪心到这儿来，听见你这一番谈话，也会使我幡然悔改。这些金子是给你的，你拿着吧。愿你继续走你的清白的路；愿神明加强你的力量！'
                        section.snippets = [snippet]

                        
class ZXSQJ(Book):
    
    def __init__(self):
        Book.__init__(self)
        self.title = '掌小说全集'
        self.authors = ['川端康成']
        self.translators = ['叶渭渠']
        self.dirName = 'D:\\pdfconv\\ZXSQJ'
        self.excludedPages = [1, 2, 3, 10, 11, 12, 13, 14, 15, 16]
        self.FONT_SIZE_FOR_CHAPTER = 15
        self.CHAPTER_TITLE_PATTERNS = []
        self.HAS_PAGE_FOOT = True
        self.markChapter(4, 1, 1, '致中国读者')
        self.markChapter(5, 1, 1, '主编者的话')
        
    def markHeadFoot(self, page):
        if page.pageNum in [4]:
            self.PAGE_HEAD_LINE_INDEX = 1
            self.HAS_PAGE_FOOT = False
        elif page.pageNum in [293]:
            self.PAGE_HEAD_LINE_INDEX = 2
            self.HAS_PAGE_FOOT = False
        else:
            self.PAGE_HEAD_LINE_INDEX = 0
            self.HAS_PAGE_FOOT = True
        Book.markHeadFoot(self, page)
    
    def getChapterTitle(self, page, line):
        title = line.getText()
        if line.chars[-1].isFootnoteAnchor():
            title = title[:-1]
        return title.replace('　', '')
    
    def getChapterLevel(self, page, line):
        if page.pageNum == 4:
            return -1
        return Book.getChapterLevel(self, page, line)
    
    def adjustSections(self):
        for chapter in self.chapters:
            for section in chapter.sections:
                if section.lines != []:
                    line = section.lines[0]
                    if line.page.pageNum == 4 and line.lineNum == 15:
                        snippet = TextFormatSnippet()
                        snippet.text = '但愿中国读者通过这次翻译出版的《川端康成文集》，可以了解到川端文学创作的多样性，以及其文学的趣味性。他向西方学习，但决不单纯模仿西方，而是创造出东方的文学来。但愿读者能体味到川端康成文学的真正价值。　　川端香男里方'
                        section.snippets = [snippet]


def main():
    book = ZXSQJ()
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
