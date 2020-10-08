import os, glob
import datetime, time, logging
from extract_packet import txt_log_summary_5g


# Global defines
repl_date = datetime.date.today()

running_logfile = os.path.join(os.getcwd(), 'running_log.txt')
processed_file  = os.path.join(os.getcwd(), 'processed_logs.txt')

# Start logging
with open(running_logfile, 'w') as f:
    f.write("Running log for tool parser 5G logs")

logging.basicConfig(
    filename=running_logfile,
    filemode='a',
    format='\n%(asctime)s %(levelname)s %(message)s',
    level=logging.INFO
)

# FUNCTIONS
def is_time_between(begin_time, end_time, check_time=None):
    """ Check given time or current time in range of time or not"""
    # If check time is not given, default to current UTC time
    check_time = check_time or datetime.datetime.now().time()

    if begin_time < end_time:
        return check_time >= begin_time and check_time <= end_time
    else: # Crosses midnight
        return check_time >= begin_time or check_time <= end_time

def path_to_summary(log_path, output_path):
    """Define path to output file"""
    if log_path == None:
        print("Error: Missing log file!!!")
        return
    else:
        reformat_path = log_path.replace('\\', '/')
        if reformat_path.find('/'):
            split_log_path = reformat_path.split('/')
            log_name = split_log_path[-1].split('.')[0]  # remove file extension, Ex. '.txt'
            path_to_file = os.path.join(output_path, log_name + '_summary.txt')
        else:
            path_to_file = os.path.join(output_path, 'log_summary.txt')
        return path_to_file

def auto_run(log_folder, output_path):
    """Export summary in periodic if new logs are appended to folder"""
    global repl_date, processed_file, running_logfile
    while True:
        try:
            if is_time_between(datetime.time(7, 0), datetime.time(20, 0)):
                pass
            else:
                repl_time = '0h00'
                time.sleep(120 * 60)
                continue

            # clean if running log too large
            running_logfile_size = os.stat(running_logfile).st_size
            if running_logfile_size > 99999:
                with open(running_logfile, 'w') as f:
                    f.truncate(0)

            # clean processed_logs for new day
            to_day = datetime.date.today()
            if to_day > repl_date:
                try:
                    logging.info("Clearing processed_logs.txt...")
                    with open(processed_file, 'w') as f:
                        f.truncate(0)
                except Exception as e:
                    logging.exception(e)

            cur_time = time.strftime('%Hh%M')

            repl_date = to_day # record last date scanning

            # Read processed logs
            with open(processed_file, 'r') as pf:
                log_paths = pf.readlines()

            processed_logs = [log_path.strip() for log_path in log_paths]
            new_logs = [f for f in glob.glob(os.path.join(log_folder, '*.txt')) if f not in processed_logs] # Init list for append new log names

            if len(new_logs) == 0:
                logging.warning(" ! No new log!")
                logging.info(" ! Sleep 120 min...!")
                time.sleep(1 * 60)
                continue
            else:
                for log in new_logs:
                    # export summary file name
                    summary_file = path_to_summary(log, output_path)
                    # Start extract info from log
                    logging.info(" ! Exporting summary of log %s...!" %log)
                    txt_log_summary_5g(log, summary_file)
                    logging.info(" ! Exported summary of log %s!" % log)
                with open(processed_file, 'a') as pf:
                    pf.writelines("%s\n" % processed_log for processed_log in new_logs)

            logging.info(" ! Finished! Sleep 120 min...!")
            time.sleep(1 * 60)
        except Exception as e:
            logging.exception(e)
            time.sleep(120 * 60)
            continue



if __name__ == '__main__':
    logfolder = "D:\\ng_analysis\\tool_analysis_QCAT\\QCAT_input"
    output_path = "D:\\ng_analysis\\tool_analysis_QCAT\\QCAT_output"
    auto_run(logfolder, output_path)



