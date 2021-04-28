import codelysis,os,json,flask,requests,re,magic,concurrent.futures,uuid
from urllib.parse import urlparse
from flask import request, jsonify, render_template, Response
from lxml.html import parse
from bs4 import BeautifulSoup

app = flask.Flask(__name__, static_url_path='')
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
		print(getMime('html'+str(urlparse(request.url).path)))
		return resp
	except Exception as e:
		print(e)
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



def analyse(code):
	error,trace = codelysis.analyse(code)

	links,query = codelysis.getlinks(error,template='stackoverflow.com') #1 == accurate

	broken=None
	lineno=None
	filename=None
	if len(error) < 1:
		broken = False
		print('codes works perfectly fine')
	else:
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
	threads[jobid] = executor.submit(analyse, code)
	return {'status':0,'job':jobid}


@app.route('/api/v1/job_status',methods=['GET','POST'])	
def job_done():
	if 'id' in request.args:
		jobid = request.args['id']
	else:
		print(request.args)
		return {'status':1,'msg':'Error: No id field provided. Please specify a job id.'}

	if threads[jobid].done():
		return {'status':'Finished'}
	return {'status':'Running'}

@app.route('/api/v1/job_result',methods=['GET','POST'])	
def job_result():
	if 'id' in request.args:
		jobid = request.args['id']
	else:
		print(request.args)
		return {'status':1,'msg':'Error: No id field provided. Please specify a job id.'}

	future = threads[jobid]
	return future.result()

app.run()
