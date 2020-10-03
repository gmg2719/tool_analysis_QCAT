# from tkinter import *
from tkinter import Frame, Text, Button, Menu, Label, W, E, END, Tk
from tkinter.filedialog import askopenfilename, askdirectory, Toplevel, CENTER, askopenfilenames
from tkinter.messagebox import *
from tkinter.scrolledtext import ScrolledText

from log_parser_Hoang import *
from qcat_exp import *
from UpLinkAnalysis import *

from variable import *


# from variable import log_file_PATH, config_file_PATH, csv_folder_PATH, raw_log_file_PATH
# IMPORTAN PATH
# config_file_PATH = r''
# log_file_PATH = r''
# csv_folder_PATH = r''
# csv_dict = {}
#
# log_type_list_brief = []
# log_type_list_full = []

class Window(Frame):
    def __init__(self, master):
        Frame.__init__(self, master)
        self.master = master
        self.master.title("LOG ANALYSIS TOOLS")

        self.QCAT_func_button = Button(self.master, text='QCAT Automation', command=self.Call_Open_QCAT)
        self.QCAT_func_button.config(width=25, heigh=2, padx=5, pady=5)
        # self.QCAT_func_button.grid(row = 0, column = 0, columnspan=2)
        self.QCAT_func_button.place(relx=0.5, rely=0.2, anchor=CENTER)

        self.Table_func_button = Button(self.master, text='Convert Table Automation',
                                        command=self.Call_Convert_Table_Auto)
        self.Table_func_button.config(width=25, heigh=2, padx=5, pady=5)
        self.Table_func_button.place(relx=0.5, rely=0.4, anchor=CENTER)

        self.Table_func_button = Button(self.master, text='Uplink Table Merge',
                                        command=self.Call_Uplink_Analysis)
        self.Table_func_button.config(width=25, heigh=2, padx=5, pady=5)
        self.Table_func_button.place(relx=0.5, rely=0.6, anchor=CENTER)

    def Call_Open_QCAT(self):
        self.newWindow = Toplevel(self.master)
        self.app = QCAT_Auto(self.newWindow)

    def Call_Convert_Table_Auto(self):
        self.newWindow = Toplevel(self.master)
        self.app = Convert_Table_Auto(self.newWindow)

    def Call_Uplink_Analysis(self):
        self.newWindow = Toplevel(self.master)
        self.app = Uplink_Analysis(self.newWindow)


######################
class Convert_Table_Auto(Frame):

    def __init__(self, master=None):

        Frame.__init__(self, master)
        self.master = master
        self.master.title("Conver Table Automation")

        ######################################################################################################
        self.config_file_PATH_label = Label(self.master, text="Config file path")
        self.config_file_PATH_label.grid(row=0, column=0, sticky=W, pady=2)
        self.config_file_PATH_txt = Text(self.master, heigh=1, width=35)
        self.config_file_PATH_txt.grid(row=0, column=1, pady=2)

        self.log_file_PATH_label = Label(self.master, text="Log files dir")
        self.log_file_PATH_label.grid(row=1, column=0, sticky=W, pady=2)
        self.log_file_PATH_txt = Text(self.master, heigh=1, width=35)
        self.log_file_PATH_txt.grid(row=1, column=1, pady=2)

        self.qcat_input_label = Label(self.master, text='')

        self.log_type_label = Label(self.master, text="Information")
        self.log_type_label.grid(row=2, column=0, sticky=W)
        self.log_type_txt = ScrolledText(self.master, undo=True, width=55)
        self.log_type_txt.grid(row=3, rowspan=4, column=0, columnspan=3, sticky=W)

        self.csv_dir_label = Label(self.master, text="CSV directory")
        self.csv_dir_label.grid(row=8, column=0, sticky=W)
        self.csv_dir_txt = Text(self.master, heigh=1, width=35)
        self.csv_dir_txt.grid(row=8, column=0, columnspan=3, padx=80, sticky=W)

        ######################################################################################################

        self.convert_csv_button = Button(self.master, text='Convert to csv', command=self.call_convert_csv)
        self.convert_csv_button.grid(row=8, column=1, columnspan=2, sticky=E, pady=2, padx=3)
        self.convert_csv_button.config(width=11, heigh=2)
        self.extract_config_button = Button(self.master, text="Extract", command=self.call_extract)
        self.extract_config_button.grid(row=0, column=2, sticky=E, padx=4)
        # self.view_log_button = Button(self.master, text = "View")
        # self.view_log_button.grid(row=1, column=2, sticky=E, padx=4)

        ###############################################################################
        # creating a menu instance
        self.menu = Menu(self.master)
        self.master.config(menu=self.menu)

        # create the file object)
        self.file = Menu(self.menu)

        # adds a command to the menu option, calling it exit, and the
        # command it runs on event is client_exit
        # self.file.add_command(label="QCAT Automation", command = self.openQCAT)
        self.file.add_command(label="Open Config", command=self.open_config)
        self.file.add_command(label="Choose Log Files", command=self.open_log)
        self.file.add_command(label="Set CSV Directory", command=self.set_csv_directory)
        self.file.add_command(label="Exit", command=self.client_exit)
        self.menu.add_cascade(label="File", menu=self.file)
        # menu.add_cascade(label="Open config", menu=file)

        self.edit = Menu(self.menu)
        self.menu.add_cascade(label="Edit", menu=self.edit)

        self.help = Menu(self.menu)
        self.help.add_command(label="About", command=self.show_about)
        self.help.add_command(label="Instruction", command=self.show_instruction)
        self.menu.add_cascade(label="Help", menu=self.help)

    ####################################################################################

    def client_exit(self):
        exit()

    def open_config(self):
        ###Test
        # global config_file_PATH
        # config_file_PATH = r'G:\PycharmProjects\Log_Extractor\parser.cfg'
        filename = askopenfilename(initialdir='/', title="Select file",
                                   filetypes=(("config file", "*.cfg"), ("all files", "*.*")))
        if filename:
            global config_file_PATH
            config_file_PATH = filename
            print(config_file_PATH)
            # self.update_text()
            self.config_file_PATH_txt.delete("1.0", "end")
            self.config_file_PATH_txt.insert(END, config_file_PATH)
        else:
            showerror("Error", "No file selected")

    def open_log(self):
        # Test
        # global log_file_PATH
        # log_file_PATH = r'G:\PycharmProjects\Log_Extractor\Test\log_test.txt'
        log_paths = askopenfilenames(initialdir='/', title="Select file",
                                    filetypes=(("log file", "*.log"), ("text file", "*.txt"), ("all files", "*.*")))
        # log_path = askdirectory()
        if log_paths:
            global log_file_PATH
            for path in log_paths:
                log_file_PATH.append(path)

            # log_file_PATH = log_paths
            print(log_paths)
            self.log_file_PATH_txt.delete("1.0", "end")
            self.log_file_PATH_txt.insert(END, log_file_PATH)
        else:
            showerror("Error", "No file selected")

    def set_csv_directory(self):
        csv_dir = askdirectory()
        if csv_dir:
            global csv_folder_PATH
            csv_folder_PATH = csv_dir
            self.csv_dir_txt.delete("1.0", "end")
            self.csv_dir_txt.insert(END, csv_dir)
        else:
            showerror("Error", "No directory selected")
        ##Test'
        # global csv_folder_PATH
        # csv_folder_PATH = r'C:\Users\Admin\Desktop\test'

    def call_extract(self):
        global config_file_PATH
        global log_type_list_brief, log_type_list_full
        # if config_file_PATH == '':
        #     self.log_type_txt.insert("Error, No file selected")
        #     # showerror("Error", "No file selected")
        #     return
        try:
            self.log_type_txt.insert(END, "Extracting...\n")
            lines = read_file(config_file_PATH)
            log_type_list_brief, log_type_list_full = read_config_log_types(lines)
            if len(log_type_list_brief) != 0:
                # self.log_type_txt.delete("1.0", "end")
                for log in log_type_list_brief:
                    self.log_type_txt.insert(END, log + '\n')
                self.log_type_txt.insert(END, "Extract successfully\n")
                # showinfo("Respond", "Extract successfully")
            else:
                showwarning("Config Empty", "No log type found in config file. Try again!")
        except:
            # self.log_type_txt.delete("1.0", "end")
            self.log_type_txt.insert(END, "Error extracting\n")

    def call_convert_csv(self):
        global csv_dict, csv_folder_PATH, log_file_PATH, log_type_list_brief
        print(log_type_list_brief)
        if csv_folder_PATH == '':
            self.log_type_txt.insert(END, "You need to select csv directory before convert\n")
            return
        try:
            self.log_type_txt.insert(END, "Converting! Please wait...\n")
            for t in log_type_list_brief:  # init dict of log data list for csv
                csv_dict[t] = [0, []]
            parse_log(log_file_PATH, log_type_list_brief, csv_dict)
            write_csv(csv_folder_PATH, csv_dict)
            self.log_type_txt.insert(END, "Converting successful\n")
        except:
            self.log_type_txt.insert(END, "Fail converting!\n")
            # showerror("Error", "Error Converting")

    # def openQCAT(self):
    #     self.newWindow = Toplevel(self.master)
    #     self.app = QCAT_Auto(self.newWindow)

    def show_instruction(self):
        pass

    def show_about(self):
        pass


class QCAT_Auto(Frame):

    def __init__(self, master=None):

        Frame.__init__(self, master)
        self.master = master
        self.master.title("QCAT Automation")

        ######################################################################################################
        self.config_file_PATH_label = Label(self.master, text="Config file path")
        self.config_file_PATH_label.grid(row=0, column=0, sticky=W, pady=2)
        self.config_file_PATH_txt = Text(self.master, heigh=1, width=35)
        self.config_file_PATH_txt.grid(row=0, column=1, pady=2)

        self.raw_log_file_PATH_label = Label(self.master, text="Raw Log file path")
        self.raw_log_file_PATH_label.grid(row=1, column=0, sticky=W, pady=2)
        self.raw_log_file_PATH_txt = Text(self.master, heigh=1, width=35)
        self.raw_log_file_PATH_txt.grid(row=1, column=1, pady=2)

        # self.qcat_input_label = Label(self.master, text = '')

        self.log_type_label = Label(self.master, text="Information")
        self.log_type_label.grid(row=2, column=0, sticky=W)
        self.log_type_txt = ScrolledText(self.master, undo=True, width=55)
        self.log_type_txt.grid(row=3, rowspan=4, column=0, columnspan=3, sticky=W)

        self.QCAT_txt_dir_label = Label(self.master, text="QCAT Output\nDirectory")
        self.QCAT_txt_dir_label.grid(row=8, column=0, sticky=W)
        self.QCAT_txt_dir_txt = Text(self.master, heigh=1, width=35)
        self.QCAT_txt_dir_txt.grid(row=8, rowspan=2, column=0, columnspan=3, padx=80, sticky=W)

        ######################################################################################################

        self.Import_txt_button = Button(self.master, text='Import to txt', command=self.call_import_txt)
        self.Import_txt_button.grid(row=8, column=1, columnspan=2, sticky=E, pady=2, padx=3)
        self.Import_txt_button.config(width=11, heigh=2)
        self.extract_config_button = Button(self.master, text="Extract", command=self.call_extract)
        self.extract_config_button.grid(row=0, column=2, sticky=E, padx=4)
        # self.view_log_button = Button(self.master, text = "View")
        # self.view_log_button.grid(row=1, column=2, sticky=E, padx=4)

        ###############################################################################
        # creating a menu instance
        self.menu = Menu(self.master)
        self.master.config(menu=self.menu)

        # create the file object)
        self.file = Menu(self.menu)

        # adds a command to the menu option, calling it exit, and the
        # command it runs on event is client_exit
        # self.file.add_command(label="QCAT Automation", command = self.openQCAT)
        self.file.add_command(label="Open Config", command=self.open_config)
        self.file.add_command(label="Open Raw Log", command=self.open_raw_log)
        self.file.add_command(label="Set Output Directory", command=self.set_output_directory)
        self.file.add_command(label="Exit", command=self.client_exit)
        self.menu.add_cascade(label="File", menu=self.file)
        # menu.add_cascade(label="Open config", menu=file)

        self.edit = Menu(self.menu)
        self.menu.add_cascade(label="Edit", menu=self.edit)

        self.help = Menu(self.menu)
        self.help.add_command(label="About", command=self.show_about)
        self.help.add_command(label="Instruction", command=self.show_instruction)
        self.menu.add_cascade(label="Help", menu=self.help)

    ####################################################################################

    def client_exit(self):
        exit()

    def open_config(self):
        ###Test
        # global config_file_PATH
        # config_file_PATH = r'G:\PycharmProjects\Log_Extractor\parser.cfg'
        filename = askopenfilename(initialdir='/', title="Select file",
                                   filetypes=(("config file", "*.cfg"), ("all files", "*.*")))
        if filename:
            global QCAT_config_file_PATH
            QCAT_config_file_PATH = filename
            print(config_file_PATH)
            # self.update_text()
            self.config_file_PATH_txt.delete("1.0", "end")
            self.config_file_PATH_txt.insert(END, QCAT_config_file_PATH)
        else:
            showerror("Error", "No file selected")

    def open_raw_log(self):
        # Test
        # global log_file_PATH
        # log_file_PATH = r'G:\PycharmProjects\Log_Extractor\Test\log_test.txt'
        log_path = askopenfilename(initialdir='/', title="Select file",
                                   filetypes=(("raw log file", "*.qmdl *.dlf *.isf"), ("dlf file", "*.dlf"), ("all files", "*.*")))
        if log_path:
            global QCAT_raw_log_file_PATH
            QCAT_raw_log_file_PATH = log_path
            print(log_path)
            self.raw_log_file_PATH_txt.delete("1.0", "end")
            self.raw_log_file_PATH_txt.insert(END, QCAT_raw_log_file_PATH)
        else:
            showerror("Error", "No file selected")

    def set_output_directory(self):
        csv_dir = askdirectory()
        if csv_dir:
            global QCAT_output_directory
            QCAT_output_directory = csv_dir
            self.QCAT_txt_dir_txt.delete("1.0", "end")
            self.QCAT_txt_dir_txt.insert(END, csv_dir)
        else:
            showerror("Error", "No directory selected")
        ##Test'
        # global csv_folder_PATH
        # csv_folder_PATH = r'C:\Users\Admin\Desktop\test'

    def call_extract(self):
        global QCAT_config_file_PATH
        global QCAT_log_list_brief, QCAT_log_list_full

        try:
            self.log_type_txt.insert(END, "Extracting...\n")
            lines = read_file(QCAT_config_file_PATH)
            QCAT_log_list_brief, QCAT_log_list_full = read_config_log_types(lines)
            if len(QCAT_log_list_brief) != 0:
                # self.log_type_txt.delete("1.0", "end")
                for log in QCAT_log_list_brief:
                    self.log_type_txt.insert(END, log + '\n')
                self.log_type_txt.insert(END, "Extract successfully\n")
                # showinfo("Respond", "Extract successfully")
            else:
                showwarning("Config Empty", "No log type found in config file. Try again!")
        except:
            # self.log_type_txt.delete("1.0", "end")
            self.log_type_txt.insert(END, "Error extracting\n")

    def call_import_txt(self):
        global QCAT_raw_log_file_PATH, QCAT_output_directory, QCAT_log_list_brief
        self.log_type_txt.insert(END, "Importing! Please wait...\n")
        if QCAT_raw_log_file_PATH == '' or QCAT_output_directory == '' or len(QCAT_log_list_brief) == 0:
            self.log_type_txt.insert(END, "Error, Please check raw log path, output directory and config file\n")
        try:
            QCAT_Execute(QCAT_raw_log_file_PATH, QCAT_log_list_brief, QCAT_output_directory)
            self.log_type_txt.insert(END, "Import successful")

        except:
            self.log_type_txt.insert(END, "Error importing\n")

    # def openQCAT(self):
    #     self.newWindow = Toplevel(self.master)
    #     self.app = QCAT_Auto(self.newWindow)

    def show_instruction(self):
        pass

    def show_about(self):
        pass


class Uplink_Analysis(Frame):
    def __init__(self, master):
        Frame.__init__(self, master)
        self.master = master
        self.master.geometry("420x200")
        self.master.title("Uplink Analysis")

        self.PwCtrl_file_PATH_label = Label(self.master, text="Power Control File Path")
        self.PwCtrl_file_PATH_label.grid(row=0, column=0, sticky=W, pady=2)
        self.PwCtrl_file_PATH_txt = Text(self.master, heigh=1, width=35)
        self.PwCtrl_file_PATH_txt.grid(row=0, column=1, pady=2)

        self.DCI_file_PATH_label = Label(self.master, text="DCI File Path")
        self.DCI_file_PATH_label.grid(row=1, column=0, sticky=W, pady=2)
        self.DCI_file_PATH_txt = Text(self.master, heigh=1, width=35)
        self.DCI_file_PATH_txt.grid(row=1, column=1, pady=2)

        self.TxReport_file_PATH_label = Label(self.master, text="Tx Report File Path")
        self.TxReport_file_PATH_label.grid(row=2, column=0, sticky=W, pady=2)
        self.TxReport_file_PATH_txt = Text(self.master, heigh=1, width=35)
        self.TxReport_file_PATH_txt.grid(row=2, column=1, pady=2)

        self.PHICH_file_PATH_label = Label(self.master, text="PHICH File Path")
        self.PHICH_file_PATH_label.grid(row=3, column=0, sticky=W, pady=2)
        self.PHICH_file_PATH_txt = Text(self.master, heigh=1, width=35)
        self.PHICH_file_PATH_txt.grid(row=3, column=1, pady=2)

        self.Output_dir_label = Label(self.master, text="Output directory")
        self.Output_dir_label.grid(row=4, column=0, sticky=W, pady=2)
        self.Output_dir_txt = Text(self.master, heigh=1, width=35)
        self.Output_dir_txt.grid(row=4, column=1, pady=2)

        # Button config
        self.merge_button = Button(self.master, text = 'Merge Table', command = self.call_merge)
        self.merge_button.config(width=10, heigh=4)
        self.merge_button.grid(row = 5, column=0, columnspan = 2, sticky = E)




        self.menu = Menu(self.master)
        self.master.config(menu=self.menu)

        # create the file object)
        self.file = Menu(self.menu)

        # adds a command to the menu option, calling it exit, and the
        # command it runs on event is client_exit

        self.file.add_command(label="Open Power Control file", command=self.open_PwCtrl)
        self.file.add_command(label="Open DCI file", command=self.open_DCI)
        self.file.add_command(label="Open Tx Report file", command=self.open_TxReport)
        self.file.add_command(label="Open PHICH file", command=self.open_PHICH)
        self.file.add_command(label="Set oput directory", command=self.set_dir)
        self.file.add_command(label="Exit", command=self.client_exit)
        self.menu.add_cascade(label="File", menu=self.file)
        # menu.add_cascade(label="Open config", menu=file)

        self.edit = Menu(self.menu)
        self.menu.add_cascade(label="Edit", menu=self.edit)

        self.help = Menu(self.menu)
        self.help.add_command(label="About", command=self.show_about)
        self.help.add_command(label="Instruction", command=self.show_instruction)
        self.menu.add_cascade(label="Help", menu=self.help)

    def open_PwCtrl(self):
        filename = askopenfilename(initialdir='/', title="Select file",
                                   filetypes=(("csv file", "*.csv"), ("all files", "*.*")))
        if filename:
            global pw_ctrl_path
            pw_ctrl_path = filename
            print(pw_ctrl_path)
            # self.update_text()
            self.PwCtrl_file_PATH_txt.delete("1.0", "end")
            self.PwCtrl_file_PATH_txt.insert(END, pw_ctrl_path)
        else:
            showerror("Error", "No file selected")

    def open_DCI(self):
        filename = askopenfilename(initialdir='/', title="Select file",
                                   filetypes=(("csv file", "*.csv"), ("all files", "*.*")))
        if filename:
            global dci_path
            dci_path = filename
            print(dci_path)
            # self.update_text()
            self.DCI_file_PATH_txt.delete("1.0", "end")
            self.DCI_file_PATH_txt.insert(END, dci_path)
        else:
            showerror("Error", "No file selected")

    def open_TxReport(self):
        filename = askopenfilename(initialdir='/', title="Select file",
                                   filetypes=(("csv file", "*.csv"), ("all files", "*.*")))
        if filename:
            global tx_report_path
            tx_report_path = filename
            print(tx_report_path)
            # self.update_text()
            self.TxReport_file_PATH_txt.delete("1.0", "end")
            self.TxReport_file_PATH_txt.insert(END, tx_report_path)
        else:
            showerror("Error", "No file selected")
    def open_PHICH(self):
        filename = askopenfilename(initialdir='/', title="Select file",
                                   filetypes=(("csv file", "*.csv"), ("all files", "*.*")))
        if filename:
            global phich_path
            phich_path = filename
            print(phich_path)
            # self.update_text()
            self.PHICH_file_PATH_txt.delete("1.0", "end")
            self.PHICH_file_PATH_txt.insert(END, phich_path)
        else:
            showerror("Error", "No file selected")
    def set_dir(self):
        dir = askdirectory()
        if dir:
            global output_path
            output_path = dir
            print(output_path)
            self.Output_dir_txt.delete("1.0", "end")
            self.Output_dir_txt.insert(END, output_path)
        else:
            showerror("Error", "No directory selected")

    def call_merge(self):
        global pw_ctrl_path, dci_path, tx_report_path, phich_path, output_path
        try:
            Execute(pw_ctrl_path, dci_path, tx_report_path, phich_path, output_path)
        except:
            showerror("Error", "Check files or directory")



    def client_exit(self):
        exit()
    def show_about(self):
        pass
    def show_instruction(self):
        pass


# root window created. Here, that would be the only window, but
# you can later have windows within windows.
root = Tk()
root.geometry("300x300")
root.resizable(width=False, height=False)

# creation of an instance
app = Window(root)

# mainloop
root.mainloop()
