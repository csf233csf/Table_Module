from bs4 import BeautifulSoup
import re

class TableClassifier:
    def __init__(self, input_file, output_file):
        self.input_file = input_file
        self.output_file = output_file

    def is_long_table(self, table):
        # 定义判断长表格的逻辑
        rows = table.find_all('tr')
        flag_split = False
        total_text_length = 0

        for idx, row in enumerate(rows):
            cells = row.find_all(['th', 'td'])
            num_p_in_cells = [len(cell.find_all('p')) for cell in cells]

            if any(num_p >= 10 or (num_p >= 5 and "quest_num" in str(cell)) for num_p, cell in zip(num_p_in_cells, cells)):
                flag_split = True
            if len(cells) == 1 and cells[0].get_text(strip=True) and idx != 0:
                flag_split = True
            
            total_text_length += sum(len(cell.get_text(strip=True)) for cell in cells)
        
        # 其他可能的长表格判断条件，比如行数和总文本长度
        if len(rows) > 10 or total_text_length > 1000:
            flag_split = True

        # 检查是否包含教学相关的关键词
        teaching_keywords = re.compile("合作探究|课时|主备人|课题|授课人|新授课|我的疑问|三维目标|教学目标|教学方法|教具准备|授课时间|课后总结|板书设计|当堂检测|教学过程|教学反思|教师活动设计|学生活动设计|教学难点|教学重点|教师活动|学生活动|教学意图|内容与方法|教师复备栏")
        if teaching_keywords.search(table.get_text()):
            flag_split = True

        return flag_split

    def classify_tables(self):
        with open(self.input_file, 'r', encoding='utf-8') as file:
            html_data = file.read()

        soup = BeautifulSoup(html_data, 'html.parser')
        tables = soup.find_all('table')
        long_tables = [table for table in tables if self.is_long_table(table)]

        if long_tables:
            with open(self.output_file, 'w', encoding='utf-8') as file:
                for table in long_tables:
                    file.write(str(table))
                    file.write("\n\n")  # 添加空行以分隔各个表格

        return len(long_tables)


input_file_path = 'ppt type table/中学地理.html'
output_file_path = 'splitlongtable.html'
classifier = TableClassifier(input_file_path, output_file_path)
num_long_tables = classifier.classify_tables()

print(f"Identified {num_long_tables} long tables. Output saved to {output_file_path}")
