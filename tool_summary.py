from __future__ import print_function, division

import os
import re
import logging

from math import ceil
from QCAT_Lib.QCAT_Basic import qcat_export_text


templates = {
    "LTE L1 RI Modulation Type Stats"   : ";LTE;Summary;LTE L1 RI Modulation Type Stats",
    "LTE PDCP DL Stats Summary"         : ";LTE;Summary;LTE PDCP Summary;LTE PDCP DL Stats Summary",
    "LTE PDCP UL Stats Summary"         : ";LTE;Summary;LTE PDCP Summary;LTE PDCP UL Stats Summary",
    "LTE Pdsch Stat Indication vs. Time": ";LTE;Time Grids;LTE Pdsch Stat Indication vs. Time",
    "LTE DL Throughput vs. Time"        : ";LTE;Time Grids;Phy/RLC/PDCP Grids;LTE DL Throughput vs. Time",
    "LTE UL Throughput vs. Time"        : ";LTE;Time Grids;Phy/RLC/PDCP Grids;LTE UL Throughput vs. Time",
    "LTE DCI Info vs. Time"             : ";LTE;Time Grids;Physical Grid;LTE DCI Info vs. Time",
    "LTE L1 CQI RI and MCS vs. Time"    : ";LTE;Time Grids;Physical Grid;LTE L1 CQI RI and MCS vs. Time",
    "LTE DL BLER Vs Subfr"              : ";LTE;Time Grids;Physical Grid;LTE DL BLER Vs Subfr",
    "LTE L1 Tput and BLER vs. Time"     : ";LTE;Time Grids;Physical Grid;LTE L1 Tput and BLER vs. Time",
    "LTE UL Avg BlerTputPwr Vs Time"    : ";LTE;Time Grids;Physical Grid;LTE UL Avg BlerTputPwr Vs Time",
    "LTE PUSCH BLER vs. Subframe"       : ";LTE;Time Grids;Physical Grid;LTE PUSCH BLER vs. Subframe",
    "LTE UL MCS and RB vs. Time"        : ";LTE;Time Grids;Physical Grid;LTE UL MCS and RB vs. Time",
    "LTE Serving Cell Meas vs. Time"    : ";LTE;Time Grids;Physical Grid;LTE Serving Cell Meas vs. Time",
    "LTE Inst Meas RSRP vs. Time"       : ";LTE;Time Grids;Physical Grid;Serving & Neighbor Measurement;LTE Inst Meas RSRP vs. Time"
}


def read_config(configfile=None):
    global config_templates
    if configfile == None:
        cur_dir = os.getcwd()
        configfile = os.path.join(cur_dir, '4g_parser.cfg')
    with open(configfile) as f:
        for line in f:
            if line.find(':') != -1 and line[0] != '#':
                temp = line.split(':')
                config_templates[temp[0].rstrip()] = temp[1].rstrip()


def is_num(num):
    """Check if a string is a number"""
    try:
        float(num)
        return True
    except ValueError:
        return False

def name_out_file (analyzer_name):
    "Output file name after running analyzer"
    new_name = analyzer_name.replace(".", "_") # remove dot after 'vs.'
    new_name = new_name.replace(" ", "_")
    new_name = new_name + ".txt"
    return  new_name

def path_to_out_folder():
    """path to output folder after running analyzer"""
    current_dir = os.getcwd()
    return os.path.join(current_dir, "QCAT_output")  # current path order

def path_to_outfile (analyzer_name):
    """path to output file after running analyzer"""
    current_dir = os.getcwd()
    return os.path.join(current_dir, "QCAT_output", name_out_file(analyzer_name)) # current path order


# PART 1: Analysis with QCAT templates

def is_file_exist(file_path):
    if os.path.exists(file_path):
        return True
    return False

def change_file_name(log_path, exported_path):
    """Change exported file name from 'analyzer'.txt to 'log_analyser.txt'"""
    if not is_file_exist(exported_path):
        return False

    reformat_path = log_path.replace('\\', '/')
    if reformat_path.find('/'):
        split_log_path = reformat_path.split('/')
        log_name = split_log_path[-1].split('.')[0]  # remove file extension, Ex. '.txt'

    exported_path = exported_path.replace('\\', '/')
    if exported_path.find('/'):
        cur_dir = os.getcwd().replace('\\', '/')
        short_dir = exported_path.split(cur_dir)      # Get short path from current directory
        split_exported_path = short_dir[1].split('/')
        exported_name = split_exported_path[-1]       # Get file name

    if log_name and exported_name:
        new_path = os.path.join(*split_exported_path[:-1], log_name + '_' + exported_name)
        if not is_file_exist(new_path):
            os.rename(exported_path, new_path)
        return True
    return False


def run_analyzer(log_path, analyzer_name):
    """run annalyzer by its name"""
    try:
        analyzer         = templates[analyzer_name]
        parsed_folder_path = path_to_out_folder()
        qcat_export_text(log_path, analyzer, parsed_folder_path)
    except:
        print("Error: No grid name \'%s\'!" % analyzer_name)

def run_config_analyzer(log_path, analyzer_name):
    """run annalyzer by its name extract from config file"""
    global config_templates
    read_config()
    try:
        analyzer         = templates[analyzer_name]
        parsed_folder_path = path_to_out_folder()
        qcat_export_text(log_path, analyzer, parsed_folder_path)
    except:
        print("Error: No grid \'%s\' in config file!" % analyzer_name)

def extract_pci():
    """Extract physical cell ID from analyzer 'cell measure'"""
    analyzer_name = "LTE Serving Cell Meas vs. Time"
    cur_dir = os.getcwd()
    log_path = os.path.join(cur_dir, "QCAT_input", "FTP DL_eHI04623_MS1_m06090009.dlf")
    print("Running PCI analyzer...")
    run_analyzer(log_path, analyzer_name)

    re_cell_id = re.compile(r"Cell\s(\d+)\sEARFCN")
    meas_file_path = path_to_outfile(analyzer_name)
    cell_id = None

    print("Extracting cell ID...")
    with open(meas_file_path, 'r') as f:
        for line in f:
            cell_id = re_cell_id.search(line)
            if cell_id != None:
                break
    return cell_id.group(1)

def extract_pci_rsrp(log_path=None):
    """Extract physical cell ID, EARFCN, RSRP from analyzer 'cell measure'"""
    analyzer_name = "LTE Serving Cell Meas vs. Time"
    cur_dir = os.getcwd()
    if log_path == None:
        log_path = os.path.join(cur_dir, "QCAT_input", "FTP DL_eHI04623_MS1_m06090009.dlf")
    print("Running PCI RSRP analyzer...")
    run_analyzer(log_path, analyzer_name)

    re_cell_id = re.compile(r"Cell\s(\d+)\sEARFCN\s(\d+)\sInst\sMeasured\sRSRP")

    meas_file_path = path_to_outfile(analyzer_name)
    cell_id = None
    # earfcn  = None
    total_rsrp = 0
    rsrp_count = 0

    #TODO: if there are more than 2 serving cells in the log?
    print("Extracting cell ID, RSRP...")
    with open(meas_file_path, 'r') as f:
        for line in f:
            if cell_id != None:
                meas = line.split(',')
                if len(meas) > 5 and meas[6] != '':
                    total_rsrp += float(meas[6])
                    rsrp_count += 1
            else:
                cell_inf = re_cell_id.search(line)
                if cell_inf != None:
                    cell_id = cell_inf.group(1)
                    earfcn = cell_inf.group(2)

    # Change exprorted file name
    change_file_name(log_path, meas_file_path)

    if rsrp_count != 0:
        avg_rsrp = ceil(total_rsrp / rsrp_count * 10) / 10.0
    if cell_inf != None:
        return cell_id, earfcn, avg_rsrp
    return None

def extract_dl_rb(log_path=None):
    """Extract DL Resource Block number"""
    analyzer_name = "LTE Pdsch Stat Indication vs. Time"
    cur_dir = os.getcwd()
    if log_path == None:
        log_path = os.path.join(cur_dir, "QCAT_input", "FTP DL_eHI04623_MS1_m06090009.dlf")
    print("Running DL Resource Block number analyzer...")
    run_analyzer(log_path, analyzer_name)
    stat_file_path = path_to_outfile(analyzer_name)

    total_rb = 0
    rb_count  = 0

    print("Extracting Downlink CQI RI and MCS...")
    with open(stat_file_path, 'r') as f:
        for line in f:
            stat = line.split(',')
            if len(stat) > 5:
                if stat[3] != '':
                    total_rb += int(stat[3])
                    rb_count += 1

    # Change exprorted file name
    change_file_name(log_path, stat_file_path)

    if rb_count != 0:
        avg_rb = ceil(total_rb / rb_count)
        return avg_rb
    else:
        return None

def extract_cqi_ri_mcs(log_path=None):
    """Extract DL Channel Quality Indicator, Rank Indicator and MCS index"""
    analyzer_name = "LTE L1 CQI RI and MCS vs. Time"
    cur_dir = os.getcwd()
    if log_path == None:
        log_path = os.path.join(cur_dir, "QCAT_input", "FTP DL_eHI04623_MS1_m06090009.dlf")
    print("Running DL CQI RI and MCS analyzer...")
    run_analyzer(log_path, analyzer_name)
    qual_file_path = path_to_outfile(analyzer_name)

    total_cqi = 0
    total_ri  = 0
    total_mcs = 0
    cqi_count = 0
    ri_count  = 0
    mcs_count = 0

    print("Extracting Downlink CQI RI and MCS...")
    with open(qual_file_path, 'r') as f:
        for line in f:
            qual = line.split(',')
            if len(qual) > 5:
                if is_num(qual[2]):
                    total_cqi += int(qual[2])
                    cqi_count += 1

                if is_num(qual[1]):
                    total_ri += int(qual[1])
                    ri_count += 1

                if is_num(qual[4]):
                    total_mcs += int(qual[4])
                    mcs_count += 1

    # Change exprorted file name
    change_file_name(log_path, qual_file_path)

    if mcs_count != 0:
        avg_mcs = ceil(total_mcs / mcs_count)
        if cqi_count != 0:
            avg_cqi = ceil(total_cqi / cqi_count)
            if ri_count != 0:
                avg_ri = ceil(total_ri / ri_count)
                return avg_cqi, avg_ri, avg_mcs
    else:
        return None

def extract_ul_rb_mcs(log_path=None):
    """Extract Uplink Average Resource Block number and Average MCS index"""
    analyzer_name = "LTE UL MCS and RB vs. Time"
    cur_dir = os.getcwd()
    if log_path == None:
        log_path = os.path.join(cur_dir, "QCAT_input", "FTP DL_eHI04623_MS1_m06090009.dlf")
    print("Running UL MCS and RB analyzer...")
    run_analyzer(log_path, analyzer_name)
    grant_file_path = path_to_outfile(analyzer_name)

    # re_grant = re.compile("\d{2}:\d{2}:\d{2}\.\d{3}\t(\d+)\t(\d+)")
    re_grant = re.compile("[^,]+,(\d+),(\d+)")
    total_rb_num  = 0
    total_mcs_num = 0
    rb_num_count  = 0
    mcs_num_count = 0

    print("Extracting UL MCS and RB number...")
    with open(grant_file_path, 'r') as f:
        for line in f:
            grant = re_grant.search(line)
            if grant != None:
                total_rb_num  += int(grant.group(1))
                rb_num_count  += 1

                total_mcs_num += int(grant.group(2))
                mcs_num_count += 1

    # Change exprorted file name
    change_file_name(log_path, grant_file_path)

    if rb_num_count != 0:
        avg_rb_num = total_rb_num / rb_num_count
        if mcs_num_count != 0:
            avg_mcs_num = total_mcs_num / mcs_num_count
            return int(avg_rb_num), int(avg_mcs_num)
    else:
        return None

def extract_dl_bler_tput(log_path=None):
    """Extract Downlink Average BLER and Average throughput"""
    analyzer_name = "LTE L1 Tput and BLER vs. Time"
    cur_dir = os.getcwd()
    if log_path == None:
        log_path = os.path.join(cur_dir, "QCAT_input", "FTP DL_eHI04623_MS1_m06090009.dlf")
    print("Running DL Tput and BLER analyzer...")
    run_analyzer(log_path, analyzer_name)
    qual_file_path = path_to_outfile(analyzer_name)

    total_dl_tput = 0
    total_bler    = 0
    dl_tput_count = 0
    bler_count    = 0

    print("Extracting Downlink Throughput and BLER...")
    with open(qual_file_path, 'r') as f:
        for line in f:
            qual = line.split(',')
            if len(qual) > 5:
                if qual[2] != '':
                    total_dl_tput  += float(qual[2])
                    dl_tput_count  += 1

                if qual[5] != '':
                    total_bler += float(qual[5])
                    bler_count += 1

    # Change exprorted file name
    change_file_name(log_path, qual_file_path)

    if dl_tput_count != 0:
        avg_dl_tput = ceil(total_dl_tput / dl_tput_count / 1024 * 10) / 10.0
        if bler_count != 0:
            avg_bler = ceil(total_bler / bler_count * 100) / 100.0
            return avg_bler, avg_dl_tput
    else:
        return None

def extract_dl_tput(log_path=None):
    """Extract Uplink Average PHY, RLC, PDCP throughput"""
    analyzer_name = "LTE DL Throughput vs. Time"
    cur_dir = os.getcwd()
    if log_path == None:
        log_path = os.path.join(cur_dir, "QCAT_input", "FTP DL_eHI04623_MS1_m06090009.dlf")
    print("Running UL Tput analyzer...")
    run_analyzer(log_path, analyzer_name)
    qual_file_path = path_to_outfile(analyzer_name)

    phy_dl_tput     = 0
    rlc_dl_tput     = 0
    pdcp_dl_tput    = 0
    phy_tput_count  = 0
    rlc_tput_count  = 0
    pdcp_tput_count = 0

    print("Extracting Uplink Throughput...")
    with open(qual_file_path, 'r') as f:
        for line in f:
            qual = line.split(',')
            if len(qual) > 5:
                if qual[2] != '':
                    phy_dl_tput     += float(qual[2])
                    phy_tput_count  += 1

                if qual[13] != '':
                    rlc_dl_tput     += float(qual[13])
                    rlc_tput_count  += 1

                if qual[14] != '':
                    pdcp_dl_tput    += float(qual[14])
                    pdcp_tput_count += 1

    # Change exprorted file name
    change_file_name(log_path, qual_file_path)

    if pdcp_tput_count != 0: #TODO: if phy_count > 0 but rlc_count or pdcp_count = 0?
        avg_phy_tput  = ceil(phy_dl_tput / phy_tput_count / 1024 * 10) / 10.0
        avg_rlc_tput  = ceil(rlc_dl_tput / rlc_tput_count / 1024 * 10) / 10.0
        avg_pdcp_tput = ceil(pdcp_dl_tput / pdcp_tput_count / 1024 * 10) / 10.0
        return avg_phy_tput, avg_rlc_tput, avg_pdcp_tput
    else:
        return None

def extract_ul_tput(log_path=None):
    """Extract Uplink Average PHY, RLC, PDCP throughput"""
    analyzer_name = "LTE UL Throughput vs. Time"
    cur_dir = os.getcwd()
    if log_path == None:
        log_path = os.path.join(cur_dir, "QCAT_input", "FTP DL_eHI04623_MS1_m06090009.dlf")
    print("Running UL Tput analyzer...")
    run_analyzer(log_path, analyzer_name)
    qual_file_path = path_to_outfile(analyzer_name)

    phy_ul_tput     = 0
    rlc_ul_tput     = 0
    pdcp_ul_tput    = 0
    phy_tput_count  = 0
    rlc_tput_count  = 0
    pdcp_tput_count = 0

    print("Extracting Uplink Throughput...")
    with open(qual_file_path, 'r') as f:
        for line in f:
            qual = line.split(',')
            if len(qual) > 5:
                if qual[2] != '':
                    phy_ul_tput     += float(qual[2])
                    phy_tput_count  += 1

                if qual[3] != '':
                    rlc_ul_tput     += float(qual[3])
                    rlc_tput_count  += 1

                if qual[4] != '':
                    pdcp_ul_tput    += float(qual[4])
                    pdcp_tput_count += 1

    # Change exprorted file name
    change_file_name(log_path, qual_file_path)

    if pdcp_tput_count != 0: #TODO: if phy_count > 0 but rlc_count or pdcp_count = 0?
        avg_phy_tput  = ceil(phy_ul_tput / phy_tput_count / 1024 * 10) / 10.0
        avg_rlc_tput  = ceil(rlc_ul_tput / rlc_tput_count / 1024 * 10) / 10.0
        avg_pdcp_tput = ceil(pdcp_ul_tput / pdcp_tput_count / 1024 * 10) / 10.0
        return avg_phy_tput, avg_rlc_tput, avg_pdcp_tput
    else:
        return None

def extract_ul_pwr_bler_tput(log_path=None):
    """Extract Tx Power, Average BLER, and Average PHY Uplink throughput"""
    analyzer_name = "LTE UL Avg BlerTputPwr Vs Time"
    cur_dir = os.getcwd()
    if log_path == None:
        log_path = os.path.join(cur_dir, "QCAT_input", "FTP DL_eHI04623_MS1_m06090009.dlf")
    print("Running BLER, Tx Power, Throughput analyzer...")
    run_analyzer(log_path, analyzer_name)
    qual_file_path = path_to_outfile(analyzer_name)

    # re_qual = re.compile("[^,]+,\d+,\w+,\d+,(-\d+),(\d+\.*\d*),(\d+\.*\d*)")
    total_ul_tput = 0
    total_bler    = 0
    ul_tput_count = 0
    bler_count    = 0
    total_tx_pwr  = 0
    tx_pwr_count  = 0

    print("Extracting Tx power, UL BLER and Throughput...")
    with open(qual_file_path, 'r') as f:
        for line in f:
            qual = line.split(',')
            if len(qual) > 10:
                if is_num(qual[9]):
                    total_ul_tput  += float(qual[9])
                    ul_tput_count  += 1

                if is_num(qual[8]):
                    total_bler += float(qual[8])
                    bler_count += 1

                if is_num(qual[7]):
                    total_tx_pwr += float(qual[7])
                    tx_pwr_count += 1

    # Change exprorted file name
    change_file_name(log_path, qual_file_path)

    if ul_tput_count != 0:
        avg_up_tput = ceil(total_ul_tput / ul_tput_count * 10) / 10.0
        if bler_count != 0:
            avg_bler = ceil(total_bler / bler_count * 100) / 100.0
            if tx_pwr_count != 0:
                avg_tx_pwr = ceil(total_tx_pwr / tx_pwr_count * 1) / 1.0
                return avg_tx_pwr,  avg_bler, avg_up_tput
    else:
        return None

def test_export():
    """Just for a fool test"""
    cur_dir = os.getcwd()
    log_path = os.path.join(cur_dir, "QCAT_input", "FTP DL_eHI04623_MS1_m06090009.dlf")
    run_analyzer(log_path, "LTE Serving Cell Meas vs. Time")

def ul_summary():
    """Summarizing uplink resource and quality"""
    pci           = extract_pci()
    rb_num, mcs   = extract_ul_rb_mcs()
    ul_tput, bler = extract_dl_bler_tput()

    cur_dir = os.getcwd()
    log_path = os.path.join(cur_dir, "uplink_summary.txt")
    with open(log_path, 'w') as f:
        f.write(
            "Serving Physical Cell ID: " + str(pci) + "\n"
            + "UL avg PHY throughput: " + str(ul_tput) + "(Mbps)\n"
            + "Avg RBs: " + str(rb_num) + "\n"
            + "Avg MCS: " + str(mcs) + "\n"
            + "Avg Uplink BLER: " + str(bler) + "%\n"
        )
    print("Finished exporting UL summary!")

def log_summary(log_path):
    """Summarize info in log"""
    pci, earfcn, rsrp                      = extract_pci_rsrp(log_path)

    # Downlink
    dl_phy_tput, dl_rlc_tput, dl_pdcp_tput = extract_dl_tput(log_path)
    dl_rb                                  = extract_dl_rb(log_path)
    cqi, ri, dl_mcs                        = extract_cqi_ri_mcs(log_path)
    dl_bler, dl_tput                       = extract_dl_bler_tput(log_path)

    # Uplink
    ul_phy_tput, ul_rlc_tput, ul_pdcp_tput = extract_ul_tput(log_path)
    ul_rb, ul_mcs                          = extract_ul_rb_mcs(log_path)
    tx_pwr, ul_bler, ul_tput               = extract_ul_pwr_bler_tput(log_path)

    cur_dir = os.getcwd()
    log_path = os.path.join(cur_dir, "log_summary.txt")
    with open(log_path, 'w') as f:
        f.write(
            "Serving Physical Cell ID: " + str(pci) + "\n"
            + "RSRP Serving PCI: " + str(rsrp) + "\n"
            + "EARFCN: " + str(earfcn) + "\n"
            + "\n#DOWNLINK" + "\n"
            + "DL avg PHY throughput (Mbps): " + str(dl_phy_tput) + "\n"
            + "DL avg RLC throughput (Mbps): " + str(dl_rlc_tput) + "\n"
            + "DL avg PDCP throughput (Mbps): " + str(dl_pdcp_tput) + "\n"
            + "Avg RBs: " + str(dl_rb) + "\n"
            + "Avg CQI: " + str(cqi) + "\n"
            + "Avg MCS: " + str(dl_mcs) + "\n"
            + "Avg Dlink BLER: " + str(dl_bler) + "%\n"
            + "Avg RI: " + str(ri) + "\n"
            + "\n#UPLINK" + "\n"
            + "UL avg PHY throughput (Mbps): " + str(ul_phy_tput) + "\n"
            + "UL avg RLC throughput (Mbps): " + str(ul_rlc_tput) + "\n"
            + "UL avg PDCP throughput (Mbps): " + str(ul_pdcp_tput) + "\n"
            + "Avg RBs: " + str(ul_rb) + "\n"
            + "Avg MCS: " + str(ul_mcs) + "\n"
            + "Avg Uplink BLER: " + str(ul_bler) + "%\n"
            + "Avg PUSCH Actual Tx Power (dBm): " + str(tx_pwr) + "\n"
        )
    # print(dl_tput, ul_tput)
    print("Finished exporting log summary!")


# PART 2: Signaling messages
from QCAT_Lib.QCAT_Basic import qcat_parse_log
def read_2nd_config(configfile=None):
    """Read configuration file type 2"""
    types_long = []
    types_short = []
    re_LOG_type = re.compile('(0x\w{4})')
    if configfile == None:
        return
    with open(configfile) as f:
        for line in f:
            short = re_LOG_type.search(line)
            if short:
                types_short.append(int(short.group(1), 16))
                types_long.append(line)

    return types_short, types_long

def concat_signaling(configfile, log_path, output_path):
    """Export all signaling message to 1 file"""
    if log_path == None:
        print("Error: Missing log file!!!")
        return
    else:
        reformat_path = log_path.replace('\\', '/')
        if reformat_path.find('/'):
            split_log_path = reformat_path.split('/')
            log_name = split_log_path[-1].split('.')[0]  # remove file extension, Ex. '.txt'
    path_to_file = os.path.join(output_path, log_name + '_signaling.txt')

    # Empty existed signaling file for new turn
    if is_file_exist(path_to_file):
        with open(path_to_file, 'w') as f:
            f.truncate(0)

    # Detect extension of input log
    extension = os.path.splitext(log_path)[-1]

    # Handle log in text type
    if extension in ['.txt', '.log']:
        type_short, type_long = read_2nd_config(configfile)
        re_pkt_type = re.compile('(0x\w{4})')
        flag = False  # Flag: True if detecting signaling packet
        with open(log_path, 'r') as f:
            for line in f:
                pkt_type = re_pkt_type.search(line)
                if pkt_type != None: # Found 1st line of a packet
                    a = int(pkt_type.group(1), 16)
                    if int(pkt_type.group(1), 16) in type_short: # Check if signaling packet
                        with open(path_to_file, 'a') as outfile:
                            outfile.write(line)
                        flag = True
                    else: # Not a signaling packet
                        flag = False
                        continue
                elif flag == True: # Lines in signaling packet
                    with open(path_to_file, 'a') as outfile:
                        outfile.write(line)

    # Handle log in raw type
    elif extension in ['.qxdm', '.dlf', '.isf']:
        type_short, type_long = read_2nd_config(configfile)
        qcat_parse_log(log_path, type_short, path_to_file)




# test_export()
config_f = "D:\\ng_analysis\\tool_analysis_QCAT\\4g_signaling.cfg"
raw_log = "D:\\ng_analysis\\tool_analysis_QCAT\\QCAT_input\\05-22.16-18.isf"
# raw_log = "D:\\ng_analysis\\tool_analysis_QCAT\\QCAT_output\\data15_02_35.txt"
out_path = "D:\\ng_analysis\\tool_analysis_QCAT\\\\QCAT_output\\"
# print(extract_pci_rsrp(raw_log))
# print(extract_ul_rb_mcs(raw_log))
# print(extract_dl_tput())
# print(extract_ul_pwr_bler_tput(raw_log))
# print(extract_cqi_ri_mcs("05-22.16-18.isf"))
conf = 'D:/ng_analysis/tool_analysis_QCAT/4g_signaling.cfg'
lo  = ['D:/ng_analysis/tool_analysis_QCAT/QCAT_output/test_02_10.txt']


# ul_summary()
# log_summary("05-22.16-18.isf")

# analyzer_name = "LTE Serving Cell Meas vs. Time"
# cur_dir = os.getcwd()

# concat_signaling(config_f, raw_log, out_path)




