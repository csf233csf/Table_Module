import re
from bs4 import BeautifulSoup, NavigableString


class AnswerTableProcessor:
    def __init__(self, html_file_path, regex_pattern):
        self.html_file_path = html_file_path
        self.regex_pattern = regex_pattern
        self.soup = None
        self.processed_tables = []  # To store processed text for all tables

    def load_html(self):
        with open(self.html_file_path, 'r', encoding='utf-8') as file:
            self.soup = BeautifulSoup(file, 'html.parser')

    @staticmethod
    def clean_text(text, regex_pattern):
        return re.sub(regex_pattern, '', text).strip()

    def extract_tables(self):
        return self.soup.find_all('table')

    def process_table(self, table):
        # New code snippet to check for period and preprocess the table text
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

    def insert_answers_into_document(self):
        tables = self.extract_tables()
        for table in tables:
            formatted_string = self.process_table(table)
            self.processed_tables.append(
                formatted_string)  # Save processed text

        # Now, do all the editing at the last step
        for i, table in enumerate(tables):
            answer_paragraph = self.soup.new_tag("p")
            answer_paragraph.append(NavigableString(self.processed_tables[i]))
            table.insert_after(answer_paragraph)

    def save_modified_html(self):
        new_file_path = self.html_file_path.replace('.html', '_modified.html')
        with open(new_file_path, 'w', encoding='utf-8') as file:
            file.write(str(self.soup))


# Usage
html_file_path = 'gpttrials/answer_tables初中英语.html.html'
regex_answer = r'[\u4e00-\u9fff]|:##Z#X#X#K.|[\u2191\u2193]|△|、|大题|阅卷人|评卷人|得分|题次|选项|序号|题号|题目|选择题|答案|分数|成绩|—|Ⅰ|Ⅱ|\]|\[|[一二三四五六七八九十]|新|课|标|第|一|网|来|源|学|科|\||答|题|小|'


processor = AnswerTableProcessor(html_file_path, regex_answer)
processor.load_html()
processor.insert_answers_into_document()
processor.save_modified_html()
