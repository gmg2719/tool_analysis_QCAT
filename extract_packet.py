from __future__ import print_function, division

import os
import datetime
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
        num_rb    = int(power_ctrl[11].strip())
        return num_rb, pusch_pwr

def fill_ul_mcs(stat_line):
    """Extract MCS, TB size on PUSCH"""
    schedule_info = stat_line.split('|')
    if len(schedule_info) > 40:
        mcs = int(schedule_info[26].strip())
        tb_size = int(schedule_info[11].strip())
        return mcs, tb_size

def fill_dl_mcs_rb(stat_line):
    """Extract DL MCS and RBs"""
    schedule_info = stat_line.split('|')
    if len(schedule_info) > 60:
        mcs = int(schedule_info[18].strip())
        rb  = int(schedule_info[45].strip())
        return mcs, rb

def fill_pdsch_tb(stat_line):
    """Extract TB Byte from PDSCH status"""
    dl_stat = stat_line.split('|')
    if len(dl_stat) > 13:
        slot_elapsed = int(dl_stat[3].strip())
        tb_byte = int(dl_stat[12].strip())
        return tb_byte, slot_elapsed

def fill_pdsch_stat(stat_line):
    """Extract PDSCH UL status for retrieve throughput info"""
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
    ul_tb    = []

    total_rsrp   = 0
    total_rsrq   = 0
    total_ul_rb  = 0
    total_dl_rb  = 0
    total_tx_pwr = 0
    total_ul_mcs = 0
    total_dl_mcs = 0
    total_ul_tb  = 0

    meas_count   = 0
    tx_count     = 0
    ul_mcs_count = 0
    dl_mcs_count = 0
    pusch_count  = 0

    max_ul_tb       = 0
    max_rsrp        = -999
    max_rsrq        = -999
    max_ul_mcs      = 0
    max_dl_mcs      = 0
    max_ul_rb       = 0
    max_dl_rb       = 0
    max_tx_pwr      = -99

    min_ul_tb  = 999999
    min_rsrp   = 99
    min_rsrq   = 99
    min_ul_mcs = 99
    min_dl_mcs = 99
    min_ul_rb  = 999
    min_dl_rb  = 999
    min_tx_pwr = 99

    ml1_measure_found = False
    tx_power_found    = False
    ul_mcs_found      = False
    dl_mcs_found      = False
    freq_found        = False
    first_pusch_found = True

    iline_context = 0

    with open(log_file) as f:
        for line in f:
            if line.find('0xB97F') != -1:
                ml1_measure_found = True
            elif line.find('0xB884') != -1:
                tx_power_found = True
            elif line.find('0xB883') != -1:
                ul_mcs_found = True
                if first_pusch_found:
                    first_time = line.split()[3]
                    first_pusch_found = False
                else:
                    last_time = line.split()[3]
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
                    total_rsrp += rsrp
                    total_rsrq += rsrq

                    # Find min max RSRP, RSRQ
                    if rsrp > max_rsrp:
                        max_rsrp = rsrp
                    if rsrq > max_rsrq:
                        max_rsrq = rsrq
                    if rsrp < min_rsrp:
                        min_rsrp = rsrp
                    if rsrq < min_rsrq:
                        min_rsrq = rsrq

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
                        total_ul_rb  += ul_rb
                        total_tx_pwr += tx_pwr
                        tx_count     += 1

                        # Find min max UL RB
                        if ul_rb < min_ul_rb:
                            min_ul_rb = ul_rb
                        if ul_rb > max_ul_rb:
                            max_ul_rb = ul_rb

                        # Find min max Tx Power
                        if tx_pwr < min_tx_pwr:
                            min_tx_pwr = tx_pwr
                        if tx_pwr > max_tx_pwr:
                            max_tx_pwr = tx_pwr

                if line == '\n':
                    tx_power_found = False
                    iline_context = 0

            if ul_mcs_found:
                iline_context += 1
                if iline_context == 14 or iline_context == 15: # Line 14th or 15th when found ' Physical Channel Schedule' contains MCS
                    if line.find('PUSCH') != -1: # Only consider PUSCH, skip PUCCH
                        if line.find('NEW_TX') != -1:
                            ul_mcs, tb_size = fill_ul_mcs(line)
                            total_ul_mcs += ul_mcs
                            total_ul_tb  += tb_size
                            ul_mcs_count += 1

                            # Find min max UL MCS
                            if ul_mcs > max_ul_mcs:
                                max_ul_mcs = ul_mcs
                            if ul_mcs < min_ul_mcs:
                                min_ul_mcs = ul_mcs

                            # Calculate Min Max UL TB
                            ul_tb.append(tb_size)
                            if len(ul_tb) == 10: # Period of message 0xB883 is 10ms => Consider sliding window 100ms
                                inst_tb = sum(ul_tb) # Total TB bytes in period of 100ms
                                if inst_tb < min_ul_tb:
                                    min_ul_tb = inst_tb
                                if inst_tb > max_ul_tb:
                                    max_ul_tb = inst_tb

                                ul_tb.pop(0)

                        pusch_count += 1

                if line == '\n':
                    ul_mcs_found = False
                    iline_context = 0

            if dl_mcs_found:
                iline_context += 1
                if iline_context == 15: # Line 15th when found ' MAC PDSCH Status' contains DL MCS and RBs
                    dl_mcs, dl_rb = fill_dl_mcs_rb(line)
                    total_dl_mcs += dl_mcs
                    total_dl_rb        += dl_rb
                    dl_mcs_count += 1

                    # Find min max DL MCS
                    if dl_mcs > max_dl_mcs:
                        max_dl_mcs = dl_mcs
                    if dl_mcs < min_dl_mcs:
                        min_dl_mcs = dl_mcs

                    # Find min max DL RB
                    if dl_rb < min_dl_rb:
                        min_dl_rb = dl_rb
                    if dl_rb > max_dl_rb:
                        max_dl_rb = dl_rb

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
                ul_bler    = ceil((pusch_count - ul_mcs_count) / pusch_count * 10) / 10.0
                first_pusch_time = datetime.datetime.strptime(first_time, "%H:%M:%S.%f")
                last_pusch_time = datetime.datetime.strptime(last_time, "%H:%M:%S.%f")
                time_diff  = last_pusch_time - first_pusch_time
                seconds_diff =  time_diff.total_seconds()
                ul_tput    = ceil(total_ul_tb * 8 / 1000 / seconds_diff / 1000 * 100) / 100.0  # Byte => Mb
                max_ul_tput = ceil(max_ul_tb * 8 / 10000 * 100) / 100 # divide 0.01 second = multiply 100 => 1000000 -> 10000
                min_ul_tput = ceil(min_ul_tb * 8 / 10000 * 100) / 100
                if dl_mcs_count != 0:
                    avg_dl_mcs = int(ceil(total_dl_mcs / dl_mcs_count))
                    avg_dl_rb  = int(ceil(total_dl_rb / dl_mcs_count))

                    return cell_ids, min_rsrp, max_rsrp, avg_rsrp, min_rsrq, max_rsrq, avg_rsrq, \
                           dl_freqs, ul_freqs, dl_bwths, ul_bwths, \
                           min_dl_rb, max_dl_rb, avg_dl_rb, min_ul_rb, max_ul_rb, avg_ul_rb, \
                           min_dl_mcs, max_dl_mcs, avg_dl_mcs, min_ul_mcs, max_ul_mcs, avg_ul_mcs, \
                           min_tx_pwr, max_tx_pwr, avg_tx_pwr, min_ul_tput, max_ul_tput, ul_tput, ul_bler

def rlc_inst_ul_tput(pre_stat, cur_stat):
    """Calculate instant RLC UL througput every 0.5 second"""
    pre_rlc_tput = fill_rlc_ul_stat(pre_stat)
    cur_rlc_tput  = fill_rlc_ul_stat(cur_stat)
    return cur_rlc_tput - pre_rlc_tput

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
                       / num_slot_elapsed * 10) / 10.0
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
    rlc_ul_tput = ceil((last_total_tx_byte - first_total_tx_byte) / 1000 * 8 * 2 / num_slot_elapsed * 100) / 100.0
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
    pdcp_ul_tput = ceil((last_total_num_rx_byte - first_total_num_rx_byte) / 1000 * 8 * 2 / num_slot_elapsed * 100) / 100.0
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

    max_slot         = 0
    max_dl_byte      = 0
    max_rlc_ul_byte  = 0
    max_rlc_dl_byte  = 0
    max_pdcp_ul_byte = 0
    max_pdcp_dl_byte = 0

    min_slot         = 0
    min_dl_byte      = 99999
    min_rlc_ul_byte  = 99999
    min_rlc_dl_byte  = 99999
    min_pdcp_ul_byte = 99999
    min_pdcp_dl_byte = 99999

    dl_tb          = []

    iline         = 0
    iline_context = 0

    with open(logtxt) as f:
        for line in f:
            iline += 1
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

                            # calculate Max DL Byte
                            idex = line.split('|')
                            # TODO: Check why 2 previous lines in messages appear here
                            if len(idex) > 1 and idex[1].strip().isdigit(): # Check if this line is values line
                                inst_dl_byte, slot_elapsed = fill_pdsch_tb(line)
                                dl_tb.append((inst_dl_byte, slot_elapsed))
                                if len(dl_tb) == 20: # Period of 0xB888 message is 5ms => Consider sliding window of 100 ms
                                    dl_byte = dl_tb[19][0] - dl_tb[0][0]
                                    # Find max min DL bytes
                                    if dl_byte > max_dl_byte:
                                        max_dl_byte = dl_byte
                                        max_slot    = dl_tb[19][1] - dl_tb[0][1]
                                    if dl_byte < min_dl_byte:
                                        min_dl_byte = dl_byte
                                        min_slot    = dl_tb[19][1] - dl_tb[0][1]

                                    dl_tb.pop(0) # Remove first element for sliding window

                else:
                    if rlc_ul_found:
                        if line == '\n':
                            rlc_ul_found = False
                        else:
                            if iline == iline_context:
                                if first_rlc_find:
                                    first_rlc_stat = line

                                    # Calculate first RLC UL Bytes
                                    pre_rlc_ul_byte = fill_rlc_ul_stat(first_rlc_stat)

                                    first_rlc_find = False
                                else:
                                    # Instant rlc UL status
                                    last_rlc_stat  = line

                                    # Calculate instant RLC UL Bytes

                                    cur_rlc_ul_byte = fill_rlc_ul_stat(last_rlc_stat)
                                    inst_rlc_ul_byte = cur_rlc_ul_byte - pre_rlc_ul_byte
                                    # Find max min transmitted bytes in message 0xB868 period of 0.5 second
                                    if inst_rlc_ul_byte > max_rlc_ul_byte:
                                        max_rlc_ul_byte = inst_rlc_ul_byte
                                    if inst_rlc_ul_byte < min_rlc_ul_byte:
                                        min_rlc_ul_byte = inst_rlc_ul_byte
                                    # Store for next calculation
                                    pre_rlc_ul_byte = cur_rlc_ul_byte
                                    # print(int_rlc_ul_byte)

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

                                            # Extract first PDCP UL Bytes
                                            pre_pdcp_ul_byte = fill_pdcp_ul_stat(line)

                                            first_pdcp_ul_find = False
                                        else:
                                            # Instant PDCP UL status
                                            last_pdcp_ul_stat = line

                                            # Calculate instant PDCP UL Bytes
                                            cur_pdcp_ul_byte = fill_pdcp_ul_stat(last_pdcp_ul_stat)
                                            inst_pdcp_ul_byte = cur_pdcp_ul_byte - pre_pdcp_ul_byte
                                            # Find max transmitted bytes in message 0xB860 period of 0.5 second
                                            if inst_pdcp_ul_byte > max_pdcp_ul_byte:
                                                max_pdcp_ul_byte = inst_pdcp_ul_byte
                                            if inst_pdcp_ul_byte < min_pdcp_ul_byte:
                                                min_pdcp_ul_byte = inst_pdcp_ul_byte
                                            # Store for next calculation
                                            pre_pdcp_ul_byte = cur_pdcp_ul_byte


                                        iline_context += 1
                        else:
                            if pdcp_dl_found:
                                if line == '\n':
                                    pdcp_dl_found = False
                                else:
                                    if iline == iline_context:
                                        if first_pdcp_dl_find:
                                            first_pdcp_dl_stat = line

                                            # Extract first PDCP UL Bytes
                                            pre_pdcp_dl_byte = fill_pdcp_dl_stat(line)

                                            first_pdcp_dl_find = False
                                        else:
                                            # Instant PDCP DL status
                                            last_pdcp_dl_stat  = line

                                            # Calculate instant PDCP DL Bytes
                                            cur_pdcp_dl_byte = fill_pdcp_dl_stat(last_pdcp_dl_stat)
                                            inst_pdcp_dl_byte = cur_pdcp_dl_byte - pre_pdcp_dl_byte
                                            # Find max transmitted bytes in message 0xB842 period of 100 miliseconds
                                            if inst_pdcp_dl_byte > max_pdcp_dl_byte:
                                                max_pdcp_dl_byte = inst_pdcp_dl_byte
                                            if inst_pdcp_dl_byte < min_pdcp_dl_byte:
                                                min_pdcp_dl_byte = inst_pdcp_dl_byte
                                            # Store for next calculation
                                            pre_pdcp_dl_byte = cur_pdcp_dl_byte

                                        iline_context += 1
                            else:
                                if rlc_dl_found:
                                    if line == '\n':
                                        rlc_dl_found = False
                                    else:
                                        if iline == iline_context:
                                            if first_dl_rlc_find:
                                                first_rlc_dl_stat = line

                                                # Calculate first RLC DL Bytes
                                                pre_rlc_dl_byte = fill_rlc_dl_stat(line)

                                                first_dl_rlc_find = False
                                            else:
                                                # Instant RLC DL status
                                                last_rlc_dl_stat  = line

                                                # Calculate instant RLC DL Bytes
                                                cur_rlc_dl_byte = fill_rlc_dl_stat(line)
                                                int_rlc_dl_byte = cur_rlc_dl_byte - pre_rlc_dl_byte
                                                # Find max transmitted bytes in message 0xB868 period of 0.5 second
                                                if int_rlc_dl_byte > max_rlc_dl_byte:
                                                    max_rlc_dl_byte = int_rlc_dl_byte
                                                if int_rlc_dl_byte < min_rlc_dl_byte:
                                                    min_rlc_dl_byte = int_rlc_dl_byte
                                                # Store for next calculation
                                                pre_rlc_dl_byte = cur_rlc_dl_byte

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

    # Average throughput calculations and DL BLER
    num_slot_elapsed, phy_tput_pdsch, mac_tput_dl, dl_bler, dl_retx_bler = pdsch_dl_tput(first_pdsch_stat, last_pdsch_stat)
    rlc_u_tput = rlc_ul_tput(first_rlc_stat, last_rlc_stat, num_slot_elapsed)
    rlc_d_tput = rlc_dl_tput(first_rlc_dl_stat, last_rlc_dl_stat, num_slot_elapsed)
    pdcp_ul  = pdcp_ul_tput(first_pdcp_ul_stat, last_pdcp_ul_stat, num_slot_elapsed)
    pdcp_dl  = pdcp_dl_tput(first_pdcp_dl_stat, last_pdcp_dl_stat, num_slot_elapsed)

    # Max throughput calculations
    max_rlc_ul_tput  = ceil(max_rlc_ul_byte * 2 * 8 / 1000000 * 100) / 100.0 # Multiply 2 because period message is 500ms
    max_rlc_dl_tput  = ceil(max_rlc_dl_byte * 8 / 1000001 * 10) / 10.0 # Period is 100ms => *10
    max_pdcp_ul_tput = ceil(max_pdcp_ul_byte * 2 * 8 / 1000000 * 100) / 100.0
    max_pdcp_dl_tput = ceil(max_pdcp_dl_byte * 8 / 100000 * 10) / 10.0
    max_dl_tput      = ceil(max_dl_byte * 2 * 8 / 1000 / max_slot * 10) / 10.0 # Each slot = 0.5ms

    # Min throughput calculations
    min_rlc_ul_tput = ceil(min_rlc_ul_byte * 2 * 8 / 1000000 * 100) / 100.0  # Multiply 2 because period message is 500ms
    min_rlc_dl_tput = ceil(min_rlc_dl_byte * 8 / 1000001 * 10) / 10.0  # Period is 100ms => *10
    min_pdcp_ul_tput = ceil(min_pdcp_ul_byte * 2 * 8 / 1000000 * 100) / 100.0
    min_pdcp_dl_tput = ceil(min_pdcp_dl_byte * 8 / 100000 * 10) / 10.0
    min_dl_tput = ceil(min_dl_byte * 2 * 8 / 1000 / min_slot * 10) / 10.0  # Each slot = 0.5ms

    return phy_tput_pdsch, mac_tput_dl, rlc_d_tput, rlc_u_tput, pdcp_dl, pdcp_ul, dl_bler, \
           max_rlc_ul_tput, max_rlc_dl_tput, max_pdcp_ul_tput, max_pdcp_dl_tput, max_dl_tput, \
           min_rlc_ul_tput, min_rlc_dl_tput, min_pdcp_ul_tput, min_pdcp_dl_tput, min_dl_tput

def txt_log_summary_5g(logfile, outfile):
    """Report 5G log in brief to a text file"""
    # Extract cell information
    cell_ids, min_rsrp, max_rsrp, rsrp, min_rsrq, max_rsrq, rsrq, \
    dl_freqs, ul_freqs, dl_bwths, ul_bwths, \
    min_dl_rbs, max_dl_rbs, dl_rbs, min_ul_rbs, max_ul_rbs, ul_rbs, \
    min_dl_mcs, max_dl_mcs, dl_mcs, min_ul_mcs, max_ul_mcs, ul_mcs, \
    min_tx_pwr, max_tx_pwr, tx_pwr, min_ul_tput, max_ul_tput, ul_tput, ul_bler = extract_cell_info(logfile)

    # Extract throughput values
    phy_tput_pdsch, mac_tput_dl, rlc_d_tput, rlc_u_tput, pdcp_dl, pdcp_ul, dl_bler, \
    max_rlc_ul_tput, max_rlc_dl_tput, max_pdcp_ul_tput, max_pdcp_dl_tput, max_dl_tput, \
    min_rlc_ul_tput, min_rlc_dl_tput, min_pdcp_ul_tput, min_pdcp_dl_tput, min_dl_tput = extract_throughput(logfile)

    with open(outfile, 'w') as f:
        f.write(
            "Serving Physical cell ID list: " + str(cell_ids) + '\n'
            + "Min/Max/Avg RSRP: " + str(min_rsrp) + '/' + str(max_rsrp) + '/' + str(rsrp) + '\n'
            + "Min/Max/Avg RSRQ: " + str(min_rsrq) + '/' + str(max_rsrq) + '/' + str(rsrq) + '\n'
            + "Dlink EARFCN list: " + str(dl_freqs) + '\n'
            + "Uplink EARFCN list: " + str(ul_freqs) + '\n'
            + "Dlink Bandwidth list: " + str(dl_bwths) + '\n'
            + "Uplink Bandwidth list: " + str(ul_bwths) + '\n'
            + "\n# DOWNLINK" + '\n'
            + "Min/Max/Avg PHY DL throughput (Mbps): " + str(min_dl_tput) + '/' + str(max_dl_tput) + '/' + str(phy_tput_pdsch) + '\n'
            # + "DLink MAC Throughput (Mbps): " + str(mac_tput_dl) + '\n'
            + "Min/Max/Avg RLC DL Throughput (Mbps): " + str(min_rlc_dl_tput) + '/' + str(max_rlc_dl_tput) + '/' + str(rlc_d_tput) + '\n'
            + "Min/Max/Avg PDCP DL Throughput (Mbps): " + str(min_pdcp_dl_tput) + '/' + str(max_pdcp_dl_tput) + '/' + str(pdcp_dl) + '\n'
            + "Min/Max/Avg RBs: " + str(min_dl_rbs) + '/' + str(max_dl_rbs) + '/' + str(dl_rbs) + '\n'
            + "Min/Max/Avg MCS: " + str(min_dl_mcs) + '/' + str(max_dl_mcs) + '/' + str(dl_mcs) + '\n'
            + "Avg DLink BLER: " + str(dl_bler) + '%'+ '\n'
            + "\n# UPLINK" + '\n'
            + "Min/Max/Avg PHY UL throughput (Mbps): " + str(min_ul_tput) + '/' + str(max_ul_tput) + '/' + str(ul_tput) + '\n'
            + "Min/Max/Avg RLC UL throughput (Mbps): " + str(min_rlc_ul_tput) + '/' + str(max_rlc_ul_tput) + '/' + str(rlc_u_tput) + '\n'
            + "Min/Max/Avg PDCP UL throughput (Mbps): " + str(min_pdcp_ul_tput) + '/' + str(max_pdcp_ul_tput) + '/' + str(pdcp_ul) + '\n'
            + "Min/Max/Avg RBs: " + str(min_ul_rbs) + '/' + str(max_ul_rbs) + '/' + str(ul_rbs) + '\n'
            + "Min/Max/Avg MCS: " + str(min_ul_mcs) + '/' + str(max_ul_mcs) + '/' + str(ul_mcs) + '\n'
            + "Avg UpLink BLER: " + str(ul_bler) + '%' + '\n'
            + "Min/Max/Avg PUSCH Actual Tx Power (dBm): " + str(min_tx_pwr) + '/' + str(max_tx_pwr) + '/' + str(tx_pwr) + '\n'
        )

pa = "D:\\ng_analysis\\UlDl-90-9-1.txt"
# pa = "D:\\ng_analysis\\sample_5g_log.txt"
# pa = "D:\\ng_analysis\\small_log.txt"

out = "D:\\ng_analysis\\5g_summary.txt"
# print(extract_throughput(pa))
# print(extract_cell_info(pa))
txt_log_summary_5g(pa, out)



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

