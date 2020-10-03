import pandas as pd
import os
from datetime import timedelta
from variable import SystemFrameHdr, SubFrameHdr, SFNSF
# from variable import pw_ctrl_path, dci_path, tx_report_path, phich_path

# Create 4 data frame 0xB16C for DCI, 0xB139 for PUSCH Tx Report,
# 0xB16E for PUSCH power control, 0xB12C for PHICH decoding result


# DCI = pd.read_csv(dci_path)
# Tx_Report = pd.read_csv(tx_report_path)
# PHICH = pd.read_csv(phich_path)

####################################################################################

def get_frame_type(data_frame):
    # Check for type of Frame header of a table
    # type 1, type 2
    # type 0: not define: error
    SFN_type, sub_frame_type = '', ''
    for col in data_frame.columns:
        if col in SystemFrameHdr:
            SFN_type = col
            break
        elif col in SFNSF:
            return col
    for col in data_frame.columns:
        if col in SubFrameHdr:
            sub_frame_type = col
            break
        elif col in SFNSF:
            return col
    if SFN_type != '' and sub_frame_type != '':
        return SFN_type, sub_frame_type
    else:
        return 0


# print(get_frame_type(Tx_Report))
# print(Tx_Report.info())
####################################################################################
def get_frame_num(data_frame, type, row, SFN, Subfn, SFNSF):
    # Return System Frame Number and Sub frame number of a row
    if type == 0:
        print("Error")
        return 0
    elif type == 2:
        return str(data_frame[SFN][row]) + str(data_frame[Subfn][row])
    elif type == 12:
        # Tx_Report has frame column is float64 and NaN
        if pd.isnull(data_frame[SFNSF][row]):
            value = 99999
            # return 'NaN'
        else:
            value = int(data_frame[SFNSF][row])
        return str(value)


#####################################################################################
def extend_hdrs(ref_table_lines, new_table_lines, output):
    hdr1 = ref_table_lines[0].rstrip('\n')
    hdr2 = new_table_lines[0].rstrip('\n')
    hdr = hdr1 + ',' + hdr2
    output.write(hdr + '\r')


#######################################################################################
def extend_row_exist(ref_table_lines, new_table_lines, ref_row_num, new_row_num, output):
    # ref_table_lines[ref_row_num].rstrip('\n')
    combine_data = ref_table_lines[ref_row_num].rstrip('\n') + ',' + new_table_lines[new_row_num].rstrip('\n')
    output.write(combine_data + '\r')


######################################################################################

def extend_row_none(ref_table_lines, ref_row_num, numberofhdrs, output):
    empty_data = ''
    for i in range(numberofhdrs):
        empty_data += ','
    combine_data = ref_table_lines[ref_row_num].rstrip('\n') + empty_data
    output.write(combine_data + '\r')

######################################################################################
# Test unit
# Pow_Ctrl = pd.read_csv(r'G:\PycharmProjects\Log_Extractor\Test\0xB16E - Copy.csv')
# Pow_Ctrl['LogTime'] = pd.to_timedelta(Pow_Ctrl['LogTime'])
# PHICH = pd.read_csv(r'G:\PycharmProjects\Log_Extractor\Test\0xB12C - Copy.csv')
# PHICH['LogTime'] = pd.to_timedelta(PHICH['LogTime'])
# DCI = pd.read_csv(r'G:\PycharmProjects\Log_Extractor\Test\0xB16C - Copy.csv')
# DCI['LogTime'] = pd.to_timedelta(DCI['LogTime'])
# Tx_Report = pd.read_csv(r'G:\PycharmProjects\Log_Extractor\Test\0xB139 - Copy.csv')
# Tx_Report['LogTime'] = pd.to_timedelta(Tx_Report['LogTime'])
#
# ref_table = r'G:\PycharmProjects\Log_Extractor\Test\0xB16E - Copy.csv'
# new_table1 = r'G:\PycharmProjects\Log_Extractor\Test\0xB12C - Copy.csv'
# new_table2 = r'G:\PycharmProjects\Log_Extractor\Test\0xB16C - Copy.csv'
# new_table3 = r'G:\PycharmProjects\Log_Extractor\Test\0xB139 - Copy.csv'


def extend_data(ref_dataframe, ref_table, new_dataframe, new_table, diff, output):
    f = open(ref_table, 'r')
    ref_data = f.readlines()
    f = open(new_table, "r")
    new_data = f.readlines()
    extend_hdrs(ref_data, new_data, output)
    # Frame header of the reference dataframe
    ref_SFN, ref_Subfn, ref_SFNSF = '', '', ''
    ref_type = len(get_frame_type(ref_dataframe))
    if ref_type == 12:
        ref_SFNSF = get_frame_type(ref_dataframe)
    if ref_type == 2:
        ref_SFN, ref_Subfn = get_frame_type(ref_dataframe)
    # Frame header of the new dataframe
    new_SFN, new_Subfn, new_SFNSF = '', '', ''
    new_type = len(get_frame_type(new_dataframe))
    if new_type == 12:
        new_SFNSF = get_frame_type(new_dataframe)
    if new_type == 2:
        new_SFN, new_Subfn = get_frame_type(new_dataframe)

    # ref_index, new_index is for dataframe
    # ref_line_index, new_line_index is for txt, csv file
    Time_bound = 1
    anchor = 0
    ref_index, new_index, ref_line_index, new_line_index = 0, 0, 1, 1
    while True:
        # ref_frame_num = str(ref_dataframe['SFN'][ref_index]) + str(ref_dataframe['Sub-fn'][ref_index])
        ref_frame_num = get_frame_num(ref_dataframe, ref_type, ref_index, ref_SFN, ref_Subfn, ref_SFNSF)
        new_index = 0
        while True:
            # print(anchor)
            # new_frame_num = str(new_dataframe['SystemFrameNumber'][anchor + new_index]) + str(new_dataframe['Sub-frameNumber'][anchor + new_index])
            if anchor + new_index >= len(new_dataframe['LogTime']):
                break
            new_frame_num = get_frame_num(new_dataframe, new_type, anchor + new_index, new_SFN, new_Subfn, new_SFNSF)
            if (int(new_frame_num) - int(ref_frame_num)) == diff:
                anchor = anchor + new_index + 1
                new_line_index = anchor
                extend_row_exist(ref_data, new_data, ref_line_index, new_line_index, output)
                break
            # duration = abs(timedelta.total_seconds(ref_dataframe['LogTime'][ref_index] - new_dataframe['LogTime'][anchor + new_index]))
            duration = timedelta.total_seconds(
                ref_dataframe['LogTime'][ref_index] - new_dataframe['LogTime'][anchor + new_index])
            if abs(duration) > Time_bound:
                if duration < 0:
                    extend_row_none(ref_data, ref_line_index, len(new_dataframe.columns), output)
                    break
                else:
                    new_index += 1
                    continue

            # if duration > 0:
            #     new_index += 1
            #     continue
            new_index += 1

        ref_index += 1
        ref_line_index = ref_index + 1
        if ref_index == len(ref_dataframe['LogTime']):
            break
        if anchor >= len(new_dataframe['LogTime']) and ref_index != len(ref_dataframe['LogTime']):
            while ref_index != len(ref_dataframe['LogTime']):
                extend_row_none(ref_data, ref_line_index, len(new_dataframe.columns), output)
                ref_index += 1
                ref_line_index = ref_index + 1
            break
        # if anchor + new_index > len(new_dataframe['LogTime']) and ref_index != len(ref_dataframe['LogTime']):
        #     while ref_index != len(ref_dataframe['LogTime']):
        #         extend_row_none(ref_data, ref_line_index, len(new_dataframe.columns), output)
        #         ref_index += 1
        #         ref_line_index = ref_index + 1
        #     break

    output.close()

###########################################################################################
# new_table4 = r'G:\PycharmProjects\Log_Extractor\Test\output_test.csv'
# prev_data = pd.read_csv(r'G:\PycharmProjects\Log_Extractor\Test\output_test.csv')
# extend_data(Pow_Ctrl, ref_table, PHICH, new_table1, 4)
# extend_data(prev_data, new_table4, DCI, new_table2, -4)

def Execute(pw_ctrl_path, dci_path, tx_report_path, phich_path, output_path):
    index = 0
    ref_path = ''
    if pw_ctrl_path == '':
        return
    else:
        ref_path = pw_ctrl_path
    path_dict = {dci_path:-4, tx_report_path:0, phich_path:4}
    for i, path in enumerate(path_dict):
        if path == '':
            continue
        else:
            ref_dataframe = pd.read_csv(ref_path)
            ref_dataframe['LogTime'] = pd.to_timedelta(ref_dataframe['LogTime'])
            new_frame = pd.read_csv(path)
            new_frame['LogTime'] = pd.to_timedelta(new_frame['LogTime'])
            Path = os.path.join(output_path, 'data number_' + str(i) + '.csv')
            output = open(Path, 'a+')
            output.truncate(0)
            extend_data(ref_dataframe, ref_path, new_frame, path, path_dict[path], output)
            ref_path = Path
            output.close()

    # if dci_path != '':
    #     ref_dataframe = pd.read_csv(ref_path)
    #     ref_dataframe['LogTime'] = pd.to_timedelta(ref_dataframe['LogTime'])
    #     dci_frame = pd.read_csv(dci_path)
    #     dci_frame['LogTime'] = pd.to_timedelta(dci_frame['LogTime'])
    #     Path = os.path.join(output_path, str(index) + '.csv')
    #     output = open(Path, 'w')
    #     extend_data(ref_dataframe, ref_path, dci_frame, dci_path, -4, output)
    #     index += 1
    #     ref_path = Path
    # if tx_report_path != '':
    #     ref_dataframe = pd.read_csv(ref_path)
    #     ref_dataframe['LogTime'] = pd.to_timedelta(ref_dataframe['LogTime'])
    #     tx_frame = pd.read_csv(tx_report_path)
    #     # tx_frame['CurrentSFNSF'] = tx_frame['CurrentSFNSF'].astype(int)
    #     tx_frame['LogTime'] = pd.to_timedelta(tx_frame['LogTime'])
    #     Path = os.path.join(output_path, str(index) + '.csv')
    #     output = open(Path, 'w')
    #     extend_data(ref_dataframe, ref_path, tx_frame, tx_report_path, 0, output)
    #     index += 1
    #     ref_path = Path
    #
    # if phich_path != '':
    #     ref_dataframe = pd.read_csv(ref_path)
    #     ref_dataframe['LogTime'] = pd.to_timedelta(ref_dataframe['LogTime'])
    #     phich_frame = pd.read_csv(tx_report_path)
    #     phich_frame['LogTime'] = pd.to_timedelta(phich_frame['LogTime'])
    #     Path = os.path.join(output_path, str(index) + '.csv')
    #     output = open(Path, 'w')
    #     extend_data(ref_dataframe, ref_path, phich_frame, phich_path, 4, output)
    #     index += 1
    #     ref_path = Path



########################################################################################################
# output_path = r'G:\PycharmProjects\Log_Extractor_v2\Test\Merge'
# Test
# Execute(pw_ctrl_path, dci_path, tx_report_path, phich_path, output_path)
