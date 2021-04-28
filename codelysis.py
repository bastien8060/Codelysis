import pty, sys, select, os, subprocess, random, re, pickle,json,requests
from googlesearch import search
from googleapiclient.discovery import build

from apiconfigs import getkeys

keys = getkeys()

def google_search(search_term, api_key, cse_id, **kwargs):
    service = build("customsearch", "v1", developerKey=api_key)
    res = service.cse().list(q=search_term, cx=cse_id, **kwargs).execute()
    return res['items']

def serp(query):
	ret = []
	try:
		received = Falsef
		attempts = 0
		for key in keys['scaleserp']['keys']:
			try:
				print(f'trying {key}')
				s = json.loads(requests.get(f'https://api.scaleserp.com/search?api_key={key}&q={query}&hl=en').content.decode())
				if 'organic_results' not in s:
					print("0 Results")
					return []
				for i in s['organic_results']:
					ret.append({'title':i['title'],'link':i['link']})
					received = True
				return ret
			except Exception as e:
				print(f'Dropped Serp api key {attempts} for')
				print(e)
				print(s)
				attempts += 1
				pass
		if received == False:
			raise Exception('No Serp api keys worked.')
	except:
		print('No Serp api keys worked.')
		try:
			service = build("customsearch", "v1", developerKey=keys['gsearch']['api_key'])
			res = service.cse().list(q=query, cx=keys['gsearch']['cse_id'], num=10).execute()
			#print(res['items'])
			res = res['items']
			for i in res:
				if len(ret) < 10: 
					ret.append({'link':i['link'],'title':i['title']})
		except:
			print('Google Api Key down')
			res = search(query, num=10, stop=10, pause=2,user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36")
			for i in res:
				ret.append({'link':i,'title':i})
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
		os.makedirs(f"/tmp/pysess/{sess}/main/") 
	except:
		pass
	with open(f'/tmp/pysess/{sess}/main/user.py','w') as f:
		f.write(pythoncode)
		f.close()
	try:
		try:
			subprocess.run([f"cd /tmp/pysess/{sess}/main/;screen pipreqs"], check = True)
		except subprocess.CalledProcessError:
			print (f'pipreqs does not exist')
		requirement_file = open (f'/tmp/pysess/{sess}/main/requirements.txt', 'r' )
		content = requirement_file.read()
		contents = re.sub(r"==.*$", "", content, flags = re.M)
		print(contents)
		requirement_file.close()
		requirement_file = open (f'/tmp/pysess/{sess}/main/requirements.txt', 'w')
		requirement_file.write(contents)
		requirement_file.close()
	except:
		pass
	with open(f'/tmp/pysess/{sess}/main/main.py','w') as f:
		f.write(wrapper)
		f.close()
	with open(f'/tmp/pysess/{sess}/main/run.sh','w') as f:
		f.write(run_sh)
		f.close()
		os.system(f'chmod 777 /tmp/pysess/{sess}/main/run.sh')
	with open(f"/tmp/pysess/{sess}/output.log", "a") as output:
		try:
			subprocess.call(f'bash -c "timeout 180 docker run -w /tmp --cpus=0.25 -v /tmp/pysess/{sess}/main:/tmp --ulimit rtprio=19 --memory=300M --cap-add=sys_nice --rm -it {container} /tmp/run.sh"', shell=True, stdin=tty, stdout=output, stderr=output)
		except:
			pass
		try:
			trace = pickle.load(open(f'/tmp/pysess/{sess}/main/codelysis-trace.log','rb'))
			error = trace[0]
			stacktrace = trace[1]

			print(trace)
			
		except Exception as e:
			print(e)
			return '',0


		return error,stacktrace
