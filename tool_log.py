from __future__ import print_function, division

import os
import re
import logging

from math import ceil
from QCAT_Lib.QCAT_Basic import qcat_export_text


outfiles = {
    "LTE L1 RI Modulation Type Stats"   : "LTE_L1_RI_Modulation_Type_Stats.txt",
    "LTE PDCP DL Stats Summary"         : "LTE_PDCP_DL_Stats_Summary.txt",
    "LTE PDCP UL Stats Summary"         : "LTE_PDCP_UL_Stats_Summary.txt",
    "LTE DL Throughput vs. Time"        : "LTE_DL_Throughput_vs_Time.txt",
    "LTE UL Throughput vs. Time"        : "LTE_UL_Throughput_vs_Time.txt",
    "LTE DCI Info vs. Time"             : "LTE_DCI_Info_vs_Time.txt",
    "LTE DL BLER Vs Subfr"              : "LTE_DL_BLER_Vs_Subfr.txt",
    "LTE L1 Tput and BLER vs. Time"     : "LTE_L1_Tput_and_BLER_vs_Time.txt",
    "LTE PUSCH BLER vs. Subframe"       : "LTE_PUSCH_BLER_vs_Subframe.txt",
    "LTE UL MCS and RB vs. Time"        : "LTE_UL_MCS_and_RB_vs_Time.txt"
}

templates = {
    "LTE L1 RI Modulation Type Stats"   : ";LTE;Summary;LTE L1 RI Modulation Type Stats",
    "LTE PDCP DL Stats Summary"         : ";LTE;Summary;LTE PDCP Summary;LTE PDCP DL Stats Summary",
    "LTE PDCP UL Stats Summary"         : ";LTE;Summary;LTE PDCP Summary;LTE PDCP UL Stats Summary",
    "LTE DL Throughput vs. Time"        : ";LTE;Time Grids;Phy/RLC/PDCP Grids;LTE DL Throughput vs. Time",
    "LTE UL Throughput vs. Time"        : ";LTE;Time Grids;Phy/RLC/PDCP Grids;LTE UL Throughput vs. Time",
    "LTE DCI Info vs. Time"             : ";LTE;Time Grids;Physical Grid;LTE DCI Info vs. Time",
    "LTE DL BLER Vs Subfr"              : ";LTE;Time Grids;Physical Grid;LTE DL BLER Vs Subfr",
    "LTE L1 Tput and BLER vs. Time"     : ";LTE;Time Grids;Physical Grid;LTE L1 Tput and BLER vs. Time",
    "LTE UL Avg BlerTputPwr Vs Time"    : ";LTE;Time Grids;Physical Grid;LTE UL Avg BlerTputPwr Vs Time",
    "LTE PUSCH BLER vs. Subframe"       : ";LTE;Time Grids;Physical Grid;LTE PUSCH BLER vs. Subframe",
    "LTE UL MCS and RB vs. Time"        : ";LTE;Time Grids;Physical Grid;LTE UL MCS and RB vs. Time",
    "LTE Serving Cell Meas vs. Time"    : ";LTE;Time Grids;Physical Grid;LTE Serving Cell Meas vs. Time",
    "LTE Inst Meas RSRP vs. Time"       : ";LTE;Time Grids;Physical Grid;Serving & Neighbor Measurement;LTE Inst Meas RSRP vs. Time"
}

def name_out_file (analyzer_name):
    "Output file name after running analyzer"
    new_name = analyzer_name.replace(".", "_") # remove dot after 'vs.'
    new_name = new_name.replace(" ", "_")
    new_name = new_name + ".txt"
    return  new_name

def path_to_out_folder():
    """path to output folder after running analyzer"""
    current_dir = os.getcwd()
    return os.path.join(current_dir, "Test", "QCAT output")  # current path order

def path_to_outfile (analyzer_name):
    """path to output file after running analyzer"""
    current_dir = os.getcwd()
    return os.path.join(current_dir, "Test", "QCAT output", name_out_file(analyzer_name)) # current path order

def run_analyzer(log_path, analyzer_name):
    """run annalyzer by its name"""
    analyzer         = templates[analyzer_name]
    parsed_folder_path = path_to_out_folder()
    qcat_export_text(log_path, analyzer, parsed_folder_path)

def extract_pci():
    """Extract physical cell ID from analyzer 'cell measure'"""
    analyzer_name = "LTE Serving Cell Meas vs. Time"
    cur_dir = os.getcwd()
    log_path = os.path.join(cur_dir, "Test", "QCAT input", "FTP DL_eHI04623_MS1_m06090009.dlf")
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

def extract_pci_rsrp():
    """Extract physical cell ID, EARFCN, RSRP from analyzer 'cell measure'"""
    analyzer_name = "LTE Serving Cell Meas vs. Time"
    cur_dir = os.getcwd()
    log_path = os.path.join(cur_dir, "Test", "QCAT input", "FTP DL_eHI04623_MS1_m06090009.dlf")
    print("Running PCI RSRP analyzer...")
    run_analyzer(log_path, analyzer_name)

    re_cell_id = re.compile(r"Cell\s(\d+)\sEARFCN\s(\d+)\sInst\sMeasured\sRSRP")
    # "Cell 104 EARFCN 1750 Inst Measured RSRP"
    re_rsrp    = re.compile(r"[^\t]+\t\d*\.*\d*\t-\d*\.*\d*\t-\d*\.*\d*\t-\d*\.*\d*\t-\d*\.*\d*\t(-\d+\.*\d*)")

    meas_file_path = path_to_outfile(analyzer_name)
    cell_id = None
    # earfcn  = None
    total_rsrp = 0
    rsrp_count = 0

    print("Extracting cell ID, RSRP...")
    with open(meas_file_path, 'r') as f:
        for line in f:
            if cell_id != None:
                meas = re_rsrp.search(line)
                if meas != None:
                    total_rsrp += float(meas.group(1))
                    a = meas.group(1)
                    rsrp_count += 1
            else:
                cell_inf = re_cell_id.search(line)
                if cell_inf != None:
                    cell_id = cell_inf.group(1)
                    earfcn = cell_inf.group(2)

    if rsrp_count != 0:
        avg_rsrp = ceil(total_rsrp / rsrp_count / 1024 * 10) / 10.0
    if cell_inf != None:
        return cell_id, earfcn, avg_rsrp
    return None

def extract_ul_rb_mcs():
    """Extract Uplink Average Resource Block number and Average MCS index"""
    analyzer_name = "LTE UL MCS and RB vs. Time"
    cur_dir = os.getcwd()
    log_path = os.path.join(cur_dir, "Test", "QCAT input", "FTP DL_eHI04623_MS1_m06090009.dlf")
    print("Running UL MCS and RB analyzer...")
    run_analyzer(log_path, analyzer_name)
    grant_file_path = path_to_outfile(analyzer_name)

    # re_grant = re.compile("\d{2}:\d{2}:\d{2}\.\d{3}\t(\d+)\t(\d+)")
    re_grant = re.compile("[^\t]+\t(\d+)\t(\d+)")
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

    if rb_num_count != 0:
        avg_rb_num = total_rb_num / rb_num_count
        if mcs_num_count != 0:
            avg_mcs_num = total_mcs_num / mcs_num_count
            return int(avg_rb_num), int(avg_mcs_num)
    else:
        return None

def extract_ul_bler_tput():
    """Extract Uplink Average throughput and Average BLER"""
    analyzer_name = "LTE L1 Tput and BLER vs. Time"
    cur_dir = os.getcwd()
    log_path = os.path.join(cur_dir, "Test", "QCAT input", "FTP DL_eHI04623_MS1_m06090009.dlf")
    print("Running Tput and BLER analyzer...")
    run_analyzer(log_path, analyzer_name)
    qual_file_path = path_to_outfile(analyzer_name)

    re_qual = re.compile("[^\t]+\t\d+\.*\d*\t(\d+\.*\d*)\t\d+\.*\d*\t\d+\.*\d*\t(\d+\.*\d*)")
    total_ul_tput = 0
    total_bler    = 0
    ul_tput_count = 0
    bler_count    = 0

    print("Extracting Uplink Throughput and BLER...")
    with open(qual_file_path, 'r') as f:
        for line in f:
            qual = re_qual.search(line)
            if qual != None:
                total_ul_tput  += float(qual.group(1))
                ul_tput_count  += 1

                total_bler += float(qual.group(2))
                bler_count += 1

    if ul_tput_count != 0:
        avg_up_tput = ceil(total_ul_tput / ul_tput_count / 1024 * 10) / 10.0
        if bler_count != 0:
            avg_bler = ceil(total_bler / bler_count * 100) / 100.0
            return avg_up_tput, avg_bler
    else:
        return None

def extract_ul_bler_tput_pwr():
    """Extract Tx Power, Average BLER, and Uplink Average throughput"""
    analyzer_name = "LTE UL Avg BlerTputPwr Vs Time"
    cur_dir = os.getcwd()
    log_path = os.path.join(cur_dir, "Test", "QCAT input", "FTP DL_eHI04623_MS1_m06090009.dlf")
    print("Running BLER, Tx Power, Throughput analyzer...")
    run_analyzer(log_path, analyzer_name)
    qual_file_path = path_to_outfile(analyzer_name)

    re_qual = re.compile("[^\t]+\t\d+\t\w+\t\d+\t(-\d+)\t(\d+\.*\d*)\t(\d+\.*\d*)")
    total_ul_tput = 0
    total_bler    = 0
    ul_tput_count = 0
    bler_count    = 0
    total_tx_pwr  = 0
    tx_pwr_count  = 0

    print("Extracting Tx power, UL BLER and Throughput...")
    with open(qual_file_path, 'r') as f:
        for line in f:
            qual = re_qual.search(line)
            if qual != None:
                total_ul_tput  += float(qual.group(3))
                ul_tput_count  += 1

                total_bler += float(qual.group(2))
                bler_count += 1

                total_tx_pwr += int(qual.group(1))
                tx_pwr_count += 1

    if ul_tput_count != 0:
        avg_up_tput = ceil(total_ul_tput / ul_tput_count / 1024 * 10) / 10.0
        if bler_count != 0:
            avg_bler = ceil(total_bler / bler_count * 100) / 100.0
            if tx_pwr_count != 0:
                avg_tx_pwr = int(ceil(total_tx_pwr / tx_pwr_count))
                return avg_tx_pwr,  avg_bler, avg_up_tput
    else:
        return None



def test_export():
    """Just for a fool test"""
    cur_dir = os.getcwd()
    log_path = os.path.join(cur_dir, "Test", "QCAT input", "FTP DL_eHI04623_MS1_m06090009.dlf")
    run_analyzer(log_path, "LTE Serving Cell Meas vs. Time")

def ul_summary():
    """Summarizing uplink resource and quality"""
    pci           = extract_pci()
    rb_num, mcs   = extract_ul_rb_mcs()
    ul_tput, bler = extract_ul_bler_tput()

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


# test_export()
print(extract_pci_rsrp())
# print(extract_ul_rb_mcs())
# print(extract_ul_bler_tput())

# ul_summary()

# analyzer_name = "LTE Serving Cell Meas vs. Time"
# cur_dir = os.getcwd()
# log_path = os.path.join(cur_dir, "Test", "QCAT input", "FTP DL_eHI04623_MS1_m06090009.dlf")
# print("Running PCI RSRP analyzer...")
# run_analyzer(log_path, analyzer_name)

# re_cell_id = re.compile(r"Cell\s(\d+)\sEARFCN\s(\d+)\sInst\sMeasured\sRSRP")
# # "Cell 104 EARFCN 1750 Inst Measured RSRP"
# re_rsrp    = re.compile(r"[^\t]+\t\d*\.*\d*\t\d*\.*\d*\t\d*\.*\d*\t\d*\.*\d*\t\d*\.*\d*\t(\d+\.*\d*)")
# meas_file_path = path_to_outfile(analyzer_name)
# cell_id = None
# # earfcn  = None
# total_rsrp = 0
# rsrp_count = 0
#
# print("Extracting cell ID, RSRP...")
# with open(meas_file_path, 'r') as f:
#     for line in f:
#         ak = re_cell_id.search(line)
#         if ak:
#             print(ak.group(1)+" "+ ak.group(2))







