import requests
from bs4 import BeautifulSoup
import re
import pandas as pd
from selenium import webdriver
import numpy as np
from time import sleep
import json
import datetime
import os

ACCOUNT = 1
if ACCOUNT == 1: # James Hart
	EMAIL_ADDRESS = "*****@gmail.com"
	PASSWORD = "*****"
elif ACCOUNT == 2: # Mark Tatum
	EMAIL_ADDRESS = "*****@gmail.com"
	PASSWORD = "*****"
elif ACCOUNT == 3: # Jonathon Reed
	EMAIL_ADDRESS = "*****@gmail.com"
	PASSWORD = "*****"
	
# Base search URL
base_search_url = "https://www.linkedin.com/search/results/people/?origin=FACETED_SEARCH"

# Function to sleep for a random amount of time to make requests seem like they are not from a bot
def ran_sleep(multiple,base=0):
    return sleep(base+(np.random.rand()*2)*multiple)

# Function to create a chrome browser using selenium
def initialize_browser(driver='/Users/JasonKatz/Applications/chromedriver'):
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--disable-extensions')
    chrome_options.add_argument('--profile-directory=Default')
    chrome_options.add_argument("--disable-plugins-discovery")
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--user-agent=Googlebot")
    return webdriver.Chrome(driver, chrome_options=chrome_options)

# Function to scrape profile URLs from a linkedin search
def scrape_pages(driver, num_pages, linkedin_search_url, first_page_urls):
	# List of all URLs
	all_urls = first_page_urls
	
	# Iterate through each page
	for page_number in range(2,num_pages+1):
		
		# Sometimes sleep for an extended period of time to simulate a human
		ran_num = np.random.rand()
		if ran_num < 0.001:
			print("Sleeping for 30 minutes")
			ran_sleep(1800,10)
		elif ran_num < 0.01:
			print("Sleeping for 10 minutes")
			ran_sleep(600,10)
		elif ran_num < 0.05:
			print("Sleeping for 3 minutes")
			ran_sleep(180, 5)
		elif ran_num > 0.999:
			print("Sleeping for 30 minutes")
			ran_sleep(1800, 10)
		elif ran_num > 0.99:
			print("Sleeping for 10 minutes")
			ran_sleep(600, 10)
		elif ran_num > 0.95:
			print("Sleeping for 3 minutes")
			ran_sleep(180, 5)
			
		# Go to next page
		driver.get(linkedin_search_url + "&page=" + str(page_number))
		
		# Sleep for around 30 seconds
		ran_sleep(10,20)
		
		# Sometime scroll through the page to simulate a human
		if ran_num < .33:
			driver.execute_script("window.scrollTo(0, document.body.scrollHeight/{});".format((.1+ran_num)*10))
			
		# Get page raw HTML
		page_source = driver.page_source
		
		# Parse URLs from the page
		current_urls = scrape_urls(page_source)
		
		# Add URLs to the list
		all_urls.extend(current_urls)
		
		# Print message that page has been scraped
		print("Finished page {} of {}".format(page_number, num_pages))
	return all_urls

# Function to scrape URLs from raw HTML
def scrape_urls(page_source):
	
	# Raise error if the page says that the search limit has been reached
	if "Search limit reached." in page_source:
		search_limit_reached = True
		raise Exception('Search Limit Reached')
		
	# Find all public identifiers (profile URLS)
	publicIdentifiers = re.findall("\"publicIdentifier\":\".*?\"", page_source)
	
	# Add all the identifiers that appear more than once (format of a search result profile from raw HTML)
	publicIdentifiers = list(set([i for i in publicIdentifiers if publicIdentifiers.count(i) > 1]))
	
	# Add the portion of the public identifier that is the profile URL
	urls = ["https://www.linkedin.com/in/" + publicIdentifier[20:-1] for publicIdentifier in publicIdentifiers if publicIdentifier[20:-1] != "UNKNOWN"]
	return urls

# Function to save profile counts
def save_profile_counts(total_profiles_scraped, total_profiles_encountered):
	
	# Save number of profiles scraped
	with open("partial_results/total_profiles_scraped.json", 'w') as outfile:
		json.dump(total_profiles_scraped, outfile)
		
	# Save number of profiles encountered
	with open("partial_results/total_profiles_encountered.json", 'w') as outfile:
		json.dump(total_profiles_encountered, outfile)

# Function to scrape all the pages from a linkedin search, keeping track of all global variables and results
def scrape_all_pages(total_profiles_encountered, num_results, page_source, num_pages, driver, linkedin_search_url, total_profiles_scraped, total_profiles_scraped_history, all_profile_urls, country_code, sub_region_code, geo_idx, current_time, industry_code="NA", industry_idx="NA", name="NA", name_idx="NA"):
	
	# Scrape URLs from first page of search results
	scraped_urls = scrape_urls(page_source)
	print("Finished page 1 of {}".format(num_pages))
	
	# If more than one page of results, go through all pages one by one
	if num_pages > 1:
		scraped_urls = scrape_pages(driver, num_pages, linkedin_search_url, scraped_urls)
	
	# Add scraped URLs to all results
	all_profile_urls.append({"Country_Code": country_code, "Sub_Region_Code": sub_region_code, "geo_index": geo_idx, "Industry_Code": industry_code, "industry_index": industry_idx, "Name": name, "name_indxex": name_idx, "Profile_urls": scraped_urls})
	
	# Get previous time (for removal of last partial results)
	previous_time = current_time
	
	# Get current time (for saving partial results)
	current_time = int(datetime.datetime.now().timestamp())
	
	# Save partial results (and remove previous partial results)
	with open("partial_results/partial_results-{}.json".format(current_time), 'w') as outfile:
		json.dump(all_profile_urls, outfile)
	try:
		os.remove("partial_results/partial_results-{}.json".format(previous_time))
	except:
		pass
	
	# Add to number of profiles scraped and encountered
	total_profiles_scraped += len(scraped_urls)
	total_profiles_encountered += num_results
	
	# Add to histroy of scraped profiles
	total_profiles_scraped_history.append(total_profiles_scraped)
	
	# Print update
	print("Profiles Encountered: {}, Profiles Scraped: {}".format(total_profiles_encountered, total_profiles_scraped))
	
	# Return global variables
	return total_profiles_encountered, total_profiles_scraped, total_profiles_scraped_history, all_profile_urls, current_time

# Function to get page source from a URL
def get_page_source(driver, linkedin_search_url):
	
	# Go to search page
	driver.get(linkedin_search_url)
			
	# Wait around 30 seconds
	ran_sleep(10,20)
			
	# Get page raw HTML
	return driver.page_source
	

# Load the filter data from file to make custom searches
with open('filter_data.json') as json_file:  
    filter_data = json.load(json_file)

# Geography Codes
linkedin_geo_codes = filter_data['linkedin_geo_codes']

# Industry Codes
linkedin_industry_codes = filter_data['linkedin_industry_codes']

# 200 most popular names
most_popular_names = filter_data['most_popular_names']

# Initialize the selenium browser
driver = initialize_browser()

# Go to the login page
driver.get("https://www.linkedin.com/login/")

# Wait around 30 seconds
ran_sleep(10,20)

# Enter the email address
driver.find_element_by_id("username").send_keys(EMAIL_ADDRESS)

# Enter the password
driver.find_element_by_id("password").send_keys(PASSWORD)

# Click the login button
driver.find_element_by_class_name("login__form_action_container ").click()

# Get the most recent time from partial results
last_partial_result = max([int(partial_result.split("-")[1].split(".")[0]) for partial_result in os.listdir("partial_results/") if partial_result[0] == "p"])

# Load the current results data
with open("partial_results/partial_results-{}.json".format(last_partial_result)) as json_file:  
    partial_result = json.load(json_file)

# Load previous metadata about where scraping left off
with open("partial_results/most_recent_geo_idx.json") as json_file:  
    max_geo_idx_partial = json.load(json_file)
with open("partial_results/most_recent_industry_idx.json") as json_file:  
    current_industry_idx = json.load(json_file)
with open("partial_results/most_recent_name_idx.json") as json_file:  
    current_name_idx = json.load(json_file)
with open("partial_results/total_profiles_scraped.json") as json_file:  
    total_profiles_scraped = json.load(json_file) 
with open("partial_results/total_profiles_encountered.json") as json_file:  
    total_profiles_encountered = json.load(json_file) 

# School filter for search
school_code = "19339" # Villanova University
school_filter = "&facetSchool=%5B\"" + school_code + "\"%5D"

# All profiles
all_profile_urls = partial_result

# Current time (for saving partial results)
current_time = int(datetime.datetime.now().timestamp())

# Total number of code to iterate through
num_geo_codes = len(linkedin_geo_codes)
num_industry_codes = len(linkedin_industry_codes)
num_names = len(most_popular_names)

# Initialize index
geo_idx = 0

# For tracking if scraper is not working
total_profiles_scraped_history = [total_profiles_scraped]

# Flag for search limit
search_limit_reached = False

# Continue until a certain endpoint is reached (scraper is stuck, search limit reached, end of scraping)
while True:
	
	# Break if the search limit has been reached
	if search_limit_reached:
		break
	elif "Search limit reached." in driver.page_source:
		search_limit_reached = True
		break
		
	# Break if all geo codes have been scraped
	elif geo_idx+1 == num_geo_codes:
		break
		
	# Break if no profiles are being scraped (something unknown is wrong)
	elif len(total_profiles_scraped_history) > 7:
		if total_profiles_scraped == total_profiles_scraped_history[-1] == total_profiles_scraped_history[-2] == total_profiles_scraped_history[-3] == total_profiles_scraped_history[-4] == total_profiles_scraped_history[-5]:
			print("\n\nWe appear to be stuck, exiting!\n\n")
			break
			
	# Catch error if something goes wrong
	try:
		
		# Iterate through all geography codes
		for geo_idx, geo_code in enumerate(linkedin_geo_codes):
			
			# Skip the codes that have already been scraped
			if geo_idx < max_geo_idx_partial:
				continue
			
			# Save last geography code completed
			with open("partial_results/most_recent_geo_idx.json", 'w') as outfile:
				json.dump(geo_idx, outfile)
				
			# Save profile counts
			save_profile_counts(total_profiles_scraped, total_profiles_encountered)
			
			# Get country and sub region codes
			country_code = geo_code[0]
			sub_region_code = geo_code[1]
			
			# Create location filter for search
			location_filter = "&facetGeoRegion=%5B\"" + country_code + "%3A" + sub_region_code + "\"%5D"
			
			# Empty industry and name filters
			industry_filter = ""
			name_filter = ""

			# Create custom search
			linkedin_search_url = base_search_url + school_filter + location_filter + industry_filter + name_filter
			
			# Get page raw HTML
			page_source = get_page_source(driver, linkedin_search_url)
			
			# Print current geography code
			print("Starting Scraping of Geography Code: {} out of {}".format(geo_idx+1, num_geo_codes))
			
			# If no results found in current geography code, continue to next one
			if "No results found." in page_source:
				print("No Results in Current Location")
				
			# If results, start scraping
			else:
				
				# Parse how many results there are for the current search
				num_results = re.findall("Showing (.*) result", page_source)
				
				# Try loading page again
				if not num_results:
					
					# Get page raw HTML
					page_source = get_page_source(driver, linkedin_search_url)
					
					# Parse how many results there are for the current search
					num_results = re.findall("Showing (.*) result", page_source)
					
					# Print that something is wrong
					print("Something wrong, trying again, URL: {}".format(driver.current_url))
					
				# If still no search results, move on
				if not num_results:
					
					# Add to count history
					total_profiles_scraped_history.append(total_profiles_scraped)
					
					# Raise error if the page says that the search limit has been reached
					if "Search limit reached." in page_source:
						search_limit_reached = True
						raise Exception('Search Limit Reached')
						
				# If there are results, scrape them
				else:
					
					# Parse total number of results
					num_results = int(num_results[0].replace(",", ""))
					
					# Get number of pages for results
					num_pages = int(np.ceil(num_results/10))
					
					# If there are less than 100 pages, iterate through all of them
					if num_pages <= 100:
						total_profiles_encountered, total_profiles_scraped, total_profiles_scraped_history, all_profile_urls, current_time = scrape_all_pages(total_profiles_encountered, num_results, page_source, num_pages, driver, linkedin_search_url, total_profiles_scraped, total_profiles_scraped_history, all_profile_urls, country_code, sub_region_code, geo_idx, current_time)
						
					# If there are more than 100 pages, apply the industry filters
					else:
						
						# Iterate through all industry codes
						for industry_idx, industry_code in enumerate(linkedin_industry_codes):
							
							# Skip the codes that have already been scraped
							if industry_idx < current_industry_idx:
								continue
								
							# Update the current industry index
							current_industry_idx = industry_idx
							
							# Save last industry code completed
							with open("partial_results/most_recent_industry_idx.json", 'w') as outfile:
								json.dump(industry_idx, outfile)
								
							# Save profile counts
							save_profile_counts(total_profiles_scraped, total_profiles_encountered)
								
							# Create industry filter for search
							industry_filter = "&facetIndustry=%5B\"" + industry_code + "\"%5D"
							
							# Empty name filter
							name_filter = ""

							# Create custom search
							linkedin_search_url = base_search_url + school_filter + location_filter + industry_filter + name_filter
							
							# Get page raw HTML
							page_source = get_page_source(driver, linkedin_search_url)
			
							# Print current industry code
							print("Starting Scraping of Industry Code: {} out of {}".format(industry_idx+1, num_industry_codes))
					
							# If no results found in current industry code, continue to next one
							if "No results found." in page_source:
								print("No Results in Current Industry")
								
							# If results, start scraping
							else:
								
								# Parse how many results there are for the current search
								num_results = re.findall("Showing (.*) result", page_source)
								
								# Try loading page again
								if not num_results:
									
									# Get page raw HTML
									page_source = get_page_source(driver, linkedin_search_url)
									
									# Parse how many results there are for the current search
									num_results = re.findall("Showing (.*) result", page_source)
									
									# Print that something is wrong
									print("Something wrong, trying again, URL: {}".format(driver.current_url))
									
								# If still no search results, move on
								if not num_results:
									
									# Add to count history
									total_profiles_scraped_history.append(total_profiles_scraped)
									
									# Raise error if the page says that the search limit has been reached
									if "Search limit reached." in page_source:
										search_limit_reached = True
										raise Exception('Search Limit Reached')
										
								# If there are results, scrape them
								else:
									
									# Parse total number of results
									num_results = int(num_results[0].replace(",", ""))
									
									# Get number of pages for results
									num_pages = int(np.ceil(num_results/10))
									
									# If there are less than 100 pages, iterate through all of them
									if num_pages <= 100:
										total_profiles_encountered, total_profiles_scraped, total_profiles_scraped_history, all_profile_urls, current_time = scrape_all_pages(total_profiles_encountered, num_results, page_source, num_pages, driver, linkedin_search_url, total_profiles_scraped, total_profiles_scraped_history, all_profile_urls, country_code, sub_region_code, geo_idx, current_time, industry_code=industry_code, industry_idx=industry_idx)
										
									# If there are more than 100 pages, apply the name filters
									else:
										
										# Iterate through all names
										for name_idx, name in enumerate(most_popular_names):
											
											# Skip the names that have already been scraped
											if name_idx < current_name_idx:
												continue
												
											# Update the current name index
											current_name_idx = name_idx
											
											# Save last name completed
											with open("partial_results/most_recent_name_idx.json", 'w') as outfile:
												json.dump(name_idx, outfile)
												
											# Save profile counts
											save_profile_counts(total_profiles_scraped, total_profiles_encountered)
												
											# Create name filter for search
											name_filter = "&keywords=" + name
											
											# Create custom search
											linkedin_search_url = base_search_url + school_filter + location_filter + industry_filter + name_filter
											
											# Get page raw HTML
											page_source = get_page_source(driver, linkedin_search_url)
											
											# Print current name
											print("Starting Scraping of Name: {} out of {}".format(name_idx+1, num_names))
											
											# If no results found in current name, continue to next one
											if "No results found." in page_source:
												print("No Results for Current Name")
												
											# If results, start scraping
											else:
												
												# Parse how many results there are for the current search
												num_results = re.findall("Showing (.*) result", page_source)
												
												# Try loading page again
												if not num_results:
													
													# Get page raw HTML
													page_source = get_page_source(driver, linkedin_search_url)
													
													# Parse how many results there are for the current search
													num_results = re.findall("Showing (.*) result", page_source)
													
													# Print that something is wrong
													print("Something wrong, trying again, URL: {}".format(driver.current_url))
													
												# If still no search results, move on
												if not num_results:
													
													# Add to count history
													total_profiles_scraped_history.append(total_profiles_scraped)
													
													# Raise error if the page says that the search limit has been reached
													if "Search limit reached." in page_source:
														search_limit_reached = True
														raise Exception('Search Limit Reached')
														
												# If there are results, scrape them
												else:
													
													# Parse total number of results
													num_results = int(num_results[0].replace(",", ""))
													
													# Get number of pages for results
													num_pages = int(np.ceil(num_results/10))
													
													# If there are less than 100 pages, iterate through all of them
													if num_pages <= 100:
														total_profiles_encountered, total_profiles_scraped, total_profiles_scraped_history, all_profile_urls, current_time = scrape_all_pages(total_profiles_encountered, num_results, page_source, num_pages, driver, linkedin_search_url, total_profiles_scraped, total_profiles_scraped_history, all_profile_urls, country_code, sub_region_code, geo_idx, current_time, industry_code=industry_code, industry_idx=industry_idx, name=name, name_idx=name_idx)
														
													# If there are still more than 100 pages, raise an error
													else:
														raise Exception('Need more filters')
														
							# Reset name index
							current_name_idx = 0
			
			# Reset industry index
			current_industry_idx = 0
			
	# Catch Error
	except:
		
		# Restart selenium browser and login to LinkedIn
		print("\n\nERROR - Restarting\n\n")
		driver = initialize_browser()
		driver.get("https://www.linkedin.com/login/")
		print("Sleeping for 2 minutes\n")
		ran_sleep(120,10)
		driver.find_element_by_id("username").send_keys(EMAIL_ADDRESS)
		driver.find_element_by_id("password").send_keys(PASSWORD)
		driver.find_element_by_class_name("login__form_action_container ").click()

		# Get the most recent time from partial results
		last_partial_result = max([int(partial_result.split("-")[1].split(".")[0]) for partial_result in os.listdir("partial_results/") if partial_result[0] == "p"])
		
		# Load the current results data
		with open("partial_results/partial_results-{}.json".format(last_partial_result)) as json_file:  
			partial_result = json.load(json_file)
			
		# Load previous metadata about where scraping left off
		with open("partial_results/most_recent_geo_idx.json") as json_file:  
			max_geo_idx_partial = json.load(json_file)
