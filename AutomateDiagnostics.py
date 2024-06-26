import json
import os
import subprocess
import platform
import base64
import getopt
import sys
import cgi
import html	#Added to fix escape error in Python3

def system_call(command):
	p = subprocess.Popen([command], stdout=subprocess.PIPE, shell=True)
	return p.stdout.read()

if os.path.exists("/usr/local/ltechagent/state"):

	# Read state file for info
	with open("/usr/local/ltechagent/state","r") as read_file:
		data = json.load(read_file)

	# Get last contact date
	lc = data["last_contact"]
	last_contact = "{0}/{1}/{2} {3}:{4:02d}:{5:02d}".format(lc["month"],lc["day_of_month"],lc["year"],lc["hour"],lc["min"],lc["sec"])

	old_version = data["version"]

	system_call("/usr/local/ltechagent/ltupdate")

	# Read state file for info
	with open("/usr/local/ltechagent/state","r") as read_file:
		data = json.load(read_file)

	if old_version != data["version"]:
		update = "Updated from "+old_version+" to "+ data["version"]
	else:
		update = "Already updated to "+ data["version"]

	server_addr = data["last_good_server_url"]
	version = data["version"]
	id = data['computer_id']
	clientid = data['client_id']
	online = data["is_signed_in"]

else:

	server_addr = 'Not Found'
	last_contact = ''
	version = ''
	update = ''
	id = ''
	clientid = ''
	online = ''

if os.path.exists("/usr/local/ltechagent/agent.log"):

	lterrors = ""

	try:
		opts, args = getopt.getopt(sys.argv[1:],"e")
		for opt, arg in opts:
			if opt == '-e':
				with open("/usr/local/ltechagent/agent.log","r") as log_file:
					lterrors = html.escape(log_file.read())
					#Changed from cgi.escape to html.escape to resolve errors in Python3

	except getopt.GetoptError:
		pass

	lterrors_bytes = lterrors.encode("ascii")
	lterrors_b64_bytes = base64.b64encode(lterrors_bytes)
	lterrors_str = lterrors_b64_bytes.decode("ascii")

else:

	lterrors_str = "Log file not found"

# Check services
if platform.system() == 'Darwin':
	if system_call("launchctl list | grep com.labtechsoftware.LTSvc") != "":
		statusname = "Running"
	else:
		os.system("launchctl stop com.labtechsoftware.LTSvc")
		os.system("launchctl start com.labtechsoftware.LTSvc")
		if system_call("launchctl list | grep com.labtechsoftware.LTSvc") != "":
			statusname = "Running"
		else:
			statusname = "Stopped"
	svc_ltsvc = { "Status": statusname, "User": "com.labtechsoftware.LTSvc", "Start Mode": "Auto"}
elif platform.system() == 'Linux':
	status = os.system('service ltechagent status')
	if status == 0:
		statusname = "Running"
	elif status == 3:
		os.system('service ltechagent stop')
		os.system('service ltechagent start')
		status = os.system('service ltechagent status')
		if status == 0:
			statusname = "Running"
		else:
			statusname = "Stopped"
	else:
		statusname = "Stopped"
	svc_ltsvc = { "Status": statusname, "User": "ltechagent", "Start Mode": "Auto"}

diag_result = {
	'server_addr': server_addr,
	'lastcontact': last_contact,
	'update': update,
	'version': version,
	'id': id,
	'clientid': clientid,
	'online': online,
	'svc_ltservice': svc_ltsvc,
	'lterrors': lterrors_str
}

print("!---BEGIN JSON---!")
print(json.dumps(diag_result))