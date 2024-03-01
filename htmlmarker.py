from bs4 import BeautifulSoup
import re
import os

class HTMLMarker:
    def __init__(self):
        self.regex_patterns = {
    'default': r'w\s*w\s*w\..*',
    'custom_1': r'\.c\s*o\s*m',
    'custom_2': r'\s*新\s*课\s*标\s*第\s*一\s*网\s*',
    'custom_3': r'w\s*w\.\s*.*\s*\.c\s*o\s*m',
    'custom_4': r'\.c\s*o\s*',
    'custom_5': r'\.c\s*o\s*m$',
    'custom_6': r'x\s*k\s*b\s*1\s*.\s*c\s*o\s*m',
    'custom_7': r'xHXBLANKkHXBLANKbHXBLANK1',
    '8': r'\[来源:学。科。网Z。X。X。K\]',
    '9': r'\[来源:学HXBLANK科HXBLANK网\]',
    '10': r'xkb1.com',
    '11': r'\[来源:学\|科\|网Z\|X\|X\|K',
    '12': r'w\s*w\s*w\s*.x\s*k\s*b\s*1.c\s*o\s*m',
    '13': r'\[来源:Z\*xx\*k.Com\]\[来源:学HXBLANK科HXBLANK网\]x\s*k\s*b\s*1\s*.\s*c\s*o\s*m\[来源:学#科#网Z#X#X#K\]',
    '14': r'X\s*k\s*b\s*1\s*.\s*c\s*o\s*m',
    '15': r'x\s*k\s*b\s*1\s*.\s*c',
    '16': r'x.k.b.1',
    '17': r'x\s*k\s*b\s*1\s*.\s*c\s*o\s*m',
    '18': r'\[来源:Z,xx,k.Com\]',
    '19': r'w\s*w\s*w\s*.x\s*k\s*b\s*1.c\s*o\s*m',
    '20': r'xkb1.com',
    '21': r'\[来源:学#科#网\]',
    '22': r'x\s*kb\s*1',
    '23': r'\[来源:学\+科\+网Z\+X\+X\+K\]',
    '24': r'新HXBLANK课HXBLANK标第HXBLANK一HXBLANK网',
    '25': r'\[来源:学&科&网Z&X&X&K\]\[来源来源:学*科*网Z*X*X*K\]',
    '26' : r'\[来源:学&科&网Z&X&X&K\]'
    	

    
    # 此处可以添加更多的regex patterns
                                }






    def remove_watermarks(self, html_content, pattern_key = None, file_name = None):

        soup = BeautifulSoup(html_content, 'lxml')

        # 如果不pass in key，就默认使用所有的regex
        if pattern_key is None:
            for key, regex in self.regex_patterns.items(): 
            # 可以使用 regex_patterns.values() 但我觉得加一个key 以后需要方便直接改
                watermark_elements = soup.find_all(string=re.compile(regex, re.IGNORECASE))
                img_elements = soup.find_all('img', alt=re.compile(regex, re.IGNORECASE))
                p_elements = soup.find_all('p')

                for img_element in img_elements:
                    img_element.extract()
                    print(f"已清除对应水印图片，文件名: {file_name}")

                for element in watermark_elements:
                    # 检查一下是否带img
                    if element.find_parent('img'):
                        element.find_parent().extract()
                        print(f"已清除图片，文件名: {file_name}")
                    else:
                        removed_watermark = element.extract().strip()
                        print(f"已清除水印: {removed_watermark} 文件名: {file_name}")

                for p_element in p_elements:
                    span_elements = p_element.find_all('span') 
                    # 把一些paragraph里面的span combine成text，方便我们locate被分割的水印
                    combined_text = ''.join(span.get_text() for span in span_elements)
                    # 在结合的text中用regex search寻找，extract element if found
                    if regex and re.search(regex, combined_text, re.IGNORECASE):
                        p_element.extract()
                        print(f"已清除水印: {combined_text} 文件名: {file_name}")

        else:
            # 如果pass in了pattern key，则使用指定的regex
            regex = self.regex_patterns.get(pattern_key, '')
            if regex:
                watermark_elements = soup.find_all(text=re.compile(regex, re.IGNORECASE))
                img_elements = soup.find_all('img', alt=re.compile(regex, re.IGNORECASE))
                p_elements = soup.find_all('p')

                for img_element in img_elements:
                    img_element.extract()
                    print(f"已清除对应水印图片，文件名: {file_name}")
                    
                for element in watermark_elements:
                    # 检查一下是否带img
                    if element.find_parent('img'):
                        element.find_parent().extract()
                        print(f"已清除图片，文件名: {file_name}")
                    else:
                        removed_watermark = element.extract().strip()
                        print(f"已清除水印: {removed_watermark} 文件名: {file_name}")
                
                for p_element in p_elements:
                    span_elements = p_element.find_all('span') 
                    combined_text = ''.join(span.get_text() for span in span_elements)
                    if regex and re.search(regex, combined_text, re.IGNORECASE):
                        p_element.extract()
                        print(f"已清除水印: {combined_text} 文件名: {file_name}")

        cleaned_html = str(soup)
        return cleaned_html

class HTMLProcessor:
    def __init__(self, input_folder, output_folder):
        self.input_folder = input_folder
        self.output_folder = output_folder
        # ** 这边pass in marker 调用 **
        self.marker = HTMLMarker()

    def process_files(self, pattern_key=None):

        for filename in os.listdir(self.input_folder):

            # 这边查找所有html doc
            if filename.endswith(".html"): 
                input_filepath = os.path.join(self.input_folder, filename)
                # 这边输出html doc前面加上processed
                output_filepath = os.path.join(self.output_folder, f"processed_{filename}") 

                with open(input_filepath, 'r', encoding='utf-8') as file:
                    html_content = file.read()

                # use marker
                cleaned_html = self.marker.remove_watermarks(html_content, pattern_key = pattern_key, file_name = filename)

                # output and write
                with open(output_filepath, 'w', encoding = 'utf-8') as file:
                    file.write(cleaned_html)

                # 处理完毕输出console
                print(f"\n处理完毕: {filename}\n")

if __name__ == "__main__":
    # 输入和输出文件夹名称
    input_folder_path = 'exam type table'
    output_folder_path = 'exam type table'
    # 需要pass in的regex
    pattern_key = 'default'

    processor = HTMLProcessor(input_folder_path, output_folder_path)

    # 如果这边Pass in None就默认使用所有的正则表达式
    processor.process_files(pattern_key=None) 
