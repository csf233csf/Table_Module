import os
from bs4 import BeautifulSoup
import re
from tqdm import tqdm
from classification import TableProcessor

# 用来跑单个 case
table1 = '''<table cellpadding="0" cellspacing="0" style="margin-left:2.62pt; border:0.75pt dotted #cccccc; border-collapse:collapse"><tbody><tr><td style="width:98.7pt; border-right:0.75pt dotted #cccccc; padding:2.25pt 1.12pt; vertical-align:middle; background-color:#ffffff"><p style="margin-top:0pt; margin-bottom:0pt; line-height:19.5pt; vertical-align:middle; background-color:#ffffff"><span style="font-size:10.5pt; vertical-align:middle; background-color:#ffffff">A．32</span></p></td><td style="width:97.95pt; border-right:0.75pt dotted #cccccc; border-left:0.75pt dotted #cccccc; padding:2.25pt 1.12pt; vertical-align:middle; background-color:#ffffff"><p style="margin-top:0pt; margin-bottom:0pt; line-height:19.5pt; vertical-align:middle; background-color:#ffffff"><span style="font-size:10.5pt; vertical-align:middle; background-color:#ffffff">B．67</span></p></td><td style="width:97.95pt; border-right:0.75pt dotted #cccccc; border-left:0.75pt dotted #cccccc; padding:2.25pt 1.12pt; vertical-align:middle; background-color:#ffffff"><p style="margin-top:0pt; margin-bottom:0pt; line-height:19.5pt; vertical-align:middle; background-color:#ffffff"><span style="font-size:10.5pt; vertical-align:middle; background-color:#ffffff">C．99</span></p></td><td style="width:133.3pt; border-left:0.75pt dotted #cccccc; padding:2.25pt 1.12pt; vertical-align:middle; background-color:#ffffff"><p style="margin-top:0pt; margin-bottom:0pt; line-height:19.5pt; vertical-align:middle; background-color:#ffffff"><span style="font-size:10.5pt; vertical-align:middle; background-color:#ffffff">D．166</span></p></td></tr></tbody></table>'''



with open('important, check.html','r',encoding='UTF-8') as f:
    soup = BeautifulSoup(f,'lxml')

tablelist = soup.find_all('table')

table1 = BeautifulSoup(table1,'lxml')
processor = TableProcessor(input_folder ='',output_folder='')



result= processor.is_answer_table(table1)

print(result)