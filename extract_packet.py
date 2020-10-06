from __future__ import print_function, division

import os
import re
import logging

from math import ceil
from QCAT_Lib.QCAT_Basic import qcat_parse_log, qcat_export_grids, qcat_export_all, qcat_get_field

### FUNCTIONS FOR 4G TXT LOG
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


### FUNCTION FOR 5G TXT LOG
def fill_cell_info(stat_line):
    """Extract cell id, rsrp, rsrq"""
    cell_info = stat_line.split('|')
    if len(cell_info) > 18:
        pci = cell_info[2].strip()
        rsrp = float(cell_info[10].strip())
        rsrq = float(cell_info[11].strip())
        return pci, rsrp, rsrq

def fill_freq_info(stat_line):
    """Extract frequency info"""
    freq_info = stat_line.split('|')
    if len(freq_info) > 8:
        dl_arfcn        = freq_info[3].strip()
        ul_arfcn        = freq_info[4].strip()
        dl_carrier_bwth = freq_info[7].strip()
        ul_carrier_bwth = freq_info[8].strip()
        return dl_arfcn, ul_arfcn, dl_carrier_bwth, ul_carrier_bwth

def fill_tx_rb_power(stat_line):
    """Extract number of RBs and tx power on PUSCH"""
    power_ctrl = stat_line.split('|')
    if len(power_ctrl) > 40:
        pusch_pwr = float(power_ctrl[18].strip())
        num_rb    = float(power_ctrl[11].strip())
        return num_rb, pusch_pwr

def fill_ul_mcs(stat_line):
    """Extract MCS on PUSCH"""
    schedule_info = stat_line.split('|')
    if len(schedule_info) > 40:
        mcs = float(schedule_info[26].strip())
        return mcs

def fill_dl_mcs_rb(stat_line):
    """Extract DL MCS and RBs"""
    schedule_info = stat_line.split('|')
    if len(schedule_info) > 60:
        mcs = int(schedule_info[18].strip())
        rb  = int(schedule_info[45].strip())
        return mcs, rb

def fill_pdsch_stat(stat_line):
    """Extract RLC UL status for retrieve throughput info"""
    dl_stat = stat_line.split('|')
    if len(dl_stat) > 13:
        num_slot_elapsed = int(dl_stat[3].strip())
        # num_pdsch_decode = int(dl_stat[4].strip())
        num_crc_pass_tb  = int(dl_stat[5].strip())
        num_crc_fail_tb  = int(dl_stat[6].strip())
        # num_re_tx        = int(dl_stat[7].strip())
        # ack_as_nack      = int(dl_stat[8].strip())
        harq_failure     = int(dl_stat[9].strip())
        crc_pass_tb_byte = int(dl_stat[10].strip())
        crc_fail_tb_byte = int(dl_stat[11].strip())
        tb_byte          = int(dl_stat[12].strip())
        # padding_byte     = int(dl_stat[13].strip())

        # return num_slot_elapsed, num_pdsch_decode, num_crc_pass_tb, \
        # num_crc_fail_tb, num_re_tx, ack_as_nack, harq_failure, \
        # crc_pass_tb_byte, crc_fail_tb_byte, tb_byte, padding_byte
        return num_slot_elapsed, num_crc_pass_tb, num_crc_fail_tb, \
        harq_failure, crc_pass_tb_byte, crc_fail_tb_byte, tb_byte

def fill_rlc_dl_stat(stat_line):
    """Extract RLC DL status for retrieve throughput info"""
    dl_stat = stat_line.split('|')
    if len(dl_stat) > 24:
        total_rlc_byte = int(dl_stat[24].strip())
        return total_rlc_byte

def fill_rlc_ul_stat(stat_line):
    """Extract RLC UL status for retrieve throughput info"""
    ul_stat = stat_line.split('|')
    if len(ul_stat) > 18:
        # total_retx_pdu = int(ul_stat[9].strip())
        # total_tx_pdu   = int(ul_stat[11].strip())
        total_tx_byte  = int(ul_stat[12].strip())
        # total_poll_pdu = int(ul_stat[13].strip())

        # return total_retx_pdu, total_tx_pdu, total_tx_byte, total_poll_pdu
        return total_tx_byte

def fill_pdcp_ul_stat(stat_line):
    """Extract PDCP UL status for retrieve throughput info"""
    ul_stat = stat_line.split('|')
    if len(ul_stat) > 20:
        total_rx_byte = int(ul_stat[11].strip())
        return total_rx_byte

def fill_pdcp_dl_stat(stat_line):
    """Extract PDCP DL status for retrieve throughput info"""
    dl_stat = stat_line.split('|')
    if len(dl_stat) > 19:
        pdu_byte_received = int(dl_stat[9].strip())
        return pdu_byte_received

def extract_cell_info(log_file):
    """Extract cell ID, RSRP, RSRQ, Frequencies, Bandwidths, DL RB, UL RB, DL MCS, UL MCS"""
    cell_ids = []
    dl_freqs = []
    ul_freqs = []
    dl_bwths = []
    ul_bwths = []

    total_rsrp   = 0
    total_rsrq   = 0
    total_ul_rb  = 0
    total_dl_rb  = 0
    total_tx_pwr = 0
    total_ul_mcs = 0
    total_dl_mcs = 0

    meas_count   = 0
    tx_count     = 0
    ul_mcs_count = 0
    dl_mcs_count = 0

    ml1_measure_found = False
    tx_power_found    = False
    ul_mcs_found      = False
    dl_mcs_found      = False
    freq_found        = False

    iline_context = 0

    with open(log_file) as f:
        for line in f:
            if line.find('0xB97F') != -1:
                ml1_measure_found = True
            elif line.find('0xB884') != -1:
                tx_power_found = True
            elif line.find('0xB883') != -1:
                ul_mcs_found = True
            elif line.find('0xB887') != -1:
                dl_mcs_found = True
            elif line.find('0xB825') != -1:
                freq_found   = True


            if ml1_measure_found:
                iline_context += 1
                if iline_context == 17:  # Line 17th when found 'ML1 Searcher Measurement' contains measurement info
                    cell_id, rsrp, rsrq = fill_cell_info(line)
                    ml1_measure_found = False
                    iline_context = 0

                    meas_count += 1
                    total_rsrp += float(rsrp)
                    total_rsrq += float(rsrq)

                    if cell_id not in cell_ids:
                        cell_ids.append(cell_id)

            if freq_found:
                iline_context += 1
                if iline_context == 16:
                    dl_arfcn, ul_arfcn, dl_carrier_bwth, ul_carrier_bwth = fill_freq_info(line)
                    if dl_arfcn not in dl_freqs:
                        dl_freqs.append(dl_arfcn)
                    if ul_arfcn not in ul_freqs:
                        ul_freqs.append(ul_arfcn)
                    if dl_carrier_bwth not in dl_bwths:
                        dl_bwths.append(dl_carrier_bwth)
                    if ul_carrier_bwth not in ul_bwths:
                        ul_bwths.append(ul_carrier_bwth)
                if line == '\n':
                    freq_found = False
                    iline_context = 0

            if tx_power_found:
                iline_context += 1
                if iline_context == 16 or iline_context == 17: # Line 16th or 17th when found 'MAC UL Physical Channel Power Control' contains tx_power
                    if line.find('PUSCH') != -1:
                        ul_rb, tx_pwr = fill_tx_rb_power(line)
                        total_ul_rb  += int(ul_rb)
                        total_tx_pwr += float(tx_pwr)
                        tx_count     += 1
                if line == '\n':
                    tx_power_found = False
                    iline_context = 0

            if ul_mcs_found:
                iline_context += 1
                if iline_context == 14 or iline_context == 15: # Line 14th or 15th when found ' Physical Channel Schedule' contains MCS
                    if line.find('PUSCH') != -1: # Only consider PUSCH, skip PUCCH
                        ul_mcs = fill_ul_mcs(line)
                        total_ul_mcs += int(ul_mcs)
                        ul_mcs_count += 1
                if line == '\n':
                    ul_mcs_found = False
                    iline_context = 0

            if dl_mcs_found:
                iline_context += 1
                if iline_context == 15: # Line 15th when found ' MAC PDSCH Status' contains DL MCS and RBs
                    dl_mcs, dl_rb = fill_dl_mcs_rb(line)
                    total_dl_mcs += int(dl_mcs)
                    total_dl_rb        += int(dl_rb)
                    dl_mcs_count += 1
                if line == '\n':
                    dl_mcs_found = False
                    iline_context = 0


    if meas_count != 0:
        avg_rsrp = ceil(total_rsrp / meas_count * 10) / 10.0
        avg_rsrq = ceil(total_rsrq / meas_count * 10) / 10.0

        if tx_count != 0:
            avg_ul_rb  = int(ceil(total_ul_rb / tx_count))
            avg_tx_pwr = ceil(total_tx_pwr / tx_count * 10) / 10.0
            if ul_mcs_count != 0:
                avg_ul_mcs = int(ceil(total_ul_mcs / ul_mcs_count))
                if dl_mcs_count != 0:
                    avg_dl_mcs = int(ceil(total_dl_mcs / dl_mcs_count))
                    avg_dl_rb  = int(ceil(total_dl_rb / dl_mcs_count))
                    return cell_ids, avg_rsrp, avg_rsrq, dl_freqs, ul_freqs, dl_bwths, ul_bwths, \
                           avg_dl_rb, avg_ul_rb, avg_dl_mcs, avg_ul_mcs, avg_tx_pwr


def pdsch_dl_tput(first_stat, last_stat):
    """Calculate number slot elapsed, PHY, MAC DL throughput, DL BLER"""
    first_num_slot_elapsed, first_num_crc_pass, first_num_crc_fail, \
    first_harq_fail, first_crc_pass_byte, first_crc_fail_byte, first_tb_byte \
    = fill_pdsch_stat(first_stat)

    second_num_slot_elapsed, second_num_crc_pass, second_num_crc_fail, \
    second_harq_fail, second_crc_pass_byte, second_crc_fail_byte, second_tb_byte \
    = fill_pdsch_stat(last_stat)

    num_slot_elapsed = second_num_slot_elapsed - first_num_slot_elapsed

    phy_tput_pdsch = ceil((second_tb_byte - first_tb_byte) / 1000 * 8 * 2
                          / num_slot_elapsed * 10) / 10.0
    mac_tput_dl = ceil((second_crc_pass_byte - first_crc_pass_byte) / 1000 * 8 * 2
                       / num_slot_elapsed * 10) / 10.
    total_crc = second_num_crc_pass - second_num_crc_fail + first_num_crc_pass - first_num_crc_fail
    tem_bler = (second_num_crc_fail - first_num_crc_fail) / total_crc  * 100.0
    dl_bler = float("{:.4f}".format(tem_bler))
    tem_retx_bler = (second_harq_fail - first_harq_fail) / total_crc * 100.0
    dl_retx_bler = float("{:.4f}".format(tem_retx_bler))

    return num_slot_elapsed, phy_tput_pdsch, mac_tput_dl, dl_bler, dl_retx_bler

def rlc_ul_tput(first_stat, last_stat, num_slot_elapsed):
    """Calculate RLC UL throughput"""
    first_total_tx_byte = fill_rlc_ul_stat(first_stat)
    last_total_tx_byte = fill_rlc_ul_stat(last_stat)
    rlc_ul_tput = ceil((last_total_tx_byte - first_total_tx_byte) / 1000 * 8 * 2 / num_slot_elapsed * 10) / 10.0
    return rlc_ul_tput

def rlc_dl_tput(first_stat, last_stat, num_slot_elapsed):
    """Calculate RLC UL throughput"""
    first_total_rlc_byte = fill_rlc_dl_stat(first_stat)
    last_total_rlc_byte = fill_rlc_dl_stat(last_stat)
    rlc_dl_tput = ceil((last_total_rlc_byte - first_total_rlc_byte) / 1000 * 8 * 2 / num_slot_elapsed * 10) / 10.0
    return rlc_dl_tput

def pdcp_ul_tput(first_stat, last_stat, num_slot_elapsed):
    """Calculate PDCP UL throughput"""
    first_total_num_rx_byte = fill_pdcp_ul_stat(first_stat)
    last_total_num_rx_byte  = fill_pdcp_ul_stat(last_stat)
    pdcp_ul_tput = ceil((last_total_num_rx_byte - first_total_num_rx_byte) / 1000 * 8 * 2 / num_slot_elapsed * 10) / 10.0
    return pdcp_ul_tput

def pdcp_dl_tput(first_stat, last_stat, num_slot_elapsed):
    """Calculate PDCP UL throughput"""
    first_pdu_byte_received = fill_pdcp_dl_stat(first_stat)
    last_pdu_byte_received = fill_pdcp_dl_stat(last_stat)
    pdcp_dl_tp = ceil((last_pdu_byte_received - first_pdu_byte_received) / 1000 * 8 * 2 / num_slot_elapsed * 10) / 10.0
    return pdcp_dl_tp

def extract_throughput(logtxt):
    """Extract throughput, BLER info from text log"""

    pdsch_found   = False
    rlc_ul_found  = False
    rlc_dl_found  = False
    pdcp_ul_found = False
    pdcp_dl_found = False

    first_pdsch_find   = True
    first_rlc_find     = True
    first_dl_rlc_find  = True
    first_pdcp_ul_find = True
    first_pdcp_dl_find = True

    reason_find   = False

    iline         = 0
    iline_context = 0

    with open(logtxt) as f:
        for line in f:
            iline += 1 # TODO: Check why?
            if pdsch_found or rlc_ul_found or pdcp_ul_found or pdcp_dl_found or rlc_dl_found:
                if pdsch_found:
                    if line == '\n':
                        pdsch_found = False  # End of table
                    else:
                        if iline == iline_context:
                            if first_pdsch_find:
                                first_pdsch_stat = line  # First line in table of PDSCH status
                                first_pdsch_find = False
                            else:
                                last_pdsch_stat = line
                            iline_context += 1
                else:
                    if rlc_ul_found:
                        if line == '\n':
                            rlc_ul_found = False
                        else:
                            if iline == iline_context:
                                if first_rlc_find:
                                    first_rlc_stat = line
                                    first_rlc_find = False
                                else:
                                    last_rlc_stat  = line
                                iline_context += 1
                    else:
                        if pdcp_ul_found:
                            if line == '\n':
                                pdcp_ul_found = False
                            else:
                                if reason_find:
                                    if iline == iline_context:
                                        reason = line.split('=')
                                        if reason[1].strip() == "PERIODIC":
                                            reason_find = False
                                            iline_context = iline + 29
                                        else:
                                            reason_find = False
                                            pdcp_ul_found = False
                                else:
                                    if iline == iline_context:
                                        if first_pdcp_ul_find:
                                            first_pdcp_ul_stat = line
                                            first_pdcp_ul_find = False
                                        else:
                                            last_pdcp_ul_stat = line
                                        iline_context += 1
                        else:
                            if pdcp_dl_found:
                                if line == '\n':
                                    pdcp_dl_found = False
                                else:
                                    if iline == iline_context:
                                        if first_pdcp_dl_find:
                                            first_pdcp_dl_stat = line
                                            first_pdcp_dl_find = False
                                        else:
                                            last_pdcp_dl_stat  = line
                                        iline_context += 1
                            else:
                                if rlc_dl_found:
                                    if line == '\n':
                                        rlc_dl_found = False
                                    else:
                                        if iline == iline_context:
                                            if first_dl_rlc_find:
                                                first_rlc_dl_stat = line
                                                first_dl_rlc_find = False
                                            else:
                                                last_rlc_dl_stat  = line
                                            iline_context += 1
            else:
                if line != '':
                    if line.find(" 0xB888 ") != -1:
                        pdsch_found = True
                        iline_context = iline + 11
                    elif line.find(" 0xB868 ") != -1:
                        rlc_ul_found = True
                        iline_context = iline + 21
                    elif line.find(" 0xB860 ") != -1:
                        pdcp_ul_found = True
                        reason_find   = True
                        iline_context = iline + 4
                    elif line.find(" 0xB842 ") != -1:
                        pdcp_dl_found = True
                        iline_context = iline + 10
                    elif line.find(" 0xB84D ") != -1:
                        rlc_dl_found  = True
                        iline_context = iline + 26

    # TODO: if more than 2 messages same type?
    num_slot_elapsed, phy_tput_pdsch, mac_tput_dl, dl_bler, dl_retx_bler = pdsch_dl_tput(first_pdsch_stat, last_pdsch_stat)
    rlc_u_tput = rlc_ul_tput(first_rlc_stat, last_rlc_stat, num_slot_elapsed)
    rlc_d_tput = rlc_dl_tput(first_rlc_dl_stat, last_rlc_dl_stat, num_slot_elapsed)
    pdcp_ul  = pdcp_ul_tput(first_pdcp_ul_stat, last_pdcp_ul_stat, num_slot_elapsed)
    pdcp_dl  = pdcp_dl_tput(first_pdcp_dl_stat, last_pdcp_dl_stat, num_slot_elapsed)

    return phy_tput_pdsch, mac_tput_dl, rlc_d_tput, rlc_u_tput, pdcp_dl, pdcp_ul, dl_bler

def txt_log_summary_5g(logfile, outfile):
    """Report 5G log in brief"""
    cell_ids, rsrp, rsrq, dl_freqs, ul_freqs, dl_bwths, ul_bwths, dl_rbs, ul_rbs, dl_mcs, ul_mcs, tx_pwr = extract_cell_info(logfile)
    phy_tput_pdsch, mac_tput_dl, rlc_d_tput, rlc_u_tput, pdcp_dl, pdcp_ul, dl_bler = extract_throughput(logfile)

    with open(outfile, 'w') as f:
        f.write(
            "Serving Physical cell ID list: " + str(cell_ids) + '\n'
            + "RSRP: " + str(rsrp) + '\n'
            + "RSRQ: " + str(rsrq) + '\n'
            + "Dlink EARFCN list: " + str(dl_freqs) + '\n'
            + "Uplink EARFCN list: " + str(ul_freqs) + '\n'
            + "Dlink Bandwidth list: " + str(dl_bwths) + '\n'
            + "Uplink Bandwidth list: " + str(ul_bwths) + '\n'
            + "\n# DOWNLINK" + '\n'
            + "Dlink Physical throughput (Mbps): " + str(phy_tput_pdsch) + '\n'
            + "DLink MAC Throughput (Mbps): " + str(mac_tput_dl) + '\n'
            + "DLink RLC Throughput (Mbps): " + str(rlc_d_tput) + '\n'
            + "DLink PDCP Throughput (Mbps): " + str(pdcp_dl) + '\n'
            + "Avg RBs: " + str(dl_rbs) + '\n'
            + "Avg MCS: " + str(dl_mcs) + '\n'
            + "Avg DLink BLER: " + str(dl_bler) + '%'+ '\n'
            + "\n# UPLINK" + '\n'
            + "Uplink RLC throughput (Mbps): " + str(rlc_u_tput) + '\n'
            + "Uplink PDCP throughput (Mbps): " + str(pdcp_ul) + '\n'
            + "Avg RBs: " + str(ul_rbs) + '\n'
            + "Avg MCS: " + str(ul_mcs) + '\n'
            + "Avg PUSCH Actual Tx Power (dBm): " + str(tx_pwr) + '\n'
        )

# pa = "D:\\ng_analysis\\UlDl-90-9-1.txt"
# pa = "D:\\ng_analysis\\sample_5g_log.txt"
# pa = "D:\\ng_analysis\\small_log.txt"

# out = "D:\\ng_analysis\\5g_summary.txt"
# print(extract_throughput(pa))
# print(extract_cell_info(pa))
# txt_log_summary_5g(pa, out)



# text = "   |  0|     3|   1|          0|         2|     3|         0|         0|                   0|         0|         0|         0|         0|         0|         0|                   0|         0|         0|         0|         0|"
# print(fill_pdcp_dl_stat(text))

# raw_log = "C:\\Users\\admin\Documents\\NguyenHaiHa-thuctap2020\\Log_Analysis-Hoang_version\\Test\\QCAT input\\05-22.16-18.isf"
# out_path = "C:\\Users\\admin\Documents\\NguyenHaiHa-thuctap2020\\Log_Analysis-Hoang_version\\Test\\QCAT output\\"
# out_file = "C:\\Users\\admin\Documents\\NguyenHaiHa-thuctap2020\\Log_Analysis-Hoang_version\\Test\\QCAT output\\test_parser_02_10.txt"
# out_file = "'C:Users\\admin\\Documents\\NguyenHaiHa-thuctap2020\\Log_Analysis-Hoang_version\\Test\\QCAT output\\05-22.16-18_test_parser_02_10.txt'"
# C:\Users\admin\Documents\NguyenHaiHa-thuctap2020\Log_Analysis-Hoang_version\Test\QCAT output\
# print(retrieve_tx_pwr(raw_log, out_path))
# analyzers = [";LTE;Summary;LTE L1 RI Modulation Type Stats", ";LTE;Summary;LTE PDCP Summary;LTE PDCP DL Stats Summary" ]
# qcat_export_grids(raw_log,analyzers,out_path)
# qcat_export_all(raw_log, out_file)

# logId = int("0xB0C0", 16)
# fieldString = ".\"Records\".\"Timing Offset\""
# fieldString = "Physical Cell ID ="
# qcat_get_field(raw_log, logId, fieldString, out_file)

# from tool_summary import change_file_name

# change_file_name(raw_log, out_file)

