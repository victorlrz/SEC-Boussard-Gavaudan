import requests
from bs4 import BeautifulSoup
#pip install lxml

# define our endpoint 
endpoint = r"https://www.sec.gov/cgi-bin/browse-edgar"

#define our parameters
# param_dict = {'action':'getcompany',
#             'CIK':'789019',
#             'type':'10-k',
#             'dateb':'20190101',
#             'owner':'exclude',
#             'start':'',
#             'output':'atom',
#             'count':'100'}

param_dict = {'action':'getcompany',
            'CIK':'789019',
            'type':'10-k',
            'dateb':'20190101',
            'owner':'exclude',
            'start':'',
            'output':'atom',
            'count':'10'}

# param_dict_bis = {
#     'action':'getcompany',
#     'owner':'exclude',
#     'output':'atom',
#     'company':'Microsoft',
# } 
# Change ouput to be more clear

#define our response
response = requests.get(url= endpoint, params = param_dict)

#print status code
# print(response.status_code)
# print(response.url)

soup = BeautifulSoup(response.content, 'lxml')

def parse_entries(soup):
    #find all the entry tags
    entries = soup.find_all('entry')

    # initialize our list for storage 
    master_list_xml = []

    #We need to loop through entru
    for entry in entries:
        # grab the accession number so we can create a key value
        accession_num = entry.find('accession-number').text
        # print(accession_num)

        #create a new dictionnary
        entry_dict = {}
        entry_dict[accession_num] = {}

        # store the category info
        category_info = entry.find('category')
        entry_dict[accession_num]['category'] = {}
        entry_dict[accession_num]['category']['label'] = category_info['label']
        entry_dict[accession_num]['category']['scheme'] = category_info['scheme']
        entry_dict[accession_num]['category']['term'] = category_info['term']
        # print(entry_dict)
        # store the file info
        entry_dict[accession_num]['file_info'] = {}
        try : 
            entry_dict[accession_num]['file_info']['act'] = entry.find('act').text
        except :
            entry_dict[accession_num]['file_info']['act'] = ' '

        entry_dict[accession_num]['file_info']['file_number'] = entry.find('file-number').text
        entry_dict[accession_num]['file_info']['file_number_href'] = entry.find('file-number-href').text
        entry_dict[accession_num]['file_info']['filing_date'] = entry.find('filing-date').text
        entry_dict[accession_num]['file_info']['filing_href'] = entry.find('filing-href').text
        entry_dict[accession_num]['file_info']['filing_type'] = entry.find('filing-type').text
        entry_dict[accession_num]['file_info']['form_number'] = entry.find('film-number').text
        entry_dict[accession_num]['file_info']['form_name'] = entry.find('form-name').text
        entry_dict[accession_num]['file_info']['file_size'] = entry.find('size').text

        try : 
            entry_dict[accession_num]['file_info']['xbrl_href'] = entry.find('xbrl_href').text
        except :
            entry_dict[accession_num]['file_info']['xbrl_href'] = ' '
        
        #store extra info
        entry_dict[accession_num]['request_info'] = {}
        entry_dict[accession_num]['request_info']['link'] = entry.find('link')['href']
        entry_dict[accession_num]['request_info']['title'] = entry.find('title').text
        entry_dict[accession_num]['request_info']['last_updated'] = entry.find('updated').text

        #store in the master list
        master_list_xml.append(entry_dict)
    
    return master_list_xml


# print(master_list_xml)
# print(master_list_xml[0]['0001564590-18-019062']['file_info'])

big_list = []

#parse the soup
big_list.append(parse_entries(soup))
# find the links that will take us to the next page
links = soup.find_all('link',{'rel':'next'})

# while there is still a next page
while soup.find_all('link',{'rel':'next'}) != []:
    #grab the next link
    next_page_link = links[0]['href']
    print('-'*100)
    print(next_page_link)

    # request the next page
    response = requests.get(url = next_page_link)
    soup = BeautifulSoup(response.content,'lxml')
    #parse the soup
    big_list.append(parse_entries(soup))

    # find the links that will take us to the next page
    links = soup.find_all('link',{'rel':'next'})

