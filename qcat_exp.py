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

def QCAT_Execute(raw_log_paths, log_list_brief, output_path):
    for path in raw_log_paths:
        now = datetime.now()
        current_time = now.strftime("%H_%M_%S")
        tmp_name = 'data' + current_time + '.txt'
        file_path = os.path.join(output_path, tmp_name)
        file = open(file_path, "w+")
        file.truncate(0)
        file.close()
        QCAT_hex_log_lst_brief = convert_hex(log_list_brief)
        qcat_parse_log(path, QCAT_hex_log_lst_brief, file_path)








