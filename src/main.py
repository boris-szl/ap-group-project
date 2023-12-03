import pandas as pd
import json
import requests
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup
import re
import math


'''
features to do:
	- data per page
		- locate html tag that displays search results
		- locate page-nav html-tag
		- what is the url-string for page number
			- showpage=2
		- Classes for Jomashop, Relleb, Watchrecon, DubaiLuxuryWatch, Watchbox (JSON Data)
	- implement search for each page to be scraped
'''

class Header:
	def __init__(self):
		self.header = {
		'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.84 Safari/537.36',
		'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
		'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
		'Accept-Encoding': 'none',
		'Accept-Language': 'en-US,en;q=0.8',
		'Connection': 'keep-alive',
		'refere': 'https://www.chrono24.com',
		'cookie': """your cookie value ( you can get that from your web page)"""}

	def getHeader(self):
		return self.header

	def setHeader(self, header):
		self.header = header


class Driver:
	def __init__(self):
		self.service = Service(executable_path=ChromeDriverManager().install())
		self.option = webdriver.ChromeOptions().add_argument('headless')
		self.header = Header().getHeader()

	def getService(self):
		return self.service

	def getOption(self):
		return self.option

	def setDriver(self):
		self.driver = webdriver.Chrome(service=self.getService(), options=self.getOption())

	def getDriver(self):
		return self.driver

class Chronext(Driver):
	def __init__(self):
		super().__init__()
		self.source = "https://www.chronext.ch/search?s%5Bsearch%5D%5Bq%5D="
		self.payload = {}

	# getter and setter

class Gebauer(Driver):
	def __init__(self):
		super().__init__()
		self.source = "https://marcgebauer.com/search?q="
		self.payload = {}

	# setter and getter

class Watchfinder(Driver):
	def __init__(self):
		super().__init__()
		self.source = "https://www.watchfinder.ch/search?q="
		self.payload = {}

def createSoupObject(url : str, header : dict, parser : str) -> BeautifulSoup:
	req = requests.get(url, headers=header)
	assert req.status_code == 200, "Error: Status Code is not 200"
	soup = BeautifulSoup(req.text, parser)
	return soup

class Chrono(Driver):
	def __init__(self):
		super().__init__()
		self.header = Header().getHeader()
		self.source = "https://www.chrono24.com/search/index.htm?"
		self.payload = {'query' : '', 'pageSize' : 120, 'resultview' : 'list', 'showPage' : 1 } # default paylaod´
		self.searchUrl = "&dosearch=true&searchexplain=false&watchTypes=U&accessoryTypes="
		self.parser = "html.parser"

	def getSource(self) -> str:
		return self.source

	def setSource(self, source : str):
		self.source = source

	def getHeader(self) -> dict:
		return self.header

	def setHeader(self, header)	-> None:
		self.header = header

	def getPayload(self) -> dict:
		return self.payload

	def setPayload(self, payload : dict):
		self.payload = payload

	def getSearchUrl(self) -> str:
		return self.searchUrl

	def setSearchUrl(self, url : str):
		self.sarchUrl = url

	def getParser(self) -> str:
		return self.parser

	def setParser(self, parser : str):
		self.parser = parser


	# def getListings(self) -> int:
	# 	parser = "html.parser"
	# 	req = requests.get(self.getUrlSearchResults(self.getPayload()), headers=self.getHeader())
	# 	soup = BeautifulSoup(req.text, parser)
	# 	string3 = soup.find("strong", string=re.compile("listings$"))
	# 	bsObject = BeautifulSoup(str(string3), parser)
	# 	text = bsObject.get_text()
	# 	# return int(re.findall("\\d+", text)[0])
	# 	print(text)

	def getListingSize(self) -> int:
		result = []
		while len(result) == 0:
			soup = createSoupObject(self.getUrlSearchResults(self.getPayload()), self.getHeader(), self.getParser())
			result = soup.find_all("strong", string=re.compile("listings$"))
			if len(result) != 0:
				break
		size : str = result[0].text.split(" ")[0]
		size : int = int(size)
		return size


	def calculatePages(self):
		# calculate pages to be scraped
		results = self.getListingSize()
		pageSize = self.getPayload()['pageSize']
		pages = math.ceil(results / pageSize)
		return pages

	def getUrlSearchResults(self, payload):
		assert len(payload) != 0
		if self.getLenFirstEntry() == 0:
			print("Wich reference you are looking for?\n")
			self.updateQuery(input())
			r = requests.get(self.getSource(), headers=self.getHeader(), params=self.getPayload())
			url = r.url + self.getSearchUrl()
		else:
			r = requests.get(self.getSource(), headers=self.getHeader(), params=self.getPayload())
			url = r.url + self.getSearchUrl()
		return url

	def getLdJson(self) -> dict:
		soup = createSoupObject(self.getUrlSearchResults(self.getPayload()), self.getHeader(), self.getParser())
		return json.loads("".join(soup.find("script", {"type" : "application/ld+json"}).contents))

	def getAllJson(self, max : int) -> dict:
		soup = createSoupObject(self.getUrlSearchResults(self.getPayload()), self.getHeader(), self.getParser())
		return json.loads("".join(soup.find("script", {"type" : "application/ld+json"}).contents))


	def getData(self):
		json = self.getLdJson()

	def loadOffers(self) -> list:
		results = self.getLdJson()
		return results['@graph'][1].get('offers')

	def loadAllOffers(self) -> list:
		results : list = self.loadOffers()
		for i in range(2, self.calculatePages() + 1):
			self.updatePage(i)
			results.append(self.loadOffers())
		return results


	def tableOffersRaw(self):
		dict_data = self.loadOffers()
		return pd.json_normalize(dict_data)

	def tableOffers(self, all : bool = False):
		dict_data = {}
		if all:
			dict_data = self.loadAllOffers()
		else:
			dict_data = self.loadOffers()
		table = pd.json_normalize(dict_data)
		table = table.dropna(axis=0)
		try:
			table['price'] = table['price'].astype(int)
		except KeyError as e:
			print('Price column not available, hence the price is on request')
		return table

	def getLenFirstEntry(self):
		print(len(self.payload.get('query')))

	def updateQuery(self, query):
		self.payload.update({'query' : query})

	def updatePage(self, page):
		self.payload.update({'showPage' : page})

def main():
	chrono = Chrono()
	chrono.getLenFirstEntry()
	print(chrono.getUrlSearchResults(chrono.getPayload()))
	# print(chrono.getPayload())

	# Submariner 126610LN
	chrono.updateQuery("126610LN")
	# chrono.updatePage(2)
	# print(chrono.getUrlSearchResults(chrono.getPayload()))
	# print(chrono.getPayload())
	submariner = chrono.tableOffers(all=False)[['name', 'price']]
	print(submariner)
	print(submariner.describe())
	# print(chrono.getListingSize())
	# print(chrono.calculatePages())

	# daytona
	chrono.updateQuery("116500LN")
	daytona = chrono.tableOffers(all=False)[['name', 'price']]
	print(daytona.describe())


if __name__ == "__main__":
	main()

