import pandas as pd
import json
import requests
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup
import re
import math

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

	def getHeader(self) -> dict:
		return self.header

	def setHeader(self, header) -> None:
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

	def setHeader(self, header : dict)	-> None:
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

	def getListingSize(self) -> int:
		result = []
		while len(result) == 0:
			soup = createSoupObject(self.getUrlSearchResults(self.getPayload()), self.getHeader(), self.getParser())
			result = soup.find_all("strong", string=re.compile("listings$"))
			if len(result) != 0:
				break
		if result:
			size_str = result[0].text.split(" ")[0]
			size_str = size_str.replace(',', '')  # Remove commas from the string
			return int(size_str)
		else:
			return 0  # Return 0 if no listing size found

	def calculatePages(self) -> int:
		results = self.getListingSize()
		if results is None or results == 0:
			return 0  # Return 0 to indicate no pages to process
		pageSize = self.getPayload()['pageSize']
		pages = math.ceil(results / pageSize)
		return pages

	def getUrlSearchResults(self, payload : dict):
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
			print(dict_data)
		table = pd.json_normalize(dict_data)
		table = table.dropna(axis=0)
		try:
			table['price'] = table['price'].astype(int)
		except KeyError as e:
			print('Price column not available, hence the price is on request')
		return table

	def getLenFirstEntry(self) -> int:
		return len(self.payload.get('query'))

	def updateQuery(self, query : str) -> None:
		self.payload.update({'query' : query})

	def updatePage(self, page : int) -> None:
		self.payload.update({'showPage' : page})

class Menu:
    def __init__(self):
        self.choice = None

    def display_options(self) -> None:
        print("Choose your search type:")
        print("1. Search by Model Name")
        print("2. Search by Reference Number")

    def get_user_choice(self) -> bool:
        self.choice = input("Enter your choice (1 or 2): ").strip()
        return self.validate_choice()

    def validate_choice(self) -> bool:
        return self.choice in ['1', '2']

    def get_search_input(self) -> str:
        if self.choice == '1':
            return input("Enter the model name (e.g. Daytona or Cartier Santos): ")
        elif self.choice == '2':
            return input("Enter the reference number (e.g. 126610LN): ")
        return ""

    def get_data_retrieval_choice(self) -> bool:
        data_choice = input("Do you want to retrieve all data? (yes for all data / no for first page only): ").strip().lower()
        return data_choice == 'yes'

    def get_save_csv_choice(self) -> str:
        save_csv = input("Do you want to save this data in a CSV file? (yes/no): ").strip().lower()
        if save_csv == 'yes':
            filename = input("Enter a filename for the CSV (without extension): ").strip()
            return filename if filename else "watch_data"
        return ""

    def ask_to_continue(self) -> bool:
        continue_search = input("Do you want to search for another watch? (yes/no): ").strip().lower()
        return continue_search == 'yes'

def main() -> None:
    chrono = Chrono()
    menu = Menu()

    while True:
        menu.display_options()
        if not menu.get_user_choice():
            print("Invalid choice. Please enter 1 or 2.")
            continue

        search_input = menu.get_search_input()
        if search_input:
            chrono.updateQuery(search_input)

            all_data = menu.get_data_retrieval_choice()
            watch_data = chrono.tableOffers(all=all_data)[['name', 'price']]
            print(watch_data)
            print(watch_data.describe())

            filename = menu.get_save_csv_choice()
            if filename:
                watch_data.to_csv(filename + '.csv', index=False)
                print(f"Data saved to {filename}.csv")
        else:
            print("No valid input provided.")
            continue

        if not menu.ask_to_continue():
            break

if __name__ == "__main__":
    main()

