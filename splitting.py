import re
from bs4 import BeautifulSoup

class TableSplitter:
    def __init__(self, html_file_path, regex_pattern):
        self.html_file_path = html_file_path
        self.regex_pattern = regex_pattern
        self.soup = None
        self.counters = {"original": 0, "processed": 0}

    def load_html(self):
        with open(self.html_file_path, 'r', encoding='utf-8') as file:
            self.soup = BeautifulSoup(file, 'html.parser')

    @staticmethod
    def clean_text(text, regex_pattern):
        return re.sub(regex_pattern, '', text).strip()

    def extract_tables(self):
        return self.soup.find_all('table')

    def split_answer_table(self, table):
        # Check for the presence of a dot or full-width period in the table
        if re.search(r'\.|．', table.get_text()):
            # Custom processing for tables with dots/periods
            text = ''.join(table.stripped_strings)
            modded_text = re.sub(r'([A-Z])', r'\1 ', text).rstrip()
            return modded_text
        else:
            # Standard processing 这边要很注意,因为这种方法检查的是表格的结构/所以不能随便改动Table. 包括使用str(table)
            formatted_string = ""
            question_nums = []
            answer_choices = []

            rows = table.find_all('tr')
            for row in rows:
                cells = row.find_all('td')
                for cell in cells:
                    cell_text = self.clean_text(cell.text, self.regex_pattern)
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

    def process_and_save_tables(self, output_path):
        tables = self.extract_tables()
        for table in tables:
            self.save_table(table, output_path, "original")
            processed_text = self.split_answer_table(table)
            with open(output_path, 'a', encoding='utf-8') as f:
                f.write(f"<p>{processed_text}</p>\n")
            self.counters["processed"] += 1

    def save_table(self, table, output_path, table_type): 
        with open(output_path, 'a', encoding='utf-8') as f:
            f.write(f"<p>\n</p>\n{str(table)}\n")
        self.counters[table_type] += 1

# Usage example
html_file_path = 'gpttrials/answer_tables初中英语.html.html'
regex_answer = r'[\u4e00-\u9fff]|:##Z#X#X#K.|[\u2191\u2193]|△|、|大题|阅卷人|评卷人|得分|题次|选项|序号|题号|题目|选择题|答案|分数|成绩|—|Ⅰ|Ⅱ|\]|\[|[一二三四五六七八九十]|新|课|标|第|一|网|来|源|学|科|\||答|题|小|'

output_path = 'output_path.html'  # Specify the output file path

processor = TableSplitter(html_file_path, regex_answer)
processor.load_html()
processor.process_and_save_tables(output_path)
