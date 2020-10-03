# version:
#   date:   15/9/20
#############################################Changes################################################
# + Update to use for multiple files 
#
# About:
# PARSE Log Packets from a qcat text export file
# + read configured log type list from a config file
# + func to browse the txt log file and extract all wanted packets
# + for each log packet, call func to rip header and append value rows to tables
# + for each table, write to one CSV
import re, sys, os
from time import process_time
from variable import *

# csv_dict = {}
# re_LOG_TITLE = re.compile("(\d\d:\d\d:\d\d\.\d\d\d).*(0x\w{4})")
# re_HEADER_START = "--------------"
# re_HEADER_END = re_HEADER_START


####################################################################################
def read_file(filename):
    """
    Read the text file with the given filename;
    return a list of the lines of text in the file.
    """
    try:
        f = open(filename, 'r')
        return f.readlines()
    except IOError:
        print("Error opening or reading input file: ", filename)
        sys.exit()

# lines = read_file('G:/PycharmProjects/Log_Extractor/parser.cfg')
######################################################################################

def read_config_log_types(lines):
    # TODO:
    t_dict = {}
    types_long = []
    types_short = []
    re_LOG_type = re.compile('(0x\w{4})')
    for line in lines:
        # Read packet ID
        short = re_LOG_type.match(line)
        if short:
            types_short.append(short.group())
            types_long.append(line)
        # Read QCAT templates
        if line.find(':') != -1 and line[0] != '#':
            temp = line.split(':')
            t_dict[temp[0].rstrip()] = temp[1].rstrip()
    return types_short, types_long, t_dict

######################################################################################

# log_type_list_brief, log_type_list_full = read_config_log_types(lines)

#######################################################################################
def combine_log(log_paths):
    lines = []
    if len(log_paths) == 1:
        return read_file(log_paths[0])
    else:
        for path in log_paths:
            new_lines = read_file(path) # list of all lines in log
            lines.extend(new_lines)
    return lines


########################################################################################
def parse_log(logfilePath, log_type_list_brief, csv_dict):
    # global csv_dict
    count_line = 0
    log_pkt = []
    in_wanted_packet = False
    log_time, log_type = "", ""
    time_start = process_time()

    # logfile = open(logfilePath, "rt")
    # logfile = read_file(logfilePath)
    logfile = combine_log(logfilePath)

    # Browse through log file, collect each log packet
    for line in logfile:
        count_line += 1

        res = re_LOG_TITLE.search(line)
        if res != None:  # reach a new packet
            if in_wanted_packet:
                # end of the previous wanted-packet: process it
                add_log_packet(log_pkt, csv_dict, log_type, log_time)  # already known previous logtype/logtime
                log_pkt = []
                in_wanted_packet = False
            # got a new wanted packet
            # print(log_type_list_brief)
            # print(res.group(2))
            if res.group(2) in log_type_list_brief:  # start of a wanted packet
                in_wanted_packet = True
                log_time = res.group(1)
                log_type = res.group(2)
        if in_wanted_packet:
            log_pkt.append(line) # Append all lines after line of log packet id
    # -- end for: checked whole file
    if in_wanted_packet:  # End of file, add the last wanted packet in file if inside it
        add_log_packet(log_pkt, csv_dict, log_type, log_time)

    # logfile.close()
    time_stop = process_time()

    # print(" @@@: Finished log: %d lines, in %d sec, Num log packets found:\n" \
    #       % (count_line, round(time_stop - time_start, 1)))
    # for t in log_type_list_brief:
    #     print("\t\t Log %s: \t %d\n" % (t, csv_dict[t][0]))


# --- END FUNC: parse_log
##########################################################################################
def add_log_packet(packet, store, log_type, log_time):
    # 1st line is the title
    # is_hdr_start, is_hdr_end = False, False
    # pkt_header, pkt_body = [], []

    # print("add log for " + log_type)

    # TODO: add time column
    # TODO: ignore packet with no header
    for line in packet:
        if line.find(re_HEADER_END) != -1:
            add_log_table(packet, store, log_type, log_time)
            return

    add_log_text(packet, store, log_type, log_time)


# --- END FUNC: add_log_packet ---
########################################################################################
def add_log_table(packet, store, log_type, log_time):
    # browse down to top, to only get the body/header at the end of packets (if multiple table)
    # Process table type log packet
    is_hdr_start, is_hdr_end = False, False
    pkt_header, pkt_body = [], []
    for l in reversed(packet):
        if l.strip().strip("\n") == "":  # ignore empty lines
            continue

        if (not is_hdr_start) and (not is_hdr_end):
            # if not found find func return -1
            if l.find(re_HEADER_END) == -1:
                (row, row_length) = convert_csv(l, log_time)
                if row_length > 1:
                    pkt_body.append(row)
                else:
                    sys.exit("FATAL: Got empty body row for log: " + log_type + " " + log_time)
            else:
                is_hdr_end = True
                if store[log_type][0] > 0:  # csv_data already got header for this type
                    break
        elif is_hdr_end and (not is_hdr_start):
            if l.find(re_HEADER_START) == -1:
                pkt_header.append(l)
            else:
                is_hdr_start = True
                break
    # end for

    if store[log_type][0] == 0:  # no header stored yet
        # Change reverse to ::-1, reverse return none type
        hdr = convert_csv_header(pkt_header[::-1])
        # print("header:  " + hdr)
        store[log_type][1].append(hdr)

    # print(pkt_body)
    store[log_type][0] += len(pkt_body)
    # Change append to extend
    store[log_type][1].extend(pkt_body[::-1])


########################################################################################
def add_log_text(packet, store, log_type, log_time):
    # Process text type log packet
    text_pattern = re.compile("([^=]+).*=(.+)")
    headers, values = ['LogTime'], [log_time]

    for line in packet:
        tmp = text_pattern.search(line)
        if re_LOG_TITLE.search(line) != None or line.isspace() == True:
            continue
        if tmp != None:
            headers.append(tmp.group(1))
            values.append(tmp.group(2))

    # Strip off the whitespace
    for i, hdr in enumerate(headers):
        headers[i] = hdr.replace(' ', '')

    for i, val in enumerate(values):
        values[i] = val.replace(' ', '')
    if store[log_type][0] == 0:
        header = ','.join(headers)
        store[log_type][1].append(header)

    store[log_type][0] += 1
    store[log_type][1].append(','.join(values))


###############################################################################################

def convert_csv(line, log_time):
    # Note: process symbol '|' at the beginning
    indices = re.match('\s*\|', line).span()[1]
    line = line[indices:len(line) - 2]
    a = line.strip().split("|")
    a = [x.strip() for x in a]
    a.insert(0, log_time)
    return ",".join(a), len(a)

##########################################################################################

def get_lst_header(hdr_str):
    # Function to return a list of sub_header extracted from line
    indices = re.match('\s*\|', hdr_str).span()[1]
    hdr_str = hdr_str[indices: len(hdr_str) - 2]
    header_lst = hdr_str.split('|')
    # header_lst.insert(0, 'LogTime')
    for i, hdr in enumerate(header_lst):
        if hdr.isspace():
            header_lst[i] = ''
        else:
            header_lst[i] = hdr.replace(' ', '')
    return header_lst, len(header_lst)

##############################################################################################

def get_delim_index(hdrs):
    # Return a list of delimiter ("|") in a line
    delim_lst = []
    for i, e in enumerate(hdrs):
        if e == '|':
            delim_lst.append(i)
    return delim_lst

##############################################################################################

def header_fill(last_hdr_lst, hdr_lst, lhdr_delim_index, hdr_delim_index):
    # Function to fill the line with smaller number of headers than the reference line (last line)
    lhdr_delim_index = lhdr_delim_index[1:]
    hdr_delim_index = hdr_delim_index[1:]
    # i,j used as counting variable for list of delimiter index, k used as counting variable for header list
    # Method: iterate over both reference header and the choosen header at the same time
    # If the index of the choosen header delimiter is greater than the choosen header delimiter
    # then insert the header at position k to the position k+1
    i, j, k = 0, 0, 0
    while True:
        span = hdr_lst[k]
        if hdr_delim_index[i] == lhdr_delim_index[j]:
            i += 1
            j += 1
            k += 1
            span = hdr_lst[k]
        if hdr_delim_index[i] > lhdr_delim_index[j]:
            j += 1
            hdr_lst.insert(k + 1, span)
            k += 1
        if j == len(lhdr_delim_index) - 1 and i == len(hdr_delim_index) - 1:
            break
###############################################################################################

# test = ['|   |Carrier|Num Slots |Num PDSCH |Num CRC   |Num CRC   |          |ACK As    |HARQ      |                    |                    |                    |                    |          |', '|#  |ID     |Elapsed   |Decode    |Pass TB   |Fail TB   |Num ReTx  |NACK      |Failure   |CRC Pass TB Bytes   |CRC Fail TB Bytes   |TB Bytes            |Padding Bytes       |BLER      |']
def convert_csv_header(hdr):
    # Example:
    # |   |                                          |TB Info                                                                                                                                                                                                                                                                                                 |
    # |   |                                          |   |                                                        |LC Packet Info                                                                                                                                                                                                                             |
    # |   |                                          |   |                                                        |     |      |    |      |Num  |Num  |       |       |                     |      |       |      |                   |          |                                |                   |          |                              |            |
    # |   |                                          |   |Meta                                                    |     |      |    |      |First|Last |       |       |                     |      |       |First |                   |          |                                |                   |          |                              |            |
    # |   |Meta                                      |   |                          |    |          |     |Num LC |     |      |    |      |Pkt  |Pkt  |       |       |                     |Num   |Num    |Pkt   |First Packet PDCP  |          |                                |Last Packet PDCP   |          |                              |            |
    # |   |System Time  |          |   |      |      |   |MCE BMask                 |    |          |Num  |Packet |     |      |    |      |PDCP |PDCP |       |RLC    |                     |RLC   |PDCP   |PDCP  |Header             |          |First Packet RLC Header         |Header             |          |Last Packet RLC Header        |Remaining   |
    # |   |Slot  |      |          |   |      |Num TB|   |   |MCE  |                |CA  |          |LC   |Info   |     |      |RB  |Tx    |Hdr  |Hdr  |Last   |Start  |PDCP Start Count     |Status|Control|Header|DC  |PDU  |        |First Pkt |DC  |    |    |        |        |DC  |PDU  |        |Last Pkt  |DC  |    |  |        |        |Bytes Last  |
    # |#  |Number|FN    |TB        |TTI|Num TB|Entry |#  |Pad|Built|BSR Type        |ID  |Numerology|Built|Entries|Entry|LCID  |Type|Type  |Bytes|Bytes|Poll SN|SN     |SN          |HFN     |PDUs  |PDU    |Offset|Bit |Type |SN      |PDCP Hdr  |Bit |P   |SI  |SN      |SO      |Bit |Type |SN      |PDCP Hdr  |Bit |P   |SI|SN      |SO      |Pkt         |

    ref_hdr, ref_count = get_lst_header(hdr[len(hdr) - 1])
    ref_delim_index = get_delim_index(hdr[len(hdr) - 1])

    for i in reversed(range(len(hdr) - 1)):
        tmp_hdr, tmp_count = get_lst_header(hdr[i])
        if tmp_count == ref_count:
            for j in range(len(ref_hdr)):
                # Combine 2 list of header with the same length
                ref_hdr[j] = tmp_hdr[j] + ref_hdr[j]
        else:
            tmp_delim_index = get_delim_index(hdr[i])
            header_fill(ref_hdr, tmp_hdr, ref_delim_index, tmp_delim_index)
            for j in range(len(ref_hdr)):
                if ref_hdr[j]!='' and tmp_hdr[j]!='':
                    ref_hdr[j] = tmp_hdr[j] + '/' +ref_hdr[j]
                else:
                    ref_hdr[j] = tmp_hdr[j] + ref_hdr[j]
        # process here
    ref_hdr.insert(0, 'LogTime')
    ref_hdr = ','.join(ref_hdr)
    return ref_hdr

##############################################################################################
def write_csv(folder_path, csv_dict):
    # Export to csv format file in folder_path directory
    for log_key in csv_dict:
        if csv_dict[log_key][0] == 0:
            continue
        else:
            # file_name = csv_dict[log_key]
            csv_path = os.path.join(folder_path, log_key + '.csv')
            f = open(csv_path, "a+")
            f.truncate(0)
            for line in csv_dict[log_key][1]:
                f.write(line + '\r')
            f.close()

##############################################################################################

####Test module###############################################################################
# def main():
#     for t in log_type_list_brief:  # init dict of log data list for csv
#         csv_dict[t] = [0, []]
#     data_path = r'G:\PycharmProjects\Log_Extractor\Test'
#     log_name = 'log_test.txt'
#     parse_log(os.path.join(data_path, log_name))
#     write_csv(data_path, csv_dict)
#     print(csv_dict)
#
#
# if __name__ == '__main__':
#     main()
