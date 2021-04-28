import pty, sys, select, os, subprocess, random, re, pickle,json,requests
from pathlib import Path
from googlesearch import search
from googleapiclient.discovery import build
from bs4 import BeautifulSoup

from apiconfigs import getkeys

home = str(Path.home())
keys = getkeys()

def google_search(search_term, api_key, cse_id, **kwargs):
    service = build("customsearch", "v1", developerKey=api_key)
    res = service.cse().list(q=search_term, cx=cse_id, **kwargs).execute()
    return res['items']

def get_title(url):
	page = requests.get(url).content
	soup = BeautifulSoup(page,features='lxml')
	return soup.title.string

def googlesearchapi(query):
	ret = []
	for apikey in keys['gsearch']:
		try:
			service = build("customsearch", "v1", developerKey=apikey['api_key'])
			res = service.cse().list(q=query, cx=apikey['cse_id'], num=10).execute()
			if res['searchInformation']['totalResults'] == '0':
				return []
			for i in res['items']:
				ret.append({'api':'gapi','link':i['link'],'title':i['title']})
			return ret
		except Exception as e:
			print(f'\n\n\n{e}\n\n\n')
	raise Exception('No Google api keys worked.')

def serp(query):
	ret = []
	try:
		return googlesearchapi(query)
	except Exception as e:
		print(e)
		res = search(query, num=10, stop=10, pause=2,user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36")
		for i in res:
			ret.append({'link':i,'title':get_title(i)})
		return ret


pty, tty = pty.openpty()
container = 'codelysis/linuxalpine'

with open('src/wrapper.py') as f:
	wrapper = f.read()
	f.close()

with open('src/run.sh') as f:
	run_sh = f.read()
	f.close()

def getlinks(error,template=0):
	results = []
	if template == 0:
		query = f'python3 {error} site:stackoverflow.com'
	elif template == 1:
		error = error.replace('"',"'")
		query = f'python3 "{error}" site:stackoverflow.com'
	else:
		query = f'python3 {error} site:{template}'
	for j in serp(query):
		results.append(j)
	if len(results) == 0:
		query = re.sub('\'[^>]+\'', '', query)
		for j in serp(query):
			results.append(j)
	i = 0
	return results,query


def sessid(length):
    return random.randint(10**(length-1), 10**length-1)

def analyse(pythoncode):
	sess = sessid(5)
	print(sess)
	try:
		os.makedirs(f"{home}/.tmp/pysess/{sess}/main/") 
	except:
		pass
	with open(f'{home}/.tmp/pysess/{sess}/main/user.py','w') as f:
		f.write(pythoncode)
		f.close()
	try:
		try:
			subprocess.run([f"cd {home}/.tmp/pysess/{sess}/main/;screen pipreqs"], check = True)
		except subprocess.CalledProcessError:
			print (f'pipreqs does not exist')
		requirement_file = open (f'{home}/.tmp/pysess/{sess}/main/requirements.txt', 'r' )
		content = requirement_file.read()
		contents = re.sub(r"==.*$", "", content, flags = re.M)
		print(contents)
		requirement_file.close()
		requirement_file = open (f'{home}/.tmp/pysess/{sess}/main/requirements.txt', 'w')
		requirement_file.write(contents)
		requirement_file.close()
	except:
		pass
	with open(f'{home}/.tmp/pysess/{sess}/main/main.py','w') as f:
		f.write(wrapper)
		f.close()
	with open(f'{home}/.tmp/pysess/{sess}/main/run.sh','w') as f:
		f.write(run_sh)
		f.close()
		os.system(f'chmod 777 {home}/.tmp/pysess/{sess}/main/run.sh')
	with open(f"{home}/.tmp/pysess/{sess}/output.log", "a") as output:
		try:
			subprocess.call(f'bash -c "timeout 180 docker run -w /oroot --cpus=0.25 -v {home}/.tmp/pysess/{sess}/main/:/oroot --ulimit rtprio=19 --memory=300M --cap-add=sys_nice --rm -it {container} /oroot/run.sh"', shell=True, stdin=tty, stdout=output, stderr=output)
		except:
			pass
		try:
			trace = pickle.load(open(f'{home}/.tmp/pysess/{sess}/main/codelysis-trace.log','rb'))
			error = trace[0]
			stacktrace = trace[1]

			print(trace)
			
		except Exception as e:
			print(e)
			return '',0


		return error,stacktrace
