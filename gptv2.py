from bs4 import BeautifulSoup
import re

def process_and_append_answers(html_file_path, output_file_path):
    with open(html_file_path, 'r', encoding='utf-8') as file:
        soup = BeautifulSoup(file, 'html.parser')

    regex_remove_chinese = r'[\u4e00-\u9fff]'  # Matches any Chinese character
    all_tables = soup.find_all('table')
    for table in all_tables:
        answers = []

        # Extract question numbers from the first row
        question_nums = [cell.get_text(strip=True) for cell in table.find_all('tr')[0].find_all('td')]
        
        # Initialize an empty list to hold all answer choices
        answer_choices = []

        # Correctly capturing additional rows of answers, starting from the second row of answers
        additional_rows = table.find_all('tr')[2:]  # Adjusted to skip the first row of question numbers

        for row in additional_rows:
            row_answers = [cell.get_text(strip=True) for cell in row.find_all('td')]
            answer_choices.extend(row_answers)  # Extend the list with answers from the current row

        # Cleaning and pairing question numbers with their answers
        for q_num, a_choice in zip(question_nums, answer_choices):
            q_num_clean = re.sub(regex_remove_chinese, '', q_num)
            a_choice_clean = re.sub(regex_remove_chinese, '', a_choice)
            if q_num_clean and a_choice_clean:
                answers.append(f"{q_num_clean}.{a_choice_clean}")

        # Append the answers as a paragraph under each table
        if answers:
            answer_paragraph = soup.new_tag("p")
            for answer in answers:
                answer_paragraph.append(BeautifulSoup(answer + "<br/>", 'html.parser'))
            table.insert_after(answer_paragraph)

    # Save the modified HTML to the new file
    with open(output_file_path, 'w', encoding='utf-8') as file:
        file.write(str(soup))


# Adjust file paths as necessary
html_file_path = 'gpttrials/answer_tables.html'  # Replace with your actual file path
output_file_path = 'gpttrials/answer_table_mod.html'  # Define your output file path
process_and_append_answers(html_file_path, output_file_path)
