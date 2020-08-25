# framework 2003 XLBR, global organisation, whole purpose we want to make it easier to transfer data between companies
#If we want to make data more usefull, we need to develop a whole new framexork.
#xlbr_type=v
# coer page end to end information
import csv
import pprintpp as pprint
import pathlib
import collections
import xml.etree.ElementTree as ET

#define our working directory
sec_directory = pathlib.Path.cwd().joinpath("facebook10Q")
# print(sec_directory)

#define file paths to the documents 
file_htm = sec_directory.joinpath('fb-06302020x10q_htm.xml').resolve()
file_cal = sec_directory.joinpath('fb-20200630_cal.xml').resolve()
file_lab = sec_directory.joinpath('fb-20200630_lab.xml').resolve()
file_def = sec_directory.joinpath('fb-20200630_def.xml').resolve()

# define the different storage components
storage_list = []
storage_values = {}
storage_gaap = {}

# create a named tuple
FilingTuple = collections.namedtuple('FilingTuple',['file_path','namespace_element','namespace_label'])

# Initialize my list of named tuples, I plan to parse.

files_list = [
    FilingTuple(file_cal, r'{http://www.xbrl.org/2003/linkbase}calculationLink','calculation'),
    FilingTuple(file_def, r'{http://www.xbrl.org/2003/linkbase}definitionLink','definition'),
    FilingTuple(file_lab, r'{http://www.xbrl.org/2003/linkbase}labelLink','label'),

]

# print(files_list)
#define two categories of labels, those I want and thos I don't want
avoids = ['linkbase','roleRef']
parse = ['label', 'lanelLink',"labelArc", 'loc', 'definitionLink', 'definitionArc', 'calculationArc']

# create two sets to store my keys
lab_list = set()
cal_list = set()

# loop through each file
for file in files_list:
    #parse the file
    tree = ET.parse(file.file_path)

    #grab all the namespace elements in the tree
    elements = tree.findall(file.namespace_element)

    #loop through each element
    for element in elements: 
        
        # if the element has childen w ewant to parse those as well
        for child_element in element.iter():
            # print(child_element)
    ###End of part 2
            #split the label
            element_split_label = child_element.tag.split('}')
            # get the label parts
            namespace = element_split_label[0]
            label = element_split_label[1]

            # is this the label we want
            if label in parse:
                
                #define the item type label
                element_type_label = file.namespace_label + '_' + label

                # intialize smaller dictionnary
                dict_storage = {}
                dict_storage['item_type'] = element_type_label
                
                #grab all the attributes keys
                cal_keys = child_element.keys()
                # print(cal_keys)
                # for each attribute do something
                for key in cal_keys:
                    if '}' in key : 
                        new_key = key.split('}')[1]
                        dict_storage[new_key] = child_element.attrib[key]
                    else:
                        dict_storage[key] = child_element.attrib[key]
                
                if element_type_label == 'label_label':
                    # grabe the label key
                    key_store = dict_storage['label']

                    #create master key
                    master_key = key_store.replace('lab_','')

                    # split the master key
                    label_split = master_key.split('_')

                    #create my gaap id
                    gaap_id = label_split[0] + ":" + label_split[1]

                    # print(gaap_id)

                    # One dictionary contains only the values from the XML Files.
                    storage_values[master_key] = {}
                    storage_values[master_key]['label_id'] = key_store
                    storage_values[master_key]['location_id'] = key_store.replace('lab_','loc_')
                    storage_values[master_key]['us_gaap_id'] = gaap_id
                    storage_values[master_key]['us_gaap_value'] = None
                    storage_values[master_key][element_type_label] = dict_storage

                    # The other dictionary will only contain the values related to GAAP Metrics

                    storage_gaap[gaap_id] = {}
                    storage_gaap[gaap_id]['id'] = gaap_id
                    storage_gaap[gaap_id]['master_id'] = master_key
                # add to dictionary
                storage_list.append([file.namespace_label, dict_storage])

        # pprint.pprint(storage_values)

#PARSE THE HTML 10Q FILE

# load the XML File
tree = ET.parse(file_htm)

# loop throught all the elements
for element in tree.iter():
    if 'nonNumeric' in element.tag:
        #Grab the attribut and the master ID.
        attr_name = element.attrib['name']
        gaap_id = storage_gaap[attr_name]['master_id']

        storage_gaap[attr_name]['context_ref'] = element.attrib['contextRef']
        storage_gaap[attr_name]['context_id'] = element.attrib['id']
        storage_gaap[attr_name]['continued_at'] = element.attrib.get('continuedAt','null')
        storage_gaap[attr_name]['escape'] = element.attrib.get('escape','null')
        storage_gaap[attr_name]['format'] = element.attrib.get('format','null')

        # print(element.attrib)
        # same for nonFraction tags
    if 'nonFraction' in element.tag:

        # print(element.attrib)
        # Grab the attributes name and the master ID.
        attr_name = element.attrib['name']
        gaap_id = storage_gaap[attr_name]['master_id']

        storage_gaap[attr_name]['context_ref'] = element.attrib['contextRef']
        storage_gaap[attr_name]['fraction_id'] = element.attrib['id']
        storage_gaap[attr_name]['unit_ref'] = element.attrib.get('unitRef','null')
        storage_gaap[attr_name]['scale'] = element.attrib.get('scale','null')
        storage_gaap[attr_name]['format'] = element.attrib.get('format','null')
        storage_gaap[attr_name]['value'] = element.text.strip() if element.text else 'null'

        # don't forget to store the actual value if it exist
        if gaap_id in storage_values:
            storage_values[gaap_id]['us_gaap_value'] = storage_gaap[attr_name]

# pprint.pprint(storage_values)
file_name = 'sex_xbrl_scrape_content.csv'
with open(file_name, mode = 'w', newline='') as sec_file:
    #create a writer
    writer = csv.writer(sec_file)

    #write the header
    writer.writerow(['FILE', 'LABEL', 'VALUE'])

    #dump the dict to the csv file
    for dict_cont in storage_list:
        for item in dict_cont[1].items():
            writer.writerow([dict_cont[0]] + list(item))


file_name = 'sex_xbrl_scrape_values.csv'
with open(file_name, mode = 'w', newline='') as sec_file:
    #create a writer
    writer = csv.writer(sec_file)

    #write the header
    writer.writerow(['ID', 'CATEGORY', 'LABEL', 'VALUE'])

    #start at level
    for storage_1 in storage_values:
        #level 2
        for storage_2 in storage_values[storage_1].items():
            # if the value is a dictionnary then we have one more possible level
            if isinstance(storage_2[1], dict):
                for storage_3 in storage_2[1].items():

                    # write it to the csv
                    writer.writerow([storage_1] + [storage_2[0]] + list(storage_3))
                else:
                    if storage_2[1] != None:
                    #write it to the csv
                        writer.writerow([storage_1] + list(storage_2) + ['None'])