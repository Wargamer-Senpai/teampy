import requests 
import inspect

from modules.logger import func_write_to_log
from modules.notify import *

def func_check_client_update(matrix_base_url, sync_headers, teamspeak_version_notify_matrix_rooms, matrix_update_message, teamspeak_version_saved, teamspeak_version_notify_file, event_id, stat_dict):
  """Check for Teamspeak client updates and trigger a notification if a new version is available

  Args:
      matrix_base_url (str): the base URL of the Matrix server
      access_token (str): current session access token
      user_agent (str): user agent for talking to the api
      teamspeak_version_notify_matrix_rooms (list): list of rooms to notify
      matrix_update_message (str): contains the message of when an update is available
      teamspeak_version_saved (str): the version that was found
      teamspeak_version_notify_file (str): path to file with rooms to notify
      event_id (_type_): the event id of the message 
  """
  try:
    current_function = inspect.currentframe().f_code.co_name
    request_version_header = {"Authorization": "Basic dGVhbXNwZWFrNTpMRlo2Wl5rdkdyblh+YW4sJEwjNGd4TDMnYTcvYVtbJl83PmF0fUEzQVJSR1k=", "User-Agent": "teamspeak.downloader/1.0"}
    request_version_url= "http://update.teamspeak.com/windows/x64/latest/info.json"
    version_response = requests.get(request_version_url, headers=request_version_header, auth=("teamspeak5", "LFZ6Z^kvGrnX~an,$L#4gxL3'a7/a[[&_7>at}A3ARRGY"))
    teamspeak_version_request = version_response.json()["version_string"]
    func_write_to_log("Version Check for Client: " + str(teamspeak_version_request), "INFO", current_function)
    if teamspeak_version_request:
      if teamspeak_version_saved:
        if teamspeak_version_saved != teamspeak_version_request:
          teamspeak_version_saved = teamspeak_version_request
          func_notify_update(matrix_base_url, sync_headers, teamspeak_version_notify_matrix_rooms, matrix_update_message, teamspeak_version_saved, teamspeak_version_notify_file, event_id, stat_dict)

      else:
        teamspeak_version_saved = teamspeak_version_request
  except Exception as e:
    func_write_to_log("Error checking Teamspeak client version: " + str(e), "ERROR", current_function)


