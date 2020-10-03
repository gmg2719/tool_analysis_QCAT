import win32com.client
from log_parser_Hoang import read_file, read_config_log_types
from QCAT_Lib.QCAT_Basic import qcat_parse_log, qcat_merge_log
from datetime import datetime
import os

# from variable import log_type_list_brief

def convert_hex(log_list_brief):
    QCAT_hex_log_lst = []
    for log in log_list_brief:
        QCAT_hex_log_lst.append(int(log, 16))
    return QCAT_hex_log_lst

def QCAT_Execute(raw_log_path, log_list_brief, output_path):
    now = datetime.now()
    current_time = now.strftime("%H_%M_%S")
    tmp_name = 'data' + current_time + '.txt'
    file_path = os.path.join(output_path, tmp_name)
    file = open(file_path, "w+")
    file.truncate(0)
    file.close()
    QCAT_hex_log_lst_brief = convert_hex(log_list_brief)
    # log_type_list_brief = [0xb16c, 0xb139]
    # parse_path = r'C:\Users\admin\Desktop\Log_Extractor\Test\FTP DL_eHI04623_MS1_m06090009.dlf'
    # output = r'C:\Users\admin\Desktop\Log_Extractor\Test\Test.txt'
    qcat_parse_log(raw_log_path, QCAT_hex_log_lst_brief, file_path)

# log_type_list_brief = ['0xB16C', '0xB139']
# parse_path = r'C:\Users\admin\Desktop\Log_Extractor\Test\FTP DL_eHI04623_MS1_m06090009.dlf'
# output = r'C:\Users\admin\Desktop\Log_Extractor\Test'
# QCAT_Execute(parse_path, log_type_list_brief, output)


# string = '0xAD4'
# hex_int = int(string, 16)
# # new_int = hex_int + int('0x000', 16)
# print(hex(hex_int))
# hx = 0xAD4
# print(type(hx))
# print(hx)





