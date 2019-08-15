import github3, os, platform
from modules.dataenc import pass_dec, pass_enc
from modules.configobj import ConfigObj
code_2fa = ""


# Support IIS site prefix on Windows
if platform.system() == "Windows":
	prefix = "transc\\"
else:
	prefix = ""


def get_two_factor():
	global code_2fa
	if code_2fa is None:
		return ""
	else:
		return code_2fa


def push_update_to_git(username, token, path, account, repo, message):
	files_to_upload = [path]
	gh = github3.login(username=username, token=token, two_factor_callback=get_two_factor)
	repository = gh.repository(account, repo)
	for file_info in files_to_upload:
		with open(prefix+file_info, 'rb') as fd:
			contents = fd.read()
		try:
			contents_object = repository.file_contents(file_info)
		except AttributeError:
			contents_object = False
		if contents_object: #this file already exists on remote repo
			#update
			push_status = contents_object.update(message,contents)
			return str(push_status['commit'])
		else:#file doesn't exist on remote repo
			#push
			push_status = repository.create_file(path=file_info, message=message.format(file_info),content=contents,)
			return str(push_status['commit'])


def get_git_credentials(user, admin, code):
	global code_2fa
	code_2fa = code
	if admin==0:
		return

	scriptpath = os.path.dirname(os.path.realpath(__file__)) + os.sep + ".." + os.sep
	userdir = scriptpath + "users" + os.sep
	user_dict = ConfigObj(userdir + user + '.ini')

	git_username = user_dict['git_username'] if "git_username" in user_dict else "_"
	git_token = user_dict['git_token'] if "git_token" in user_dict else "_"
	git_use2fa = user_dict['git_2fa'] if "git_2fa" in user_dict else "false"
	return git_username, git_token, git_use2fa

