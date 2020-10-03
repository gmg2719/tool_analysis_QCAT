from __future__ import print_function, division

import os
import re
import logging

from math import ceil
from QCAT_Lib.QCAT_Basic import qcat_parse_log, qcat_export_grids, qcat_export_all, qcat_get_field

def retrieve_tx_pwr(raw_log_path, output_path):
    """calculate average Tx Power from log packets"""
    pkt_id = [int('0xB139', 16)]
    outfile = "LTE LL1 PUSCH Tx Report".replace(' ', '_') + ".txt"
    path_outfile = os.path.join(output_path, outfile)

    qcat_parse_log(raw_log_path, pkt_id, path_outfile)

    total_tx_pwr  = 0
    tx_pwr_count  = 0
    total_rb      = 0
    rb_count      = 0
    total_tb_size = 0
    tb_count      = 0

    with open(path_outfile, 'r') as f:
        for line in f:
            stat = line.split('|')
            if len(stat) > 5 and stat[1].strip().isdigit():
                total_tx_pwr += int(stat[29].strip())
                tx_pwr_count += 1

                total_rb     += int(stat[13].strip())
                rb_count     += 1

                total_tb_size += int(stat[14].strip())
                tb_count      += 1

    if tx_pwr_count != 0:
        # print(tx_pwr_count) #5450
        avg_tx_pwr  = ceil(total_tx_pwr / tx_pwr_count)
        avg_rb_num  = ceil(total_rb / rb_count)
        avg_ul_tput = ceil(total_tb_size * 8 / 1024 / tb_count * 10) / 10.0
        return avg_tx_pwr, avg_rb_num, avg_ul_tput



raw_log = "C:\\Users\\admin\Documents\\NguyenHaiHa-thuctap2020\\Log_Analysis-Hoang_version\\Test\\QCAT input\\05-22.16-18.isf"
out_path = "C:\\Users\\admin\Documents\\NguyenHaiHa-thuctap2020\\Log_Analysis-Hoang_version\\Test\\QCAT output\\"
out_file = "C:\\Users\\admin\Documents\\NguyenHaiHa-thuctap2020\\Log_Analysis-Hoang_version\\Test\\QCAT output\\test_parser_02_10.txt"
# out_file = "'C:Users\\admin\\Documents\\NguyenHaiHa-thuctap2020\\Log_Analysis-Hoang_version\\Test\\QCAT output\\05-22.16-18_test_parser_02_10.txt'"
# C:\Users\admin\Documents\NguyenHaiHa-thuctap2020\Log_Analysis-Hoang_version\Test\QCAT output\
# print(retrieve_tx_pwr(raw_log, out_path))
# analyzers = [";LTE;Summary;LTE L1 RI Modulation Type Stats", ";LTE;Summary;LTE PDCP Summary;LTE PDCP DL Stats Summary" ]
# qcat_export_grids(raw_log,analyzers,out_path)
# qcat_export_all(raw_log, out_file)

logId = int("0xB0C0", 16)
# fieldString = ".\"Records\".\"Timing Offset\""
fieldString = "Physical Cell ID ="
# qcat_get_field(raw_log, logId, fieldString, out_file)

from tool_summary import change_file_name

change_file_name(raw_log, out_file)

