"""
Data Scripting Example
This script is to read input order raw data and output as formatted data.
Pandas library is needed.
Author: Chin-Ting Ko
Date: 01/04/2018
"""

import pandas as pd
import sys
import os


#path = "scripting_input_file.txt"
path = sys.argv[1]
file = open(path, 'r')

# temp.txt is to handle front whitespace for row19
file1 = open('temp.txt', 'w')
row = 0
for line in file:
    if row == 0:
        file1.write(line)
    else:
        file1.write(',' + line)
    row += 1
file1.close()
path2 = "temp.txt"

# read file to panda data frame, delimiter = tab
input_file = pd.read_table(path2, sep=r'\t', engine='python')
input_file['user_id'] = input_file['user_id'].astype(int)

# fill item price missing value to 0
input_file['item_price_1'] = input_file['item_price_1'].fillna(0).astype(float)
input_file['item_price_2'] = input_file['item_price_2'].fillna(0).astype(float)
input_file['item_price_3'] = input_file['item_price_3'].fillna(0).astype(float)
input_file['item_price_4'] = input_file['item_price_4'].fillna(0).astype(float)
# fill URL missing value to ''
input_file['start_page_url'] = input_file['start_page_url'].fillna('')
# print input_file


# temporary data frame to handle order information
temp_file = pd.DataFrame(input_file['order_id:date'].str.replace(',', '').str.split(':').tolist(), columns=['Order_id', 'Order_date1', 'Order_date2'])
temp_file['Order_date1'] = temp_file['Order_date1'].fillna('').str.replace('[^\d]', '')
temp_file['Order_date2'] = temp_file['Order_date2'].fillna('').str.replace('[^\d]', '')
temp_file['Order_date'] = temp_file['Order_date1'] + temp_file['Order_date2']
temp_file['Order_date'] = temp_file['Order_date'].apply(lambda x: x[:4]+'-'+x[4:6]+'-'+x[6:8] if len(x) == 8 else '')

# temporary data frame to handle average item price
temp_file['Sum'] = input_file['item_price_1'] + input_file['item_price_2'] \
                   + input_file['item_price_3'] + input_file['item_price_4']

temp_file['Product Count'] = input_file['item_price_1'].apply(lambda x: 1 if x > 0 else 0)\
                     + input_file['item_price_2'].apply(lambda x: 1 if x > 0 else 0)\
                     + input_file['item_price_3'].apply(lambda x: 1 if x > 0 else 0)\
                     + input_file['item_price_4'].apply(lambda x: 1 if x > 0 else 0)
# handle 0/0 causes NaN
temp_file['Product Count'] = temp_file['Product Count'].apply(lambda x: x if x > 0 else 1)
temp_file['Avg_Item_price'] = (temp_file['Sum'] / temp_file['Product Count']).round(1)
# handle URL
temp_file['Start_page_url'] = input_file['start_page_url'].apply\
    (lambda x: x if x[:23] == 'http://www.xxx.com' else '')
# handle error message
temp_file['Error_msg'] = input_file['start_page_url'].apply\
    (lambda x: '' if x[:23] == 'http://www.xxx.com' else 'Invalid URL')\
                           + temp_file['Order_id'].apply(lambda x: ' Invalid Order Id' if x == '' else '')\
                           + temp_file['Order_date'].apply(lambda x: ', Invalid Order Date' if x == '' else '')
# print temp_file

# final output data
output_file = pd.DataFrame()
output_file['Order_id'] = temp_file['Order_id']
output_file['Order_date'] = temp_file['Order_date']
output_file['User_id'] = input_file['user_id']
output_file['Avg_Item_price'] = temp_file['Avg_Item_price']
output_file['Start_page_url'] = temp_file['Start_page_url']
output_file['Error_msg'] = temp_file['Error_msg']
print output_file

# print file
# output_file.to_csv('scripting_output.txt', sep=' ', index=False)
output_file.to_csv(sys.argv[2], sep=' ', index=False)
# remove temp file
os.remove('temp.txt')
