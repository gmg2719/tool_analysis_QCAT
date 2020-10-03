import log_parser

data_path = input('Where is your folder? (Enter to use the default Test folder)\n')
if data_path.strip() == "":
    data_path = os.path.join(os.getcwd(), "Test")
    
print data_path
