import os,sys,pickle
def logtrace(msg,trace):
	msg = str(msg)
	if trace['filename'] == '/oroot/user.py':
		trace['filename'] = 'main.py'
	with open('codelysis-trace.log','wb') as f:
		content = [msg,trace]
		pickle.dump(content, f)
		f.close()

def input(*kwargs):
	return '2'
def fake_input(*kwargs):
	return '2'
input = fake_input
__name__ = '__main__'
try:
	import user
except Exception as e:

	trace = []
	tb = e.__traceback__
	while tb is not None:
		trace.append({
			"filename": tb.tb_frame.f_code.co_filename,
			"name": tb.tb_frame.f_code.co_name,
			"lineno": tb.tb_lineno
		})
		tb = tb.tb_next

	exc_type, exc_obj, exc_tb = sys.exc_info()
	fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
	if hasattr(e, 'message'):
		string = str(exc_type.__name__)+' '+getattr(e, 'message', str(e))
		logtrace(string.split('(')[0],trace[1])
		#linetrace(sys.exc_info()[-1].tb_lineno)
	else:
		try:
			logtrace(f'{str(exc_type.__name__)} {e}',trace[1])
		except:
			logtrace(f'{str(exc_type.__name__)} {e}',trace[0])