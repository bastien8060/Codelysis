import codelyse,os,json,flask,requests,re
from flask import request, jsonify
from lxml.html import parse
from bs4 import BeautifulSoup

app = flask.Flask(__name__)
app.config["DEBUG"] = True



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

	error,trace = codelyse.analyse(code)

	links,query = codelyse.getlinks(error,template='stackoverflow.com') #1 == accurate

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

	for i in links:
		title = get_title(i)
		url = i
		source = re.search(":\/\/(.[^/]+).com|.net|.co.uk|.ie|.fr|.co|.org|.gov.edu|.net",url).group(1)
		linksdetails.append({'title':title,'url':url,'source':source})

	# Use the jsonify function from Flask to convert our list of
	# Python dictionaries to the JSON format.
	return {'status':0,'broken':broken,'links':linksdetails,'query':query,'error':error,'lineno':lineno}

app.run()
