import os
from bs4 import BeautifulSoup
import re
from tqdm import tqdm
from datetime import datetime
import pytz
# import htmlmarker # 去水印


class TableProcessor:
    def __init__(self, input_folder, output_folder):
        self.input_folder = input_folder
        self.output_folder = output_folder
        self.output_answer_html = os.path.join(output_folder, 'output_for_answer_tables.html')
        self.output_blank_html = os.path.join(output_folder, 'output_for_blank_tables.html')
        self.output_normal_html = os.path.join(output_folder, 'output_for_normal_tables.html')
        self.output_long_html = os.path.join(output_folder, 'output_for_long_tables.html')
        self.output_test_html = os.path.join(output_folder,'output_for_new_type.html')
        # 我个人做完一个类型的大致筛选会输出到这儿
        
        self.counters = {'total': 0, 'answer': 0, 'blank': 0, 'normal': 0, 'long': 0}
        
        self.regex_long_table = [
            '教学过程', '教学目标', '范文展示', '选择题', '学生活动', '设计意图', '学情分析', '教学重难点', '教师活动',
            '课题', '综合题', '教材分析', '教学环节', '授课时间', '教学器材', '学习目标', '教学辅助', '病文展示', '升格作文',
            '教学方法', '教学活动', '整体赏析', '教学工具', '教学步骤', '授课教师', '学习任务', '课堂活动', '教学资源', '教学内容',
            '学习重难点', '教学内容分析', '新课标要求', '教学单元', '情境导入', '活动意图', '新知讲授', '核心素养', '新课导入',
            '教学重点与难点', '教学准备', '老师活动', '范文点评', '基本信息', '教学活动设计', '活动形式及步骤', '命题情景',
            '讲授新课', '教学策略', '判定技巧', '板书设计', '命题特点', '学习任务（教学目标）', '学习活动（教学步骤）', '学习指向（设计意图）',
            '考查要点', '精彩看点', '课标要求', '本节教学内容', '本节教学目标', '本节教学重难点', '本节内容教学方法', '讲授法', '本节内容课时安排',
            '信息类型', '主题信息', '条件信息', '过程信息', '隐藏信息', '教学设计理念', '文本解读', '活动形式与步骤', '活动层次', '学习效果评价',
            '授课教材', '授课题目', '主题情境', '内容分析', '教学反思', '教学重与难点', '真题展示', '题型特点', '考查要点', '试题来源'
        ]    # Trace to is_long_table not used yet. 还未投入使用
        
        self.regex_blank = r"能力测试|水平测试|[A-Z]组|综合分析题|考场座位号|填空|计算|实验|探究|选择|密封线内不答|综合探究|家长签字|学生签字|分析说明|卷面分|学科王|评卷人|批卷人|复核人|结分人|计分人|附加题|复评人|核分人|累分人|合分人|总分人|阅卷人|选择题|座位号|简答|多选|辨析|第.部分|共\d+分|化学|物理|生物|合计|姓名|班级|成绩|全卷|得分|评卷|选项|座号|地理|连线|选择|材料|部分|总分|分值|题号|题目|答案|分数|Ⅰ|Ⅱ|Ⅲ|—|、|:|～|Â|（|）|\.|\．|\*|,|#|[+-]|﹣|﹢|l|科|扣|卷|面|图|分|次|号|序|目|题|栏|初|核|人|复|-|第|学|非|或|[一二三四五六七八九十]|[0-9]\d*|~|～|[\u2460-\u2473]|新|课|标|第|一|网|来|源|学|科|\]|\[|\||"
        # Trace to *def is_blank_table 用来删除赘余定义空白表格
        
        self.regex_answer = r'[\u2191\u2193]|△|、|&super.?END&|[+-]|[><=＜＞＝]|→|：|[\u2460-\u2473]|&sub.?END&|得分|题次|选项|序号|题号|题目|选择题|答案|分数|成绩|﹣|﹢|\(|\)|—|Ⅰ|Ⅱ|\]|\[|[一二三四五六七八九十]|新|课|标|第|一|网|来|源|学|科|\||'
        # 选择不删除数字 和 Dot
        
        # ** 可以把基本所有很长的Regex或者Keyword都放在__init__ **
        
    # 空白表格 一筛
    # 通过一些关键字，style，html tag和regex去筛选空白表格
    def is_blank_table(self, table):
        parsed_table = str(table)
        soup_copy = BeautifulSoup(parsed_table, 'lxml') # create a copy, we want to return the full table.
        
        if re.fullmatch(r'(<[^<>]*?>|\s)+', parsed_table):
            return True
        if "007.png" in parsed_table or "TABLE_PROTECT" in parsed_table: # 极端情况 ** Protected table不管
            return False
        
        
        #  感觉用不着了
        #if len(soup_copy.find_all('tr')) >= 7 or len(soup_copy.find_all('p')) > 100:
        #    print(1) # 过长的Table或者是p tag过多的table，不是空白表格
        #    return False
        
        for p_tag in soup_copy.find_all('p'): # 另一种极端情况，p段背景颜色为蓝色
            if "background-color:#000080" in str(p_tag.get('style', '')):
                return False
            
        for span_tag in soup_copy.find_all('span'):
            if "color:#ffffff" in str(span_tag.get('style', '')) and not ("background-color:#ffffff" in str(span_tag.get('style', '')) or "background-color:#000080" in str(span_tag.get('style', ''))): # 再考虑一下其他颜色的情况
                span_tag.decompose()

        for img_tag in soup_copy.find_all("img"):
            if 'height="3"' in str(img_tag) or 'width="2"' in str(img_tag):
                img_tag.decompose()

        cleaned_html = str(soup_copy)
        img_count = cleaned_html.count("<img")
        text_clean = "".join(re.split(r"<[^>]+>", cleaned_html)).replace(" ", "").strip()
        
        # *important, remove &nbsp entity
        text_clean = re.sub(r"(\s|&nbsp;|&#160;|&#xa0;)+", "", text_clean).strip()
        
        text_clean = re.sub(self.regex_blank, "", text_clean).strip() # trace back to innit/
        print(text_clean)
        if text_clean == "" or re.search(r"条形码粘贴处|准考证", text_clean):
            if img_count <= 2:
                return True
        
        if bool(re.fullmatch(r'[wW]{0,3}', text_clean)):
            return True # 如果只剩下一个w，或者2个w，基本上是水印，可以认定为空白表 
                        # 这边以后优化好了水印module可以不用 MARK一下**
        print(text_clean)
        return False
    
    # 从html中提取表格
    def extract_tables(self, input_html):
        with open(input_html, 'r', encoding='utf-8') as file:
            soup = BeautifulSoup(file, 'html.parser')

        tables = soup.find_all('table')

        for table in tqdm(tables, desc=f"Processing Tables: {os.path.basename(input_html)}"):
            self.counters['total'] += 1
            
            
            # 不跳过嵌套和图片表格，直接操作
            #if table.find('img') or table.find('table'):
            #    continue  # Skip tables with images or nested tables for now
            
            self.classify_and_save(table)
    
    # 空白表格二筛
    # 通过计算空白表格的数量占多少百分比，用于筛选 答案表格 之后进行二筛
    # 这个函数其实在完善了空白表格 is_blank_table 之后可能没有必要
    def is_blank_table_2(self, table): 
        
        total_cells = 0
        blank_cells = 0
        text = ''.join(table.stripped_strings) # remove blank strs
        text = re.sub(r"(\s|&nbsp;|&#160;|&#xa0;)+", "", text).strip() # remove blank entity & nbsp

        for cell in table.find_all(['td', 'th']):
            total_cells += 1
            cell_text = cell.get_text(strip=True)
            if not cell_text or cell_text.isspace() and 'width' in cell.get('style', ''):
                blank_cells += 1

        if total_cells > 0:
            blank_percentage = (blank_cells / total_cells) * 100
            if blank_percentage >= 40: # *阈值 threshold needed to be changed based on the problem.
                return True
        
        return False
    
    
    # 答案表格筛选
    def is_answer_table(self, table):
        
        # [\u4e00-\u9fff] represents Chinese characters
        
        text = ''.join(table.stripped_strings)
        text = re.sub(r"(\s|&nbsp;|&#160;|&#xa0;)+", "", text).strip()
        
        if bool(re.search('√', text)) and not re.findall('[\u4e00-\u9fff]', text) : # 特殊极端情况，带√的
            return True
        
       
        Ans_type1 = re.search('答案', text) is not None and re.search('题号', text) is not None
        if Ans_type1: # 第一种情况，只带答案和题号，并且没有其他中文字符
            text_without_keywords = text.replace('答案', '').replace('题号', '')
            other_chinese_chars = re.findall('[\u4e00-\u9fff]', text_without_keywords)
            if not other_chinese_chars:
                return True
       
        # Deleted type 2     
            
        Ans_type3 = re.search('答案', text) is not None and re.search('题目', text) is not None
        if Ans_type3: # 第三种情况，答案 和 题目，没有其他中文字符 （其实类似这种很多，应该做个表放innit
            text_without_keywords3 = text.replace('答案', '').replace('题目', '')
            other_chinese_chars3 = re.findall('[\u4e00-\u9fff]', text_without_keywords3)
            if not other_chinese_chars3:
                return True

        text_clean = re.sub(self.regex_answer, "", text).strip() # trace back to innit/
        text_clean = re.sub(r'[\[\]]', '', text_clean).strip() # removes all []
        # text_clean = re.sub(r'[\uFF01-\uFF5E]','',text_clean).strip() # removes all full-width English character. 
        # 这个先不用，它会把 '.' 删掉
        
        # General Check, 做了一个大致的筛选，筛选到一个新的file里，再手动看，细化
        if re.search('[\u4e00-\u9fff]',text_clean):
            return False
        
        if '；' in text_clean:
            return False
        
        
        if '．' in text_clean: # 注意全角的 dot
            if re.match(r'[A-D]\．\d',text_clean) or re.match(r'[A-D]\.\d',text_clean): # 数字. A ，为选项table
                return False
            elif re.match(r'[A-D]\．[A-Z]',text_clean) or re.match(r'[A-D]\．[A-D]', text_clean): # 字母. 字母 选项
                return False
            elif re.search(r'[A-D]',text_clean) is None:
                return False # 没有ABCD
            elif re.match(r'[A-Z]．[a-zA-Z0-9]+',text_clean):
                return False # A．xy11B．xy12C．xy14D．xy21
            elif re.search(r'[Mg|Li]',text_clean):
                return False
            else:
                print("what's left answer table",text_clean)
                return True
        elif bool(re.search(r"^(?=.*[a-zA-Z])(?=.*\d).+$",text_clean)):
            return True
        print('final',text_clean)
        return False
    
    def is_long_table(self, table):
        text = ''.join(table.stripped_strings)
        cleaned_text = re.sub(r'(HXBLANK)+', '', text)
        
        # 这边有问题，先不用
        #for cell in table.find_all('td'):
        #    cell_text = cell.text.replace(" ", "").strip()
            #if cell_text in self.regex_long_table:
                #return True
                
        tr_ = table.find_all('tr')
        if len(tr_) >= 10:
             return False 
            
        if len(cleaned_text) >= 3000:
            return True
        # May need more checker
        
        return False 
    
    # 跑流程 call functions
    # 优先级 空白表格 > 答案表格 > 长表格 
    def classify_and_save(self, table): 
                
        # 空白表格             
        if self.is_blank_table(table):
            self.save_table(table, self.output_blank_html, 'blank')
        # 答案表格
        elif self.is_answer_table(table) is True:
            self.save_table(table, self.output_answer_html, 'answer')
        elif self.is_long_table(table):
            self.save_table(table, self.output_long_html, 'long')            
        # 正常表格
        else:
            self.save_table(table, self.output_normal_html, 'normal')
            
    # 保存表格
    def save_table(self, table, output_path, table_type): 
        with open(output_path, 'a', encoding='utf-8') as f:
            f.write(f"<p>\n</p>\n{str(table)}\n")
        self.counters[table_type] += 1

    # 输出统计文件 / KPI output
    def output_statistics(self):
        stats_path = os.path.join(self.output_folder, 'table_statistics.html')
        with open(stats_path, 'w', encoding='utf-8') as file:
            file.write("<html><head><title>Table Processing Statistics</title></head><body>")
            file.write("<h1>Table Processing Statistics</h1>")
            file.write(f"<p>Total tables processed: {self.counters['total']}</p>")
            for table_type, count in self.counters.items():
                if table_type != 'total':
                    file.write(f"<p>{table_type.capitalize()} tables: {count}</p>")
            time_now = datetime.now(pytz.timezone('Asia/Shanghai')).strftime('%Y-%m-%d %H:%M:%S')
            file.write(f"<p>Ending time: {time_now}</p>")
            file.write("</body></html>")
    
    # Processor Function，用来遍历folder中的html文件并且pass html文件给extract table function
    def process(self):
        for filename in tqdm(os.listdir(self.input_folder), desc="Processing HTML Files"):
            if filename.endswith('.html'):
                input_html = os.path.join(self.input_folder, filename)
                self.extract_tables(input_html)
                self.output_statistics()
                break
                

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
    
    