from main import * # import variables and functions from head script

#################
## import config
## only if you want to have an external config file, if no
import os
import importlib.util

def load_config():  
  config_path = os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])), "plugins","example-plugin","config.py")
  spec = importlib.util.spec_from_file_location("config", config_path)
  config_module = importlib.util.module_from_spec(spec)
  spec.loader.exec_module(config_module)
  return config_module

config = load_config()
## end of config import
#################

########################
## your logic and stuff
## you should be able to use every variable and function from the head script
if matrix_received_message == "Hello":
    func_send_message(config.message_test)