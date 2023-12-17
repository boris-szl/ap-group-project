import pandas as pd
import json
import requests
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup
import re
import math
import sys
import threading
import time

# Web Scraping Program for Chrono24 Luxury Watches
# This program uses Selenium WebDriver for automated web browsing, BeautifulSoup for HTML parsing,
# and pandas for data manipulation and CSV file handling. It's designed to scrape watch data from
# the Chrono24 website based on user inputs, offering functionalities to search by model or reference number,
# retrieve data from specific or all pages, and save the collected data into a CSV file. The architecture 
# includes classes for managing HTTP headers, WebDriver setup, and user interactions, along with a main function 
# to orchestrate the overall workflow.

# The architecture of the program is centered around modular classes:
# - Header: Manages HTTP headers to simulate genuine browser requests and avoid bot detection.
# - Driver: Configures and controls the Selenium WebDriver with headless browsing capabilities.
# - Chrono: Inherits from Driver and is tailored to interact specifically with the Chrono24 website. It handles search queries, pagination, data retrieval, and parsing.
# - Menu: Provides a user interface via the console for inputting search criteria, choosing data retrieval options, and deciding on data export.
#
# The main function serves as the application's entry point, coordinating the sequence of operations:
# - User inputs for search criteria.
# - Scraping watch data based on these inputs.
# - Offering options to save the data to CSV.
# - Looping the process for multiple searches until the user opts to exit.
# This design ensures a user-friendly and versatile tool for collecting watch data from a specialized online marketplace.

class Header:
	"""
	Manages HTTP headers for web scraping requests, essential for simulating a web browser's request pattern. 
	Proper headers can help in reducing the likelihood of being detected as a bot by web servers.

	Attributes:
		header (dict): A dictionary containing key-value pairs of HTTP header fields typically found in browser requests.
	"""
	def __init__(self):
		"""
		Initializes the Header object with default HTTP headers. These headers imitate a typical web browser's request, 
		which includes fields like User-Agent, Accept, Accept-Language, etc. This setup is crucial to make requests 
		appear more natural and less likely to be blocked by web servers.

		The 'cookie' field is set to a placeholder value and should be updated based on actual cookie data 
		from a web page if necessary.
		"""
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
		"""
		Retrieves the current set of HTTP headers.

		Returns:
			dict: The dictionary of current HTTP headers, which are used in web scraping requests.
		"""
		return self.header

	def setHeader(self, header) -> None:
		"""
		Allows for the modification and updating of the HTTP headers.

		Parameters:
			header (dict): A dictionary containing the new HTTP headers to be used. This is useful for customizing 
			headers based on specific requirements or changes in the target website's response to requests.
		"""
		self.header = header


class Driver:
	"""
	Manages the Selenium WebDriver for automated web interactions, specifically for web scraping tasks.

	This class sets up and configures a Selenium WebDriver, which is an automated web browser used 
	for navigating web pages, interacting with web elements, and extracting web content. It is particularly
	useful for dynamic websites where content is loaded asynchronously or through JavaScript execution.

	Attributes:
		service (Service): The service object used to manage the ChromeDriver, which is the WebDriver for Google Chrome.
		option (webdriver.ChromeOptions): Configuration options for the Chrome WebDriver.
		header (dict): HTTP headers to use for the WebDriver's requests, obtained from the Header class.
	"""
	def __init__(self):
		"""
		Initializes the WebDriver for Google Chrome with necessary configurations.

		The initialization includes:
			- Setting up the ChromeDriver service using ChromeDriverManager, which ensures the correct driver version.
			- Configuring the WebDriver to run in 'headless' mode, meaning it operates without opening a graphical user interface.
			- Retrieving and setting the default HTTP headers for requests, ensuring the WebDriver's requests mimic those of a regular web browser.
		"""
		self.service = Service(executable_path=ChromeDriverManager().install())
		self.option = webdriver.ChromeOptions().add_argument('headless')
		self.header = Header().getHeader()

	def getService(self):
		"""
		Retrieves the service object used by the WebDriver.
		Returns:
			Service: The service object for the WebDriver.
		"""
		return self.service

	def getOption(self):
		"""
		Retrieves the options set for the Chrome WebDriver.
		Returns:
			webdriver.ChromeOptions: The options for the WebDriver.
		"""
		return self.option

	def setDriver(self):
		"""
		Creates a new instance of the Chrome WebDriver with the specified service and options.
		"""
		self.driver = webdriver.Chrome(service=self.getService(), options=self.getOption())

	def getDriver(self):
		"""
		Retrieves the current instance of the WebDriver.
		Returns:
		    webdriver.Chrome: The current WebDriver instance.
		"""
		return self.driver


def createSoupObject(url : str, header : dict, parser : str) -> BeautifulSoup:
	"""
	Fetches a webpage at the specified URL with the provided headers and creates a BeautifulSoup object for parsing.
	Parameters:
		url (str): URL of the webpage to be fetched.
		header (dict): HTTP headers for the request.
		parser (str): Parser to be used by BeautifulSoup.
	Returns:
		BeautifulSoup: An object to parse and navigate the HTML structure of the page.
	"""
	req = requests.get(url, headers=header)
	assert req.status_code == 200, "Error: Status Code is not 200"
	soup = BeautifulSoup(req.text, parser)
	return soup

class Chrono(Driver):
	"""
	Extends the Driver class to include specific functionalities for interacting with and scraping 
	data from the Chrono24 website, a platform for buying and selling luxury watches.

	Attributes:
		header (dict): HTTP headers to be used in requests.
		source (str): Base URL for the Chrono24 search queries.
		payload (dict): Default parameters for search queries, including query text, page size, and other settings.
		searchUrl (str): Additional URL parameters to be appended to the base URL for search queries.
		parser (str): Specifies the parser to be used with BeautifulSoup for parsing HTML content.
	"""
	def __init__(self):
		"""
		Initializes the Chrono object with default settings specific to scraping data from the Chrono24 website.

		This initialization includes setting up the base URL for searches, default payload parameters for search queries,
		additional search URL parameters, and the HTML parser to be used. The inherited Driver class is also initialized
		to set up the WebDriver with appropriate configurations.
		"""
		super().__init__()
		self.header = Header().getHeader()
		self.source = "https://www.chrono24.com/search/index.htm?"
		self.payload = {'query' : '', 'pageSize' : 120, 'resultview' : 'list', 'showPage' : 1 } # default paylaod´
		self.searchUrl = "&dosearch=true&searchexplain=false&watchTypes=U&accessoryTypes="
		self.searchUrl = "&dosearch=true&searchexplain=false&watchTypes=U&accessoryTypes="
		self.parser = "html.parser"

	def getSource(self) -> str:
		"""
		Retrieves the base source URL for Chrono24 searches.

		This method is useful for accessing the base URL for forming search queries. It returns the URL
		set during initialization, which is used as the starting point for all search-related requests.

		Returns:
			str: The base URL used for Chrono24 search queries.
		"""
		return self.source

	def setSource(self, source : str):
		"""
		Updates the base source URL for Chrono24 searches.

		This method allows changing the base URL used for forming search queries. It can be used to 
		dynamically alter the starting point for search-related requests depending on the requirements.

		Parameters:
			source (str): The new base URL to be used for Chrono24 search queries.
		"""
		self.source = source


	def getHeader(self) -> dict:
		"""
		Retrieves the current HTTP headers being used for web requests.

		Returns:
			dict: A dictionary containing the current HTTP headers.
		"""
		return self.header

	def setHeader(self, header : dict)	-> None:
		"""
		Sets new HTTP headers for the web requests.

		This method allows the modification of HTTP headers used in requests, which can be 
		useful for customizing request behavior or for adapting to changes in web server policies.

		Parameters:
			header (dict): A dictionary containing the new HTTP headers to be set.
		"""
		self.header = header

	def getPayload(self) -> dict:
		"""
		Retrieves the current payload (parameters) used for search queries.

		Returns:
			dict: A dictionary representing the current search query parameters.
		"""
		return self.payload

	def setPayload(self, payload : dict):
		"""
		Updates the search query payload.

		This method allows changing the parameters used in the search queries, such as the query text, 
		page size, and other settings. It's useful for dynamically altering search criteria.

		Parameters:
			payload (dict): A dictionary containing the new search query parameters to be set.
		"""
		self.payload = payload

	def getSearchUrl(self) -> str:
		"""
		Retrieves additional URL parameters used in search queries.

		Returns:
			str: A string containing additional parameters to be appended to the base URL during searches.
		"""
		return self.searchUrl

	def setSearchUrl(self, url : str):
		"""
		Sets new additional URL parameters for search queries.

		This method allows customizing the extra parameters that are appended to the base URL during searches. 
		It can be used to refine search criteria or to adapt to changes in the website's search feature.

		Parameters:
			url (str): A string representing the new additional search URL parameters.
		"""
		self.sarchUrl = url

	def getParser(self) -> str:
		"""
		Retrieves the parser being used by BeautifulSoup.

		Returns:
			str: The name of the parser used for parsing HTML content in BeautifulSoup.
		"""
		return self.parser

	def setParser(self, parser : str):
		"""
		Sets a new parser for BeautifulSoup.

		This method allows changing the parser used by BeautifulSoup for HTML content parsing. 
		Different parsers may be used based on performance or compatibility considerations.

		Parameters:
			parser (str): The name of the new parser to be used in BeautifulSoup.
		"""
		self.parser = parser

	def getListingSize(self) -> int:
		"""
		Determines the total number of listings available for the current search query on the Chrono24 website.

		This method fetches the search results page using 'createSoupObject', which returns a BeautifulSoup
		object. It then searches for an HTML element (specified by a 'strong' tag) that contains the text
		indicating the number of listings. The method extracts this number, removes any commas for correct
		parsing, and converts it to an integer.

		If the method cannot find the number of listings (e.g., due to changes in the website's HTML structure),
		it defaults to returning 0.

		Returns:
			int: The total number of listings for the current search query. Returns 0 if the number cannot be found.
		"""
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
		"""
		Calculates the total number of pages of search results based on the total number of listings.

		This method first calls 'getListingSize' to determine the total number of listings. It then divides
		this number by the 'pageSize' (number of listings per page) set in the payload, rounding up to the
		nearest whole number. This calculation gives the total number of pages needed to display all listings.

		If 'getListingSize' returns 0 or None (indicating no listings are found or an error in fetching the 
		listing size), this method returns 0, indicating there are no pages of results to process.

		Returns:
			int: The total number of pages required to display all search results. Returns 0 if no listings are found.
		"""
		results = self.getListingSize()
		if results is None or results == 0:
			return 0  # Return 0 to indicate no pages to process
		pageSize = self.getPayload()['pageSize']
		pages = math.ceil(results / pageSize)
		return pages

	def getUrlSearchResults(self, payload : dict):
		"""
		Constructs and retrieves the full URL for the search results based on the given payload.

		This method first checks if there is an existing query in the payload. If not, it prompts the
		user to input a reference or model name, which is then added to the payload. It then makes
		a GET request to the source URL with the updated payload to construct the full URL for search results.

		Parameters:
			payload (dict): The search parameters to be included in the query.

		Returns:
			str: The full URL containing the search results.

		Raises:
			AssertionError: If the payload is empty.
		"""
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
		"""
		Retrieves JSON-LD (JavaScript Object Notation for Linked Data) structured data from the search results page.

		This method uses the BeautifulSoup library to parse the HTML content of the search results page.
		It specifically looks for a <script> tag with type 'application/ld+json', which contains structured
		data in JSON format. This is common in web pages for providing structured data to search engines
		and other crawlers.

		Returns:
			dict: A dictionary representing the parsed JSON-LD content from the page.
		"""
		soup = createSoupObject(self.getUrlSearchResults(self.getPayload()), self.getHeader(), self.getParser())
		return json.loads("".join(soup.find("script", {"type" : "application/ld+json"}).contents))

	def getData(self):
		"""
		Retrieves structured JSON data from the search results page of the Chrono24 website.

		This method acts as a wrapper around the 'getLdJson' method. It calls 'getLdJson' to fetch 
		and parse the JSON-LD structured data embedded in the search results page. The JSON-LD format 
		is typically used by websites to organize and link structured data so that it is easily 
		discoverable by search engines and other applications.

		The primary use of this method could be to simplify the external interface of the class by 
		providing a clear and concise method name for fetching data, abstracting away the specifics 
		of the JSON-LD extraction.

		Returns:
			dict: A dictionary representing the JSON-LD structured data extracted from the search results page.
		"""
		json = self.getLdJson()

	def loadOffers(self) -> list:
		"""
		Retrieves the list of offers from the current search results page.

		This method utilizes 'getLdJson' to fetch structured JSON data from the webpage,
		specifically extracting the offers section. The method navigates through the JSON 
		structure to find the offers listed under the '@graph' key. It is particularly used 
		for extracting offer data from a single page of search results.

		Returns:
			list: A list containing the offers extracted from the current page. Each offer is represented 
			as a dictionary within this list.
		"""
		results = self.getLdJson()
		return results['@graph'][1].get('offers')

	def loadAllOffers(self) -> list:
		"""
		Collects offers from all available pages of search results.

		The method iterates through each page of search results, starting from the second page 
		(as it assumes the first page's offers are already loaded). For each page, it updates 
		the search query to fetch offers and appends them to a cumulative list. This method is 
		useful for scenarios where a complete dataset of offers from all pages is required.

		Returns:
			list: A consolidated list containing offers from all pages. Each offer is a dictionary.
		"""
		results : list = self.loadOffers()
		for i in range(2, self.calculatePages() + 1):
			self.updatePage(i)
			results.append(self.loadOffers())
		return results

	def tableOffersRaw(self):
		"""
		Converts the list of offers into a raw pandas DataFrame.

		This method first retrieves the offers using the 'loadOffers' method. It then uses 
		pandas' 'json_normalize' to convert the list of dictionary objects (offers) into a DataFrame 
		for easier analysis and manipulation. The DataFrame format is useful for data analysis tasks,
		allowing application of various data transformation and filtering operations.

		Returns:
			pandas.DataFrame: A DataFrame containing the raw offer data.
		"""
		dict_data = self.loadOffers()
		return pd.json_normalize(dict_data)

	def tableOffers(self, all : bool = False):
		"""
		Converts offers into a structured pandas DataFrame with an option to include data from all pages.

		Parameters:
			all (bool): A flag to determine if the method should fetch offers from all pages (True) or 
			just the current page (False).

		This method decides based on the 'all' parameter whether to fetch offers from all pages or just the current one.
		It uses either 'loadAllOffers' or 'loadOffers' accordingly. After obtaining the data, it normalizes the list of 
		dictionary objects into a pandas DataFrame. The DataFrame is cleaned by dropping any rows with NA values and 
		attempts to convert the 'price' column to integers. This method is especially useful for preparing the data for 
		downstream analysis tasks.

		Returns:
			pandas.DataFrame: A DataFrame containing structured and potentially cleaned offer data.
		"""
		dict_data = {}
		if all:
			dict_data = self.loadAllOffers()
			# print(type(dict_data))
			# run inspect for debugging purposes, when facing data structure problems during flattening
			# inspect_data_structure(dict_data)
			# inspect_non_dict_elements(dict_data, [120])
			flattened_dict_data = flatten_list_of_dicts(dict_data)
			table = pd.json_normalize(flattened_dict_data)
			table = table.dropna(axis=0)
		else:
			dict_data = self.loadOffers()
			# print(dict_data)
			table = pd.json_normalize(dict_data)
			table = table.dropna(axis=0)
		try:
			table['price'] = table['price'].astype(int)
		except KeyError as e:
			print('Price column not available, hence the price is on request')
		return table

	def getLenFirstEntry(self) -> int:
		"""
		Gets the length of the first entry in the payload. Used to check if a query is set.
		Returns:
		int: Length of the first query string in the payload.
		"""
		return len(self.payload.get('query'))

	def updateQuery(self, query : str) -> None:
		"""
		Updates the search query in the payload.
		Parameters:
		query (str): The new search query to be set.
		"""
		self.payload.update({'query' : query})

	def updatePage(self, page : int) -> None:
		"""
		Updates the payload to request a specific page of search results.
		Parameters:
		page (int): The page number to be set in the payload.
		"""
		self.payload.update({'showPage' : page})

class Menu:
	"""
	Handles user interactions, providing a menu for input and choices.
	"""
	def __init__(self):
		"""
		Initializes the Menu with the user's choice set to None.
		"""
		self.choice = None

	def display_options(self) -> None:
		"""
		Displays the main menu options to the user for choosing the type of search.
		"""
		print("Choose your search type:")
		print("1. Search by Model Name")
		print("2. Search by Reference Number")

	def get_user_choice(self) -> bool:
		"""
		Asks the user whether to retrieve data from all pages or just the first page.
		Returns:
		    bool: True if the user wants all data, False for only the first page.
		"""
		self.choice = input("Enter your choice (1 or 2): ").strip()
		return self.validate_choice()

	def validate_choice(self) -> bool:
		"""
		Prompts the user to decide if they want to save the data to a CSV file.
		Returns:
		    str: Filename for the CSV if the user chooses to save, else an empty string.
		"""
		return self.choice in ['1', '2']

	def get_search_input(self) -> str:
		"""
		Asks the user whether they want to continue with another search.
		Returns:
		bool: True if the user wants to continue, False otherwise.
		"""
		if self.choice == '1':
			return input("Enter the model name (e.g. Daytona or Cartier Santos): ")
		elif self.choice == '2':
			return input("Enter the reference number (e.g. 126610LN): ")
		return ""

	def get_data_retrieval_choice(self) -> bool:
		"""
		Asks the user to choose whether to retrieve all available data or just the data from the first page.

		This method prompts the user with a question and expects a response. The user should respond with 'yes' 
		to retrieve data from all available pages or 'no' to retrieve only from the first page. The method 
		interprets the response and returns a boolean value accordingly.

		Returns:
			bool: True if the user wants to retrieve all data; False if the user only wants data from the first page.
		"""
		data_choice = input("Do you want to retrieve all data? (yes for all data / no for first page only): ").strip().lower()
		return data_choice == 'yes'

	def get_save_csv_choice(self) -> str:
		"""
		Prompts the user to decide if they want to save the fetched data to a CSV file and, if so, asks for a filename.

		If the user chooses to save the data, they are further prompted to enter a filename for the CSV file. 
		If the user provides a filename, it is returned; otherwise, a default filename ('watch_data') is used. 
		If the user chooses not to save the data, an empty string is returned.

		Returns:
		str: The filename for the CSV file, a default name if no name is provided, or an empty string if not saving.
		"""
		save_csv = input("Do you want to save this data in a CSV file? (yes/no): ").strip().lower()
		if save_csv == 'yes':
			filename = input("Enter a filename for the CSV (without extension): ").strip()
			return filename if filename else "watch_data"
		return ""

	def ask_to_continue(self) -> bool:
		"""
		Asks the user if they wish to perform another search or terminate the program.

		This method queries the user to make a decision about continuing with another watch search. 
		The user should respond with 'yes' to continue or 'no' to exit the program. The method then 
		returns a boolean value based on this response.

		Returns:
		bool: True if the user wants to continue with another search; False if the user wants to exit the program.
		"""
		continue_search = input("Do you want to search for another watch? (yes/no): ").strip().lower()
		return continue_search == 'yes'

def show_spinner(stop_event):
	"""
	Displays a spinning loading animation in the console.

	Args:
	stop_event (threading.Event): An event object used to control the termination of the spinner.

	This function runs in a loop, displaying a spinner animation in the console. The loop continues
	until the stop_event is set from another thread. The animation is achieved by cycling through
	a list of characters that simulate a spinning motion when printed sequentially.
	"""
	spinner = ['|', '/', '-', '\\']
	idx = 0
	while not stop_event.is_set():
		sys.stdout.write('\rLoading... ' + spinner[idx % len(spinner)])
		sys.stdout.flush()
		idx += 1
		time.sleep(0.1)
	sys.stdout.write('\n')

def start_spinner(stop_event):
	"""
	Starts a new thread to run the spinner animation.

	Args:
	stop_event (threading.Event): An event object used to control the termination of the spinner.

	This function creates and starts a new thread dedicated to running the spinner animation.
	The thread runs the 'show_spinner' function with the provided stop_event.

	Returns:
		threading.Thread: The thread object running the spinner animation.
	"""
	spinner_thread = threading.Thread(target=show_spinner, args=(stop_event,))
	spinner_thread.start()
	return spinner_thread

def stop_spinner(stop_event, spinner_thread):
	"""
	Stops the spinner animation by setting the stop event and waits for the spinner thread to finish.

	Args:
	stop_event (threading.Event): The event object used to signal the spinner thread to stop.
	spinner_thread (threading.Thread): The thread object running the spinner animation.

	This function sets the stop_event, signaling the spinner thread to terminate its loop.
	It then waits (joins) for the spinner thread to finish executing before continuing.
	"""
	stop_event.set()
	spinner_thread.join()

def inspect_data_structure(data_list, sample_size=5):
	"""
	Inspects the structure of the elements in the provided list.

	Args:
	data_list (list): The list to be inspected.
	sample_size (int): Number of elements to display for inspection.

	Returns:
	None
	"""
	# Check if all elements in the list are dictionaries
	all_dicts = all(isinstance(item, dict) for item in data_list)
	print("All elements are dictionaries:", all_dicts)

	# If not all elements are dictionaries, identify the non-dictionary elements
	if not all_dicts:
		print("Non-dictionary elements found at indices:")
		for index, item in enumerate(data_list):
			if not isinstance(item, dict):
				print(f"  Index {index}: Type {type(item).__name__}")

	# If all elements are dictionaries, print the first few elements
	elif data_list:
		print("Inspecting the first few elements:")
		for item in data_list[:sample_size]:
			print(item)
	else:
		print("The list is empty.")

def inspect_non_dict_elements(data_list, indices):
	"""
	Inspects the non-dictionary elements in the provided list at specified indices.

	Args:
	data_list (list): The list to be inspected.
	indices (list): List of indices of the non-dictionary elements.

	Returns:
	None
	"""
	print("Inspecting non-dictionary elements at specified indices:")
	for index in indices:
		if index < len(data_list):
			print(f"Index {index}:")
			print(data_list[index])
		else:
			print(f"Index {index} is out of range.")

def flatten_list_of_dicts(data_list):
	"""
	Flattens a list of dictionaries and lists containing dictionaries into a single list of dictionaries.

	Args:
	data_list (list): The list to be flattened.

	Returns:
	list: A flattened list of dictionaries.
	"""
	flattened_list = []
	for element in data_list:
		if isinstance(element, dict):
			flattened_list.append(element)
		elif isinstance(element, list) and all(isinstance(item, dict) for item in element):
			flattened_list.extend(element)
	return flattened_list

def main() -> None:
	"""
	The main function serves as the entry point for the program. It orchestrates the overall workflow of the application,
	facilitating user interactions and processing data based on user inputs.

	The function performs the following steps in a loop:
		1. Displays search options to the user and captures their choice.
		2. Based on the user's choice, prompts for further input (model name or reference number).
		3. Updates the search query in the Chrono object with the user's input.
		4. Asks the user whether they want to retrieve data from all pages or just the first page.
		5. Fetches the watch data as per the user's choice and prints it.
		6. Asks the user if they want to save the fetched data to a CSV file. If yes, saves the data.
		7. Finally, asks the user if they wish to continue with another search or exit.

	The loop continues until the user chooses to exit. This design allows the user to perform multiple searches and operations
	in a single run of the program.

	Processes within the main function:
		- Initialize Chrono and Menu objects.
		- Loop over the user interaction flow until the user decides to exit.
		- Handle user choices and inputs, displaying appropriate messages for invalid inputs.
		- Retrieve and display watch data based on user selections.
		- Optionally save data to a CSV file as per user's request.
		- Break the loop and exit the program when the user chooses not to continue.
	"""

	# Start the spinner for initializing for setting up
	stop_event = threading.Event()
	spinner_thread = start_spinner(stop_event)
	
	chrono = Chrono()

	# Stop the spinner after driver is set up
	stop_spinner(stop_event, spinner_thread)

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

			# Start the spinner thread before fetching data
			stop_event = threading.Event()
			spinner_thread = start_spinner(stop_event)

			# Fetch watch data
			watch_data = chrono.tableOffers(all=all_data)[['name', 'price']]

			# Stop the spinner after data is fetched
			stop_spinner(stop_event, spinner_thread)		

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
			print("Programme exited. Thanks for using!")
			break

if __name__ == "__main__":
	main()

