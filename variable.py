import re

csv_dict = {}
re_LOG_TITLE = re.compile("(\d\d:\d\d:\d\d\.\d\d\d).*(0x\w{4})")
re_HEADER_START = "--------------"
re_HEADER_END = re_HEADER_START

# Variable for Convert csv
config_file_PATH = r''
# log_file_PATH = r''
log_file_PATH = []
csv_folder_PATH = r''
# raw_log_file_PATH = r''
log_type_list_brief = []
log_type_list_full = []


#Variable for QCAT
QCAT_config_file_PATH = r''
QCAT_raw_log_file_PATH = r''
QCAT_output_directory = r''
QCAT_log_list_brief = []
QCAT_log_list_full = []



# Variable for UplinkAnalysis.py
SystemFrameHdr = ["SFN", "SystemFrameNumber"]
SubFrameHdr = ["Sub-fn", "Sub-frameNumber"]
SFNSF = ["CurrentSFNSF"]
#Test path variable
# pw_ctrl_path = r'G:\PycharmProjects\Log_Extractor_v2\Test\csv\0xB16E.csv'
# dci_path = r'G:\PycharmProjects\Log_Extractor_v2\Test\csv\0xB16C.csv'
# tx_report_path = r'G:\PycharmProjects\Log_Extractor_v2\Test\csv\0xB139.csv'
# phich_path = r'G:\PycharmProjects\Log_Extractor_v2\Test\csv\0xB12C.csv'


pw_ctrl_path = r''
dci_path = r''
tx_report_path = r''
phich_path = r''
path_lst = [pw_ctrl_path, dci_path, tx_report_path, phich_path]
output_path = r''
