import os
from bs4 import BeautifulSoup, NavigableString
import re
from tqdm import tqdm
from datetime import datetime
import pytz
"""
Class: TableModule

函数list:
                                            表格分类
================================================================================================
- is_blank_table(self, table: BeautifulSoup object)
    判断表格是否为空白。
    输出: bool (如果表格为空白则为True，否则为False)

- is_blank_table_2(self, table: BeautifulSoup object)
    另一种判断表格是否为空白的方法，**会有误伤**
    输出: bool (如果表格为空白则为True，否则为False)

- is_answer_table(self, table: BeautifulSoup object)
    判断表格是否是答案表格
    输出: bool (如果表格包含答案则为True，否则为False)

- is_long_table(self, table: BeautifulSoup object)
    判断表格是否为长表格。
    输出: bool (如果表格为长表格则为True，否则为False)

- classify_table(self, table: BeautifulSoup object)
    根据预定义的标准对表格进行分类，并更新计数器。
    输出: None
                                            表格拆分
================================================================================================
- clean_text(text: str, regex_pattern: Pattern)
    使用指定的正则表达式模式清洗提供的文本。
    输出: str (清洗后的文本)
    注意: 静态方法

- extract_tables(self)
    从加载的HTML文档中提取所有表格。
    输出: BeautifulSoup对象的列表 (表格)

- split_answer_table(self, table: BeautifulSoup object)
    将答案表格拆分，目前有两种拆分形式
    输出: str (格式化的答案字符串)

- insert_answers_into_document(self, filename: str)
    将处理后的答案插入到文档中。
    输出: None

- split_long_tables(self)
    拆分长表格，有两种拆分形式
                                            文件处理
================================================================================================
- output_statistics(self, output_folder: str, filename: str)
    将处理统计信息输出到HTML文件中。
    输出: None

- output_debug(self, output_folder: str, filename: str)
    将调试信息输出到文本文件中。
    输出: None

- load_html(self, input_html: str)
    从文件中加载HTML内容到BeautifulSoup对象中。
    输出: None

"""


class TableModule:
    def __init__(self):
        self.reset()

    def reset(self):
        self.ansfunc_data = []  # 用于存储未分类的数据
        self.blankfunc_2_data = []  # 用于存储空白表格的数据
        self.blank_anscard_data = []  # 用于存储答题卡的数据

        self.soup = None
        self.processed_ans_tables = []

        self.counters = {'total': 0, 'answer': 0,
                         'blank': 0, 'normal': 0, 'long': 0}  # 用于统计表格数量

        self.regex_patterns = self._compile_regex_patterns()  # 编译正则表达式

        self.soups = {
            'blank': BeautifulSoup('<div></div>', 'lxml'),
            'answer': BeautifulSoup('<div></div>', 'lxml'),
            'long': BeautifulSoup('<div></div>', 'lxml'),
            'normal': BeautifulSoup('<div></div>', 'lxml'),
        }  # 用于存储不同类型的表格

    def _compile_regex_patterns(self):
        patterns = {
            'long_table': re.compile(r'合作探究|课时|主备人|课题|授课人|新授课|我的疑问|三维目标|教学目标|教学方法|教具准备|授课时间|课后总结|板书设计|当堂检测|教学过程|教学反思|教师活动设计|学生活动设计|教学难点|教学重点|教师活动|学生活动|教学意图|内容与方法|教师复备栏'),

            'is_blank': re.compile(r'教学工作计划与总结|展示分工'),

            'split_answer': re.compile(r'[\u4e00-\u9fff]|:##Z#X#X#K.|[\u2191\u2193]|△|、|大题|阅卷人|评卷人|得分|题次|选项|序号|题号|题目|选择题|答案|分数|成绩|—|Ⅰ|Ⅱ|\]|\[|[一二三四五六七八九十]|新|课|标|第|一|网|来|源|学|科|\||答|题|小|'),

            'answer': re.compile(r'正确答案|正确选项|文综会考|答案字母|[\u2191\u2193]|△|大题|阅卷人|评卷人|得分|题次|选项|序号|题号|题目|选择题|答案|分数|成绩|—|Ⅰ|Ⅱ|\]|\[|[一二三四五六七八九十]|新|课|标|第|一|网|来|源|学|科|\||答|题|小'),

            'notanswer': re.compile(r'π|￥|□|∠|Example|[\u2460-\u2473]|[><=＜＞＝]|[+-]|\（|\）|\(|\)|→|：|；|﹣|﹢|&sub\d+END&|&super\d+END&|Ω|\/'),

            'blank': re.compile(r"jiang|XkB1．cOm|XkB1．com|阅读积累与运用|快乐的课间|基础积累与运用|我的积累卡|读写部分|轻松写作|评价同学|由教师具体指明|问题展示|展示同学|展示方式|评价同学|教师评价|读书资料卡|赋分范围|基础乐园|作文题目|课外拓展|积累运用|听力测试|笔下生辉|品德与社会|综合性学习|错别字改正|试卷成绩|口语成绩|平时成绩|单项填空|完形填空|阅读理解|卷面清洁|积累运用|短文填空|句型转换|汉译英|书面表达|卷面书写与整洁|在相应的等级上打“√”|正确选项|基础知识|阅卷老师|综合运用|快乐阅读|习作表达|分析说明题|考号末两位|完成作业|参加活动|学习行为|学习态度|细心答题|我的题词|摘录内容|卷面书写|第\d{1,3}周|共\d{1,3}分|解题方法归纳总结|错题原因分析|阅卷签名|评价等级|选项字母|判断理由|能力测试|检测等级|口语交际|水平测试|[A-Z]组|综合分析题|考场座位号|填空|计算|实验|探究|选择|密封线内不答|综合探究|文综会考|单项选择|家长签字|填字注音|基础得分|错字订正|学生姓名|学生签字|分析说明|出题教师|卷面分|学科王|评卷人|批卷人|复核人|每小题|结分人|提高题|发展题|计分人|同学们|评分人|未分类|应得分|实得分|附加题|复评人|核分人|累分人|合分人|作图题|错别字|正确字|单选题|简答题|总分人|座次号|复查人|阅卷人|选择题|问答题|座位号|写作分|正确率%|待达标|☆数|总☆|第组|组次|考号|简答|总评|多选|听力|笔试|辨析|第.部分|共\d+分|化学|物理|生物|等第|合计|小计|智慧|加分|评语|小组|修改|班级|书法|成绩|全卷|试题|得分|评卷|写字|项目|等级|选项|座号|序号|地理|正误|题次|学校|姓名|连线|选择|测试|评价|过程|积累|英语|内容|最佳|材料|书写|单选|学号|部分|日期|总分|分值|题号|题目|识记|附加|类卷|满分|大题|读写|表达|答案|赋分|分数|朗读|扣分|综合|计分|专题|字母|达标|卷面|试室|阅卷|习作|周次|小记|写话|评分|卷首|工整|阅读|批注|书面|口头|口述|语基|A卷|B卷|Ⅰ|Ⅱ|Ⅲ|I|II|III|—|、|:|～|Â|（|）|\(|\)|\.|\．|\*|,|，|#|[+-]|﹣|－|﹢|▲|▲|l|科|扣|卷|面|图|分|次|号|序|听|做|读|写|项|非|目|题|栏|初|核|人|复|-|第|学|非|或|[一二三四五六七八九十]|\d{1,4}字|[0-9]\d*|~|～|：|[\u2460-\u2473]|[\uFF10-\uFF19]+|园|新|课|标|第|一|网|来|源|学|科|格|总|节|\]|\[|\||※|答|与|填|实|小|优|良|/|I|II|III|IV|V|VI|VII|VIII|IX|X|XI|XII|XIII|XIV|XV|XVI|XVII|XVIII|XIX|XX|[\u2160-\u216F]+|☆")
        }
        return patterns

    def is_blank_table(self, table):
        str_table = str(table)
        soup_copy = BeautifulSoup(str_table, 'lxml')
        text = ''.join(table.stripped_strings)
        text = re.sub(' ', '', text)

        counts = {char: text.count(f'[{char}]') for char in 'ABC'}
        if len(set(counts.values())) == 1 and next(iter(counts.values())) >= 3:
            self.blank_anscard_data.append(text)
            return True  # 答题卡

        if bool(self.regex_patterns['is_blank'].search(text)):
            return True

        if re.fullmatch(r'(<[^<>]*?>|\s)+', str_table):
            return True  # 空白表格，Full Match空白文字
        if "007.png" in str_table or "TABLE_PROTECT" in str_table:
            return False  # 保护表格
        for p_tag in soup_copy.find_all('p'):
            if "background-color:#000080" in str(p_tag.get('style', '')):
                return False  # 保护表格2
        for span_tag in soup_copy.find_all('span'):
            if "color:#ffffff" in str(span_tag.get('style', '')) and not ("background-color:#ffffff" in str(span_tag.get('style', '')) or "background-color:#000080" in str(span_tag.get('style', ''))):
                span_tag.decompose()  # 拆解span标签
        for img_tag in soup_copy.find_all("img"):
            if 'height="3"' in str(img_tag) or 'width="2"' in str(img_tag):
                img_tag.decompose()  # 拆解img标签

        cleaned_html = str(soup_copy)
        img_count = cleaned_html.count("<img")  # 计算img标签数量
        text_clean = "".join(
            # 清洗html标签
            re.split(r"<[^>]+>", cleaned_html)).replace(" ", "").strip()
        text_clean = re.sub(r"(\s|&nbsp;|&#160;|&#xa0;)+",
                            "", text_clean).strip()  # 清洗文本，去除空格entity html
        text_clean = self.regex_patterns['blank'].sub("", text_clean)  # 清洗文本

        if text_clean == "" or re.search(r"考生须知|条形码粘贴处|准考证|密封线内不", text_clean):
            if img_count <= 2:
                return True  # 空白表格，无文本
        if bool(re.fullmatch(r'[wW]{0,3}', text_clean)):
            return True  # 用于应对一些顽固水印
        if bool(re.fullmatch(r'&ampsuperEND&amp|&ampsubEND&amp|&sub\d+END&|&super\d+END&', text_clean)):
            return True  # 空白表格，Full Match一些特殊情况
        return False

    def is_blank_table_2(self, table):
        total_cells = 0
        blank_cells = 0
        text = ''.join(table.stripped_strings)  # 获取表格文本
        text = re.sub(r"(\s|&nbsp;|&#160;|&#xa0;)+", "", text).strip()  # 清洗文本

        for cell in table.find_all(['td', 'th']):
            total_cells += 1  # 计算单元格数量
            cell_text = cell.get_text(strip=True)
            if not cell_text or cell_text.isspace() and 'width' in cell.get('style', ''):
                blank_cells += 1

        if total_cells > 0:
            blank_percentage = (blank_cells / total_cells) * 100
            if blank_percentage >= 40:
                self.blankfunc_2_data.append(text)  # 储存一些可能被误伤的不完整答案表格
                return True
        return False

    def is_answer_table(self, table):

        text = ''.join(table.stripped_strings)
        text = re.sub(r"(\s|&nbsp;|&#160;|&#xa0;)+", "", text).strip()

        text_clean = self.regex_patterns['answer'].sub("", text)
        text_clean = re.sub(
            r'[\[\]]', '', text_clean).strip()

        if bool(re.search('[\u4e00-\u9fff]', text_clean)):
            return False  # 用于排除掉还有别的中文字符的表格 **

        if bool(self.regex_patterns['notanswer'].search(text_clean)):
            return False  # 用于排除一些特殊情况

        text_upper = text.upper()

        count_nonABCD = sum(1 for char in text_upper if bool(
            re.match(r'[A-Z]', char) and char not in "ABCD"))
        if count_nonABCD >= 6:
            return False  # 不应该有太多的非ABCD字符

        text_clean = re.sub(r'[.]', '．', text_clean)  # 替换全角句号

        if '．' in text_clean:  # 如果有全角的句号
            if re.match(r'[A-D]\．\d', text_clean) or re.match(r'[A-D]\.\d', text_clean):
                return False
            elif re.match(r'[A-D]\．[A-Z]', text_clean) or re.match(r'[A-D]\．[A-D]', text_clean):
                return False
            elif re.search(r'[A-D]', text_clean) is None:
                return False
            elif re.match(r'[A-Z]\．[a-zA-Z0-9]+', text_clean):
                return False
            elif re.search(r'[Mg|Li|IaIbI]', text_clean):
                return False
            elif re.search(r'0.\d*', text_clean):
                return False
            elif re.search(r'([A-Z])、\d+', text_clean):
                return False
            elif re.search(r'([A-Z])．｛([^｝]+)', text_clean):
                return False
            elif re.search(r'([A-D])．\s*(－\d+)', text_clean):
                return False
            elif re.search(r'cm', text_clean):
                return False
            else:
                self.ansfunc_data.append(text_clean)  # 未分类的数据
                return True

        else:
            text_clean = re.sub(r'、', '', text_clean)  # 替换中文顿号
            if bool(re.search(r"^(?=.*[a-dA-D]{4,})(?=.*\d{4,}).+$", text_clean)):
                return True  # 有ABCD和数字，认定为是答案表格

        return False

    def is_long_table(self, table):
        is_long = False
        total_text_length = 0
        text = ''.join(table.stripped_strings)
        pattern = re.compile(r'[^\u4e00-\u9fa5]')  # 匹配非中文字符
        rows = table.find_all('tr')
        num_p = 0

        if len(rows) > 10:  # 如果行数大于10
            return False

        for row in rows:
            cells = row.find_all(['th', 'td'])
            for cell in cells:
                num_p = len(cell.find_all('p'))
                if num_p > 10:  # 如果p标签数量大于10
                    is_long = True
                    break

        cleaned_text = re.sub(pattern, '', text)
        total_text_length = len(cleaned_text)

        if total_text_length > 1500:
            is_long = True  # 如果总文本长度大于1500, 认定为长表格

        # teaching_keywords = re.compile(self.regex_long_table)
        # if teaching_keywords.search(table.get_text()):
        #    is_long = True  # Teaching keywords found
        # 不选择用关键词，很多误判。改用文本长度判断

        return is_long

    def classify_table(self, table):
        if self.is_blank_table(table):
            self.counters['blank'] += 1
            type = 'blank'
        elif self.is_answer_table(table):
            self.counters['answer'] += 1
            type = 'answer'
        elif self.is_long_table(table):
            self.counters['long'] += 1
            type = 'long'
        else:
            self.counters['normal'] += 1
            type = 'normal'

        self.counters['total'] += 1

        if type in self.soups:
            self.soups[type].div.append(table)

    @staticmethod  # Static method for splitting answer table
    def clean_text(text, regex_pattern):
        return re.sub(regex_pattern, '', text).strip()  # 清洗文本

    def extract_tables(self):
        return self.soup.find_all('table')

    def split_answer_table(self, table):
        if len(re.findall(r'[.．]', table.get_text())) >= 4 and re.search(r'[\u4e00-\u9fff]', table.get_text()) is None:
            text = ''.join(table.stripped_strings)
            modded_text = re.sub(r'([A-Z])', r'\1 ', text).rstrip()
            return modded_text
        else:
            formatted_string = ""
            question_nums = []
            answer_choices = []

            rows = table.find_all('tr')
            for row in rows:
                cells = row.find_all('td')
                for cell in cells:
                    cell_text = self.clean_text(
                        cell.text, self.regex_patterns['split_answer'])
                    if cell_text:
                        if cell_text.isdigit() or any(char.isdigit() for char in cell_text):
                            question_nums.append(cell_text)
                        else:
                            answer_choices.append(cell_text)

            min_length = min(len(question_nums), len(answer_choices))
            question_nums = question_nums[:min_length]
            answer_choices = answer_choices[:min_length]

            for q_num, a_choice in zip(question_nums, answer_choices):
                formatted_string += f"{q_num}.{a_choice}\n"

            return formatted_string

    def insert_answers_into_document(self, filename):
        tables = self.soups['answer'].find_all('table')
        for table in tables:
            squence = self.split_answer_table(table)
            self.processed_ans_tables.append(squence)

        for i, table in enumerate(tables):
            answer_paragraph = self.soup.new_tag("p")
            answer_paragraph.append(
                NavigableString(self.processed_ans_tables[i]))
            table.insert_after(answer_paragraph)

    def split_long_tables(self):

        output_html_content = "<html><body>"

        for table in self.soups['long'].find_all('table'):
            if len([table.find_all('tr')]) == 1:
                for row in table.find_all('tr'):
                    for cell in row.find_all(['td', 'th']):
                        output_html_content += cell.get_text(strip=True) + ' '
                    output_html_content += "<br><br>"  # Add a new line between rows
                continue  # Skip the rest of the processing for this table
            try:
                sections = []
                current_section_header = None
                current_section_rows = []

                for row in table.find_all('tr'):
                    colspan_cell = row.find(['td', 'th'], colspan=True)
                    if colspan_cell:
                        if current_section_header:
                            sections.append(
                                (current_section_header, current_section_rows))
                        current_section_header = colspan_cell
                        current_section_rows = []
                    else:
                        current_section_rows.append(row)

                if current_section_header:
                    sections.append(
                        (current_section_header, current_section_rows))

                for header, rows in sections:
                    output_html_content += header.get_text(
                        strip=True) + "<br><br>"
                    if len(rows) == 1:
                        for cell in rows[0].find_all(['td', 'th']):
                            output_html_content += cell.get_text(
                                strip=True) + ' '
                    else:
                        headers = [cell.get_text(
                            strip=True) for cell in rows[0].find_all(['td', 'th'])]
                        for row in rows[1:]:
                            cells = row.find_all(['td', 'th'])
                            for header, cell in zip(headers, cells):
                                output_html_content += f"{header}: {
                                    cell.get_text(strip=True)}<br><br>"
                    output_html_content += "<br><br>"
            except IndexError:
                print("IndexError occurred, skipping table")
                continue
            except Exception as e:
                print(f"An error occurred: {e}")
                continue
        output_html_content += "</body></html>"

        self.soups['long'] = BeautifulSoup(output_html_content, 'lxml')

    def output_statistics(self, output_folder, filename):
        stats_path = os.path.join(
            output_folder, f'table_statistics.html')
        with open(stats_path, 'a', encoding='utf-8') as file:
            file.write(
                f"<html><head><title>Table Processing Statistics</title></head><body>")
            file.write("<h1>Table Processing Statistics</h1>")
            file.write(f"<p>Total tables processed: {self.counters['total']}</p>")
            for table_type, count in self.counters.items():
                if table_type != 'total':
                    file.write(
                        f"<p>{table_type.capitalize()} tables: {count}</p>")
            time_now = datetime.now(pytz.timezone(
                'Asia/Shanghai')).strftime('%Y-%m-%d %H:%M:%S')
            file.write(f"<p>Ending time: {time_now}, Filename: {filename}</p>")
            file.write("</body></html>")

    def output_debug(self, output_folder, filename):
        if len(self.ansfunc_data) != 0 or len(self.blankfunc_2_data) != 0 or len(self.blank_anscard_data) != 0:

            debug_path = os.path.join(
                output_folder, f'debugdata{filename}.txt')

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

    def load_html(self, input_html):
        with open(input_html, 'r', encoding='utf-8') as file:
            self.soup = BeautifulSoup(file, 'lxml')

    def save_output(self, output, filename):
        for type, soup in self.soups.items():
            with open(os.path.join(output, f'{type}_table{filename}'), 'w', encoding='utf-8') as file:
                file.write(str(soup))

    def process_tables(self, input, output, filename, split_answer_tables=True, split_long_tables=True, output_stats=True, output_debug=True):
        self.load_html(input)  # Load the HTML file
        tables = self.extract_tables()
        total_tables = len(tables)
        with tqdm(total=total_tables, desc=f"Processing tables in {filename}") as pbar:
            for table in tables:
                self.classify_table(table)
                pbar.update(1)
        if split_answer_tables:
            self.insert_answers_into_document(filename)
        if split_long_tables:
            self.split_long_tables()
        if output_stats:
            self.output_statistics(output, filename)
        if output_debug:
            self.output_debug(output,filename)
        self.save_output(output, filename)
        self.reset()  # Reset the processor for the next file


if __name__ == '__main__':

    processor = TableModule()
    input_folder = r'D:\Work Files\讲义_zip\初中地理'
    output_folder = r'D:\Work Files\Table Module\表格stats319\初中地理'
    for filename in tqdm(os.listdir(input_folder), desc=f"Processing HTML Files in folder {input_folder}"):
        if filename.endswith('.html'):
            input_html = os.path.join(input_folder, filename)
            processor.process_tables(input_html, output_folder, filename)
