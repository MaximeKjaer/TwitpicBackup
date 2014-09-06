import os
import zipfile
import csv
import re
import urllib.request
from lxml import html

#Copied from https://stackoverflow.com/questions/12886768/simple-way-to-unzip-file-in-python-on-all-oses
def unzip(source_filename, dest_dir):
	with zipfile.ZipFile(source_filename) as zf:
		for member in zf.infolist():
			# Path traversal defense copied from
			# http://hg.python.org/cpython/file/tip/Lib/http/server.py#l789
			words = member.filename.split('/')
			path = dest_dir
			for word in words[:-1]:
				drive, word = os.path.splitdrive(word)
				head, word = os.path.split(word)
				if word in (os.curdir, os.pardir, ''): continue
				path = os.path.join(path, word)
			zf.extract(member, path)

def fetch_picture(url, timestamp):
	try:
		f = html.fromstring(urllib.request.urlopen(url).read())
		print('   Downloading', url)
		src = f.xpath('//*[@id="media-full"]/img/@src')[0]
		image = urllib.request.urlopen(src).read()
		with open('images/' + timestamp[:10] + '--' + url.split('/')[-2] + '.jpg', 'wb') as imgf:
			imgf.write(image)
	except urllib.error.HTTPError:
		print('  ', url, 'no longer exists :(')


def find_twitpics(csv_file):
	with open(csv_file) as f:
		reader = csv.DictReader(f)
		regex = re.compile(r'twitpic\.com\/.*?\ ', re.IGNORECASE)
		for line in reader:
			match = regex.search(line['text'])
			if match:
				picURL = 'http://' + match.group()[:-1] + '/full' #removing that last space + link without ads.
				timestamp = line['timestamp']
				fetch_picture(picURL, timestamp)




if os.path.isfile('tweets.zip'):
	print('Archive file found. We can now initiate the backup for ALL tweets.')
	print('[+] Unzipping tweets.zip')
	unzip('tweets.zip', 'tweets')
	print('[+] Creating "images" folder')
	if not os.path.exists('images'):
    		os.makedirs('images')
	print('[+] Loading all tweets')
	twitpics = find_twitpics('tweets/tweets.csv')

	print('[+] Done.')
else:
	print('No tweets.zip file found :(')
	print('You can download it from the following link: \n ')
	print('        https://twitter.com/settings/account \n ')
	print('Once you\'ve downloaded it, place it in this folder and run the script again.')

