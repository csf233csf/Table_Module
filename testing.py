from bs4 import BeautifulSoup
import re

# 将之前定义的函数直接复制到这里，以便使用
# 请确保包含 split_long_table 函数的完整定义


def _rex(left_code, right_code):
    return f"{left_code}((?!{right_code})[\s\S])*?{right_code}"


def format_table(html_data):
    def repl_table(m):
        # 竖着合并的表格先不拆
        if re.search('rowspan="\d+"', m.group()):
            return m.group()

        # 获取表格里每一格里面的文本长度
        soup = BeautifulSoup(m.group(), 'html.parser')
        table = soup.find('table')
        rows = table.find_all('tr')
        flag = False
        for row in rows:
            cells = row.find_all(['th', 'td'])
            if len(cells) >= 3 and len(rows) in [4, 5]:
                break
            for cell in cells:
                text = cell.get_text(strip=True)
                if len(text) > 300:
                    flag = True
        if flag:
            # 清除表格里的特殊写法
            for row in rows:
                cells = row.find_all(['th', 'td'])
                for cell in cells:
                    lines = cell.find_all('p')
                    count = 0
                    text = cell.get_text(strip=True)

                    for line in lines:
                        count += 1
                    # 清除竖着写的形式
                    if count >= len(text):
                        for line in lines:
                            line.string = ''
                        lines[0].string = text

                    # 清除互动，反馈等空白部分
                    if re.fullmatch('(互动与反馈|备注（教师复备栏及学生笔记）|教师复备栏或学生笔记栏|复备栏|旁注|复备与点评|教学札记|板书设计|教学反思|备注|互动与反馈|教学笔记)', text) and lines:
                        lines[0] = ''

            # 清除空的P标签
            p_tags = soup.find_all('p')
            for p in p_tags:
                if not p.get_text().strip():
                    p.extract()
            # 清除表格格式
            cleaned_html = re.sub(
                '</?(table|tr|td|tbody)[^>]*>', '', str(soup))
            cleaned_html = re.sub(
                'class="align-center"|text-align:center', '', cleaned_html)
            # 清除缩进
            cleaned_html = re.sub(
                ' style=";text-indent:[\d\.]+pt"', '', cleaned_html)
            return str(cleaned_html)
            # return '******************************************' + '\n' + str(cleaned_html) + '\n' + '******************************************' + '\n'
        return m.group()

    html_data = re.sub(_rex("<table", "</table>"), repl_table, html_data)
    return html_data


def split_long_table(html_data):
    """ split table into paragraphs with semic words
    """
    def row_needs_split(row, idx):
        """ clas row data needs split or not?
        """
        FLAG_split = False
        for cell in row.find_all('td'):
            num_p = len([c for c in cell.children])  # 考虑到图片单独行
            if num_p >= 10 or (num_p >= 5 and "quest_num" in str(cell)):
                FLAG_split = "split_table"
            # 如果 cell 只有 1 个而且字符不为空
            if len(row.find_all("td")) == 1 and len(cell.text.strip()) != 0 and idx != 0:
                FLAG_split = "single_line"
            # # 如果只有 2 个 td, 则一个是 empty 则分割
            # if len(row.find_all("td")) == 2 and len(cell.text.strip()) == 0 and "<img" not in str(cell):
            #     FLAG_split = True

        # post clean and return result
        if FLAG_split:
            list_lines = []
            for cell in row.find_all('td'):
                cell_line = str(cell)
                cell_text = cell.text.replace(" ", "").strip()
                if len(cell_text) <= 10 and len(cell_text) != 0:
                    if FLAG_split == "split_table":
                        cell_line = f"<p><b>新增标题分割：{cell_text}</b></p>"
                list_lines.append(cell_line)
            return FLAG_split, "".join(list_lines)
        return FLAG_split, str(row)

    def format_row_cell(row):
        """ format cell in row """
        for cell in row.find_all('td'):
            cell_text = cell.text.replace(" ", "").strip()
            if len(cell_text) <= 10:
                # cell.string = cell_text + "!!!" # 好像这个方法不太生效？
                pass
        return row

    def repl_table(m):
        # 判断拆分条件：1. 包含特殊关键词, 2. 某一个 cell 里行数 >= 15
        list_rows = []
        table_soup = BeautifulSoup(m.group(), "lxml")
        mode_split = False
        for idx, row in enumerate(table_soup.find_all('tr')):
            FLAG_split, row_data = row_needs_split(row, idx)
            if FLAG_split == "split_table":
                mode_split = True
                list_rows.append(
                    "###SPLIT###" + "###LINES###" + row_data + "###SPLIT###")
            elif FLAG_split == "single_line":
                mode_split = True
                list_rows.append("###SPLIT###" + row_data)
            else:
                row = format_row_cell(row)
                list_rows.append(str(row))

        list_res = []
        table_str = "".join(list_rows)
        for table in table_str.split("###SPLIT###"):
            if "###LINES###" not in table:
                table = "<table>" + table + "</table>"
            list_res.append(table)
        split_table = "".join(list_res)
        split_table = split_table.replace("###LINES###", "")

        if mode_split:
            list_split_tables.append(m.group())
            list_split_tables.append(split_table)
        else:
            # 不是所有 table 都需要检查
            table_text = re.sub(r"<[^>]+>", "", m.group())
            if re.search("目标|教学|课时", table_text) and len(table_soup.find_all('p')) >= 40:
                list_keep_tables.append(m.group())
        return split_table

    list_keep_tables = []
    list_split_tables = []
    match_regex = r"合作探究、课时、主备人、课题、授课人、新授课、我的疑问、三维目标、教学目标、教学方法、教具准备、授课时间、课后总结、板书设计、当堂检测、教学过程、教学反思、教师活动设计、学生活动设计、教学难点、教学重点、教师活动、学生活动、教学意图、内容与方法、教师复备栏"
    match_regex = match_regex.replace("、", "|")
    html_data = re.sub(
        r'<table[^<>]*?>((?!</table|<table)[\s\S])*?</table>', repl_table, html_data)
    return html_data, list_keep_tables, list_split_tables


def process_html_file(input_file_path, output_file_path):
    with open(input_file_path, 'r', encoding='utf-8') as file:
        html_data = file.read()

    formatted_html = format_table(html_data)

    modified_html, _, _ = split_long_table(html_data)

    # 将修改后的HTML保存到新文件
    with open(output_file_path, 'w', encoding='utf-8') as file:
        file.write(modified_html)

    print(f'Processed HTML has been saved to {output_file_path}')


# 调用process_html_file函数处理指定的HTML文件
input_file_path = 'ppt type table/中学地理.html'  # 更改为你的输入文件路径
output_file_path = 'splitlongtableresult.html'  # 更改为你希望保存输出的路径

process_html_file(input_file_path, output_file_path)
