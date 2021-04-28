import codelysis,os,json,flask,requests,re,magic,concurrent.futures,uuid,logging
from urllib.parse import urlparse
from flask import request, jsonify, render_template, Response
from lxml.html import parse
from bs4 import BeautifulSoup


class CustomFormatter(logging.Formatter):
    grey = "\x1b[38;21m"
    yellow = "\x1b[33;21m"
    red = "\x1b[31;21m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"
    format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s (%(filename)s:%(lineno)d)"

    FORMATS = {
        logging.DEBUG: grey + format + reset,
        logging.INFO: grey + format + reset,
        logging.WARNING: yellow + format + reset,
        logging.ERROR: red + format + reset,
        logging.CRITICAL: bold_red + format + reset
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)

app = flask.Flask(__name__, static_url_path='')
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
ch.setFormatter(CustomFormatter())
log.addHandler(ch)

app.config["DEBUG"] = True
threads = {}



def getMime(url):
	if url.endswith('css'):
		return 'text/css'
	elif url.endswith('html'):
		return 'text/html'
	elif url.endswith('js'):
		url.endswith('text/javascript')
	elif url.endswith('gif'):
		url.endswith('image/gif')
	return magic.from_file(url, mime=True)

def e_send_from_directory(folder,file):
	with open(str(folder)+'/'+str(file),'rb') as f:
		content = f.read()
		f.close()
	return content 

def get_title(url):
	page = requests.get(url).content

	soup = BeautifulSoup(page,features='lxml')
	return soup.title.string

@app.route('/', methods=['GET'])
def home():
	with open('html/index.html') as f:
		page = f.read()
		f.close()
	return page

@app.errorhandler(404)
def send_static(*args):
	try:
		ret = e_send_from_directory('html', urlparse(request.url).path)
		resp = Response(response=ret,
	                    status=200,
	                    mimetype=getMime('html'+str(urlparse(request.url).path)))
		return resp
	except Exception as e:
		print(f"[*] {e}")
		return Response(response=f'{urlparse(request.url).path} Not Found / 404',
	                    status=404,
	                    mimetype='text/html')

@app.route('/api/v1/get_title', methods=['GET','POST'])
def api_get_title():
	if 'url' in request.args:
		url = request.args['url']
	else:
		print(request.args)
		return {'status':1,'msg':'Error: No url field provided. Please specify a url.'}

	page = requests.get(url).content

	soup = BeautifulSoup(page,features='lxml')
	return soup.title.string



def analyse(code,jobid):
	threads[jobid]['status'] = 'Analysing'
	error,trace = codelysis.analyse(code,jobid)

	threads[jobid]['status'] = 'Finished Analysis'
	print(f"[*] Finished Analysis for ({jobid})")

	broken=None
	lineno=None
	filename=None
	if len(error) < 1:
		print('[*] codes works perfectly fine')
		print(f"[*] Api Finished for ({jobid})")
		return {'status':0,'broken':False,'links':None,'query':None,'error':None,'lineno':None}
	else:
		threads[jobid]['status'] = 'Fetching Links'
		links,query = codelysis.getlinks(error,template='stackoverflow.com') #1 == accurate
		print(f"[*] Finished Link Retrieval for ({jobid})")
		broken = True
		lineno = trace['lineno']
		filename = trace['filename']


	linksdetails = []

	if links[0]['title'] == '':
		for i in links:
			title = get_title(i)
			url = i
			source = re.search(":\/\/(.[^/]+).com|.net|.co.uk|.ie|.fr|.co|.org|.gov.edu|.net",url).group(1)
			linksdetails.append({'title':title,'url':url,'source':source})
	else:
		for i in links:
			title = i['title']
			url = i['link']
			source = re.search(":\/\/(.[^/]+).com|.net|.co.uk|.ie|.fr|.co|.org|.gov.edu|.net",url).group(1)
			linksdetails.append({'title':title,'url':url,'source':source})

	# Use the jsonify function from Flask to convert our list of
	# Python dictionaries to the JSON format.

	threads[jobid]['status'] = 'Done'
	print(f"[*] Api Finished for ({jobid})")
	return {'status':0,'broken':broken,'links':linksdetails,'query':query,'error':error,'lineno':lineno}

@app.route('/api/v1/analyse', methods=['GET','POST'])
def api_analyse():
	# Check if an ID was provided as part of the URL.
	# If ID is provided, assign it to a variable.
	# If no ID is provided, display an error in the browser.
	if 'code' in request.args:
		code = request.args['code']
	else:
		print(request.args)
		return {'status':1,'msg':'Error: No code field provided. Please specify a Python Script.'}

	#geeksforgeeks.org
	#www.stechies.com
	#stackoverflow.com
	#www.programiz.com

	executor = concurrent.futures.ThreadPoolExecutor() 
	jobid = str(uuid.uuid4().hex)[:10]
	print(f"\n\n[*] Started New Job (JOBID = {jobid})")
	threads[jobid] = {}
	threads[jobid]['status'] = 'Starting...'
	threads[jobid]['instance'] = executor.submit(analyse, code, jobid)
	return {'status':0,'job':jobid}


@app.route('/api/v1/job_status',methods=['GET','POST'])	
def job_done():
	if 'id' in request.args:
		jobid = request.args['id']
	else:
		print(request.args)
		return {'status':1,'msg':'Error: No id field provided. Please specify a job id.'}

	if threads[jobid]['instance'].done():
		return {'status':'Finished','msg':'Done'}
	return {'status':'Running','msg':threads[jobid]['status']}

@app.route('/api/v1/job_result',methods=['GET','POST'])	
def job_result():
	if 'id' in request.args:
		jobid = request.args['id']
	else:
		print(request.args)
		return {'status':1,'msg':'Error: No id field provided. Please specify a job id.'}

	future = threads[jobid]['instance']
	return future.result()

app.run(host='0.0.0.0', port=8080)
