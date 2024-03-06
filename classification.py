import os
from bs4 import BeautifulSoup
import re
from tqdm import tqdm
from datetime import datetime
import pytz
# import htmlmarker # 去水印


class TableProcessor:
    def __init__(self):
    
        self.ansfunc_data = []
        self.blankfunc_2_data = []
        self.blank_anscard_data = []

        self.counters = {'total': 0, 'answer': 0,
                         'blank': 0, 'normal': 0, 'long': 0}

        self.regex_long_table = r'合作探究|课时|主备人|课题|授课人|新授课|我的疑问|三维目标|教学目标|教学方法|教具准备|授课时间|课后总结|板书设计|当堂检测|教学过程|教学反思|教师活动设计|学生活动设计|教学难点|教学重点|教师活动|学生活动|教学意图|内容与方法|教师复备栏'

        # 全角数字 [\uFF10-\uFF19]+
        # Roman Numerals [\u2160-\u216F]+
        self.regex_is_blank = r'展示分工'

        self.regex_blank = r"阅读积累与运用|快乐的课间|基础积累与运用|我的积累卡|读写部分|轻松写作|评价同学|由教师具体指明|问题展示|展示同学|展示方式|评价同学|教师评价|读书资料卡|赋分范围|基础乐园|作文题目|课外拓展|积累运用|听力测试|笔下生辉|品德与社会|综合性学习|错别字改正|试卷成绩|口语成绩|平时成绩|单项填空|完形填空|阅读理解|卷面清洁|积累运用|短文填空|句型转换|汉译英|书面表达|卷面书写与整洁|在相应的等级上打“√”|正确选项|基础知识|阅卷老师|综合运用|快乐阅读|习作表达|分析说明题|考号末两位|完成作业|参加活动|学习行为|学习态度|细心答题|我的题词|摘录内容|卷面书写|第\d{1,3}周|共\d{1,3}分|解题方法归纳总结|错题原因分析|阅卷签名|评价等级|选项字母|判断理由|能力测试|检测等级|口语交际|水平测试|[A-Z]组|综合分析题|考场座位号|填空|计算|实验|探究|选择|密封线内不答|综合探究|文综会考|单项选择|家长签字|填字注音|基础得分|错字订正|学生姓名|学生签字|分析说明|出题教师|卷面分|学科王|评卷人|批卷人|复核人|每小题|结分人|提高题|发展题|计分人|同学们|评分人|未分类|应得分|实得分|附加题|复评人|核分人|累分人|合分人|作图题|错别字|正确字|单选题|简答题|总分人|座次号|复查人|阅卷人|选择题|问答题|座位号|写作分|正确率%|待达标|☆数|总☆|第组|组次|考号|简答|总评|多选|听力|笔试|辨析|第.部分|共\d+分|化学|物理|生物|等第|合计|小计|智慧|加分|评语|小组|修改|班级|书法|成绩|全卷|试题|得分|评卷|写字|项目|等级|选项|座号|序号|地理|正误|题次|学校|姓名|连线|选择|测试|评价|过程|积累|英语|内容|最佳|材料|书写|单选|学号|部分|日期|总分|分值|题号|题目|识记|附加|类卷|满分|大题|读写|表达|答案|赋分|分数|朗读|扣分|综合|计分|专题|字母|达标|卷面|试室|阅卷|习作|周次|小记|写话|评分|卷首|工整|阅读|批注|书面|口头|口述|语基|A卷|B卷|Ⅰ|Ⅱ|Ⅲ|I|II|III|—|、|:|～|Â|（|）|\(|\)|\.|\．|\*|,|，|#|[+-]|﹣|－|﹢|▲|▲|l|科|扣|卷|面|图|分|次|号|序|听|做|读|写|项|非|目|题|栏|初|核|人|复|-|第|学|非|或|[一二三四五六七八九十]|\d{1,4}字|[0-9]\d*|~|～|：|[\u2460-\u2473]|[\uFF10-\uFF19]+|园|新|课|标|第|一|网|来|源|学|科|格|总|节|\]|\[|\||※|答|与|填|实|小|优|良|/|I|II|III|IV|V|VI|VII|VIII|IX|X|XI|XII|XIII|XIV|XV|XVI|XVII|XVIII|XIX|XX|[\u2160-\u216F]+|☆|jiang;"

        self.regex_answer = r'正确答案|正确选项|文综会考|答案字母|[\u2191\u2193]|、|△|大题|阅卷人|评卷人|得分|题次|选项|序号|题号|题目|选择题|答案|分数|成绩|—|Ⅰ|Ⅱ|\]|\[|[一二三四五六七八九十]|新|课|标|第|一|网|来|源|学|科|\||答|题|小'
        
        self.regex_notanswer = r'￥|□|∠|Example|[\u2460-\u2473]|[><=＜＞＝]|[+-]|\（|\）|\(|\)|→|：|；|﹣|﹢|&sub\d+END&|&super\d+END&|Ω|\/'
        

    # 空白表格 一筛
    # 通过一些关键字，style，html tag和regex去筛选空白表格
    def is_blank_table(self, table):
        parsed_table = str(table)
        # create a copy, we want to return the full table.
        soup_copy = BeautifulSoup(parsed_table, 'lxml')

        text = ''.join(table.stripped_strings)

        text = re.sub(' ', '', text)

        counts = {char: text.count(f'[{char}]') for char in 'ABCTF'}
        if len(set(counts.values())) == 1 and next(iter(counts.values())) >= 3:
            self.blank_anscard_data.append(text)
            return True
        # 1[A][B][C][D]6[A][B][C][D]，这边处理一些答题卡类的

        if re.search(self.regex_is_blank, text):
            return True

        if re.fullmatch(r'(<[^<>]*?>|\s)+', parsed_table):
            return True
        if "007.png" in parsed_table or "TABLE_PROTECT" in parsed_table:  # 极端情况 ** Protected table不管
            return False
        
        #  感觉用不着了
        # if len(soup_copy.find_all('tr')) >= 7 or len(soup_copy.find_all('p')) > 100:
        #    print(1) # 过长的Table或者是p tag过多的table，不是空白表格
        #    return False

        for p_tag in soup_copy.find_all('p'):  # 另一种极端情况，p段背景颜色为蓝色
            if "background-color:#000080" in str(p_tag.get('style', '')):
                return False

        for span_tag in soup_copy.find_all('span'):
            if "color:#ffffff" in str(span_tag.get('style', '')) and not ("background-color:#ffffff" in str(span_tag.get('style', '')) or "background-color:#000080" in str(span_tag.get('style', ''))):  # 再考虑一下其他颜色的情况
                span_tag.decompose()

        for img_tag in soup_copy.find_all("img"):
            if 'height="3"' in str(img_tag) or 'width="2"' in str(img_tag):
                img_tag.decompose()

        cleaned_html = str(soup_copy)
        img_count = cleaned_html.count("<img")
        text_clean = "".join(
            re.split(r"<[^>]+>", cleaned_html)).replace(" ", "").strip()

        # *important, remove &nbsp entity
        text_clean = re.sub(r"(\s|&nbsp;|&#160;|&#xa0;)+",
                            "", text_clean).strip()

        # trace back to innit/
        text_clean = re.sub(self.regex_blank, "", text_clean).strip()

        if re.fullmatch(r'kBcOm|X Kb1 .C om', text_clean):
            return True

        if text_clean == "" or re.search(r"考生须知|条形码粘贴处|准考证|密封线内不要", text_clean):
            if img_count <= 2:
                return True

        if bool(re.fullmatch(r'[wW]{0,3}', text_clean)):
            return True  # 如果只剩下一个w，或者2个w，基本上是水印，可以认定为空白表
            # 这边以后优化好了水印module可以不用 MARK一下**
        if bool(re.fullmatch(r'&ampsuperEND&amp|&ampsubEND&amp|&sub\d+END&|&super\d+END&', text_clean)):
            return True  # 语文表格，作文

        return False

    # 从html中提取表格
    def extract_tables(self, input_html, output_html, filename):
        with open(input_html, 'r', encoding='utf-8') as file:
            soup = BeautifulSoup(file, 'html.parser')

        tables = soup.find_all('table')

        # {os.path.basename(input_html)}
        for table in tqdm(tables, desc=f"Processing Tables: {filename}"):

            # 跳过嵌套和图片表格，直接操作
            if table.find('img') or table.find('table'):
                continue  # Skip tables with images or nested tables for now

            self.counters['total'] += 1

            self.classify_and_save(table, output_html, filename)

    # 空白表格二筛
    # 通过计算空白表格的数量占多少百分比，用于筛选 答案表格 之后进行二筛
    # 这个函数其实在完善了空白表格 is_blank_table 之后可能*没有必要
    # 通过查看output_debug文件，可以看到筛选出来的空白表格的文本
    def is_blank_table_2(self, table):

        total_cells = 0
        blank_cells = 0
        text = ''.join(table.stripped_strings)  # remove blank strs
        text = re.sub(r"(\s|&nbsp;|&#160;|&#xa0;)+", "",
                      text).strip()  # remove blank entity & nbsp

        for cell in table.find_all(['td', 'th']):
            total_cells += 1
            cell_text = cell.get_text(strip=True)
            if not cell_text or cell_text.isspace() and 'width' in cell.get('style', ''):
                blank_cells += 1

        if total_cells > 0:
            blank_percentage = (blank_cells / total_cells) * 100
            # *阈值 threshold needed to be changed based on the problem.
            if blank_percentage >= 40:
                self.blankfunc_2_data.append(text)
                return True

        return False

    # 答案表格筛选
    def is_answer_table(self, table):

        # [\u4e00-\u9fff] represents Chinese characters

        text = ''.join(table.stripped_strings)
        text = re.sub(r"(\s|&nbsp;|&#160;|&#xa0;)+", "", text).strip()

        # if bool(re.search('√', text)) and not re.findall('[\u4e00-\u9fff]', text) : # 特殊极端情况，带√的
        #   return True

        # Ans_type1 = re.search('答案', text) is not None and re.search('题号', text) is not None
        # if Ans_type1: # 第一种情况，只带答案和题号，并且没有其他中文字符
        #    text_without_keywords = text.replace('答案', '').replace('题号', '')
        #    other_chinese_chars = re.findall('[\u4e00-\u9fff]', text_without_keywords)
        #    if not other_chinese_chars:
        #        return True

        text_clean = re.sub(self.regex_answer, "", text).strip()
        text_clean = re.sub(
            r'[\[\]]', '', text_clean).strip()  # removes all []
        # text_clean = re.sub(r'[\uFF01-\uFF5E]','',text_clean).strip() # removes all full-width English character.
        # 这个先不用，它会把 '.' 删掉

        # General Check, 做了一个大致的筛选，筛选到一个新的file里，再手动看，细化

        if bool(re.search('[\u4e00-\u9fff]', text_clean)):
            return False

        if bool(re.search(self.regex_notanswer, text_clean)):
            return False
        # new filteration, count nonABCD letters.
        text_upper = text.upper()

        count_nonABCD = sum(1 for char in text_upper if bool(
            re.match(r'[A-Z]', char) and char not in "ABCD"))
        if count_nonABCD >= 6:  # threshold 阈值

            return False

        text_clean = re.sub(r'[.]', '．', text_clean)

        if '．' in text_clean:  # 注意全角的 dot
            # 数字. A ，为选项table
            if re.match(r'[A-D]\．\d', text_clean) or re.match(r'[A-D]\.\d', text_clean):
                return False  # A．1 B．2 C．3 D．4
            elif re.match(r'[A-D]\．[A-Z]', text_clean) or re.match(r'[A-D]\．[A-D]', text_clean):  # 字母. 字母 选项
                return False  # A．B．C．D．
            elif re.search(r'[A-D]', text_clean) is None:
                return False  # 没有ABCD选项
            elif re.match(r'[A-Z]．[a-zA-Z0-9]+', text_clean):
                return False  # A．xy11B．xy12C．xy14D．xy21
            elif re.search(r'[Mg|Li|IaIbI]', text_clean):  # 有些特殊的表格
                return False
            else:
                self.ansfunc_data.append(text_clean)
                return True

        elif bool(re.search(r"^(?=.*[a-dA-D]{4,})(?=.*\d{4,}).+$", text_clean)):
            return True

        return False

    # 长表格筛选
    def is_long_table(self, table):
        # ------------------------------------------------------------------------------#
        # 这边是之前的checker
        # text = ''.join(table.stripped_strings)
        # cleaned_text = re.sub(r'(HXBLANK)+', '', text)
        '''
        tr_ = table.find_all('tr')
        if len(tr_) >= 10:
            return False

        if len(cleaned_text) >= 3000:
            return True
        '''
        # ------------------------------------------------------------------------------#

        # 长表格的判断条件， 长表格使用的是一些特殊的关键词，比如教学过程，教学目标等
        # process是采用run through all机制，可以在把优先级最高的check logic放在最后面
        rows = table.find_all('tr')
        flag_split = False
        total_text_length = 0

        for idx, row in enumerate(rows):
            cells = row.find_all(['th', 'td'])
            num_p_in_cells = [len(cell.find_all('p')) for cell in cells]
            # quest_num，inheritted from the previous build.
            if any(num_p >= 10 or (num_p >= 5 and "quest_num" in str(cell)) for num_p, cell in zip(num_p_in_cells, cells)):
                flag_split = True
            if len(cells) == 1 and cells[0].get_text(strip=True) and idx != 0:
                flag_split = True

            total_text_length += sum(len(cell.get_text(strip=True))
                                     for cell in cells)

        # 其他可能的长表格判断条件，比如行数和总文本长度
        if len(rows) > 10 or total_text_length > 2500:
            flag_split = True

        # 检查是否包含教学相关的关键词，目前为优先级最高的checker
        teaching_keywords = re.compile(self.regex_long_table)
        if teaching_keywords.search(table.get_text()):
            flag_split = True

        return flag_split

    # 跑流程 call functions
    # 优先级 空白表格 > 答案表格 > 长表格

    def classify_and_save(self, table, output, filename):

        # 空白表格
        if self.is_blank_table(table):
            self.save_table(table, f'{output}empty_{filename}', 'blank')
        # 答案表格
        elif self.is_answer_table(table):
            # if self.is_blank_table_2(table):
            #    self.save_table(table, f'{output}empty_{filename}', 'blank')
            # else:
            self.save_table(table, f'{output}answer_{filename}', 'answer')
        # 长表格
        elif self.is_long_table(table):
            self.save_table(table, f'{output}long_{filename}', 'long')
        # 正常表格
        else:
            self.save_table(table, f'{output}normal_{filename}', 'normal')

    # 保存表格
    def save_table(self, table, output_path, table_type):
        with open(output_path, 'a', encoding='utf-8') as f:
            f.write(f"<p>\n</p>\n{str(table)}\n")
        self.counters[table_type] += 1

    # 输出统计文件
    def output_statistics(self, output_folder, filename):
        stats_path = os.path.join(
            output_folder, f'table_statistics{filename}.html')
        with open(stats_path, 'w', encoding='utf-8') as file:
            file.write(
                "<html><head><title>Table Processing Statistics</title></head><body>")
            file.write("<h1>Table Processing Statistics</h1>")
            file.write(f"<p>Total tables processed: {
                       self.counters['total']}</p>")
            for table_type, count in self.counters.items():
                if table_type != 'total':
                    file.write(
                        f"<p>{table_type.capitalize()} tables: {count}</p>")
            # 输出统计最后加上时间
            time_now = datetime.now(pytz.timezone(
                'Asia/Shanghai')).strftime('%Y-%m-%d %H:%M:%S')
            file.write(f"<p>Ending time: {time_now}, Filename: {filename}</p>")
            file.write("</body></html>")

    # 输出debug文件，之后可以再完善一下，也包括Table元素和Function中的一些文本。
    def output_debug(self, output_folder, filename):
        debug_path = os.path.join(output_folder, f'debugdata{filename}.txt')
        with open(debug_path, 'w', encoding='utf-8') as file:
            file.write(f'Filename: {filename}\n')
            file.write(f'Data: ansfunc_data\n')
            for line in self.ansfunc_data:
                file.write(f"{line}\n")
            file.write(f'Data: blankfunc_2_data\n')
            for line in self.blankfunc_2_data:
                file.write(f"{line}\n")
            file.write(f'Data: blank_anscard_data\n')
            for line in self.blank_anscard_data:
                file.write(f"{line}\n")


    '''

    # Processor Function，用来遍历folder中的html文件并且pass html文件给extract table function
    # 这个可以删掉，没用，测试使用processor
    def process(self):
        for filename in tqdm(os.listdir(self.input_folder), desc="Processing HTML Files"):
            if filename.endswith('.html'):
                input_html = os.path.join(self.input_folder, filename)
                self.extract_tables(input_html)
                self.output_statistics(filename)
               # break # 先遍历一个文件，记得删掉


# debugg run
if __name__ == '__main__':

    # Input the folder path here.
    input_folder = 'exam type table'
    output_folder = 'output'

    # 去一遍水印
    # marker = htmlmarker.HTMLProcessor(input_folder= input_folder, output_folder= output_folder)
    # marker.process_files()

    # 再分类表格
    processor = TableProcessor(input_folder, output_folder)
    processor.process()

    '''