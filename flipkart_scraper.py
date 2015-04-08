from bs4 import BeautifulSoup
import requests
import re
import types
import sys
import pprint
pretty = pprint.pprint
from pymongo import MongoClient
import json
MongoClient = MongoClient('localhost', 27017)
db = MongoClient.your_staging

# url  = 'http://www.flipkart.com/zovi-regular-fit-royal-blue-mandarin-collar-men-s-solid-casual-shirt/p/itme39qwnzwee2yw?pid=SHTE39QWRUMP4TGN&otracker=from-search&srno=t_4&query=blue+slim+fit+shirt&al=ZBnCKGhnMIgkHAarHVMwafxFDk0ZSRnqbTZeROZWkom1%2Bm1l8trCtIaLq2lx4bRfFLwHQxVDMNU%3D&ref=7fb0dcf8-1e36-427c-bd69-20b35564fe62'

def runner():
	products = db.flipkart_products.find({"provider": "Flipkart", "category_head": "mens_clothing"})
	for product in products:
		scrape(product['link'])

def collapse(s):
	return " ".join(s.split())

def scrape(url):

	try:
		r = requests.get(url)
		soup = BeautifulSoup(r.content)


		try:
			title = soup.find_all("h1", attrs={"class":"title"})[0].text
		except:
			# print "error parsing title", sys.exc_info()[0]
			title =  ""

		try:
			description = collapse(soup.find_all(attrs={"class":"description-text"})[0].text)
		except:
			# print "error parsing description", sys.exc_info()[0]
			description =  ""

		try:	
			selling_price = soup.find_all(attrs={"class": "selling-price omniture-field"})[0].text
		except:
			# print"error parsing selling-price", sys.exc_info()[0]
			selling_price =  ""

		try:
			mrp = soup.find_all(attrs={"class": "price"})[0].text
		except:
			# print "error parsing mrp", sys.exc_info()[0]
			mrp =  ""

		try:
			discount = soup.find_all(attrs={"class": "discount fk-green"})[0].text
		except:
			# print "error parsing discount", sys.exc_info()[0]
			discount =  ""


		regex_for_size = re.compile("Select Size")

		try:
			size = soup.find(text=regex_for_size)
			size = size.parent.findNextSibling()
			sizes = list(size.children)
			sizes = [size for size in sizes if str(size).strip()]
			sizes = [collapse(size.text) for size in sizes]
		except:
			# print "error parsing size info", sys.exc_info()[0]
			sizes =  ""

		specifications = {}
		try:
			specTables = soup.find_all("table", attrs={"class": "specTable"})
			for specTable in specTables:
				keys = specTable.find_all("td", attrs={"class": "specsKey"})
				values = specTable.find_all("td", attrs={"class": "specsValue"})
				keys = [collapse(key.text) for key in keys]
				values = [collapse(value.text) for value in values]
				specifications = dict(specifications.items() + dict(zip(keys,values)).items())
		except:
			pass
			# print "error parsing specifications", sys.exc_info()[0]

		scraped_info = {
			"title": title,
			"description": description,
			"sizes": sizes,
			"mrp": mrp,
			"selling_price": selling_price,
			"discount": discount,
			"specifications": specifications
		}

		print json.dumps(scraped_info)

	except:
		pass
		# print "error fetching page", sys.exc_info()[0]

if __name__ == "__main__":
	if len(sys.argv) > 1:
		url = sys.argv[1]
		scrape(url)
	else:
		url = raw_input("please paste a url to parse : ")
		scrape(url)