import pandas as pd
from tabulate import *
import spacy
import re
pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)

# Cleanup and Service assignment - cleans and categorize crawled data
# Saves information in a csv. No specific Return Value.
# :param data: dataframe, if empty takes all raw crawler data csv else takes input dataframe with specific crawler data
# :type data: pandas dataframe
class Service:
    # init with raw crawled data of all sellers if param 'data' is empty else with raw crawled data of one seller
    def __init__(self, data = pd.DataFrame()):
        if not data.empty:
            self.changed_data = data
            self.services = pd.read_csv(r'../Website_Gloger/data/Services.csv', encoding='utf-8',header = 0)
        else:
            self.changed_data = pd.read_csv(r'../data/scraped_data.csv',header=0)
            self.services = pd.read_csv(r'../data/Services.csv', encoding='utf-8',header = 0)

    #cleanup of columns Services and Service-subdirectory, uses regex to get raw text of crwaled html body
    def pre_clean_data(self, columns = ["Services","Service_subdirectory"]):
        for col in columns:
            for idx,row in enumerate(self.changed_data[col]):
                if ("No Website" in row or "No Service" in row):
                    self.changed_data.at[idx,col] = "No Website/Services"
                elif("Failed" in row):
                    self.changed_data.at[idx,col] = "Failed"
                elif isinstance(row, str):
                    rows = row.split(",")

                    rows = [re.sub(r'<.*?>', '', r) for r in rows]
                    rows = [re.sub(r'\n', '', r) for r in rows]
                    rows = [re.sub(r'\t', '', r) for r in rows]
                    rows = [r.strip() for r in rows]
                    #rows = [re.sub(r"-","",r) for r in rows if r == "-"]
                    rows = [r.replace('-','') for r in rows]
                    rows = list(filter(None, rows))
                    rows = [r.capitalize() if r.isupper() else r for r in rows]
                    #rows = [re.sub(r'{.*?}', '', r) for r in rows] #re.compile('<.*?>')

                    self.changed_data.at[idx,col]=rows

                else:
                    self.changed_data.at[idx,col] = []


                #print(self.data.at[idx,col])

    #nlp pos tagging of columns Services and Service-subdirectory - only selection of Nouns and Pronouns
    def clean_by_tag(self,columns = ["Services","Service_subdirectory"]):
        nlp = spacy.load("de_core_news_sm")
        for col in columns:
            for idx,row in enumerate(self.changed_data[col]):
                cleaned_string =[]
                if ("No Website" in row or "No Services" in row):
                    cleaned_string = "No Website/Services"
                elif("Failed" in row):
                    cleaned_string = "Failed"
                else:
                    try:
                        for string in row:
                            doc = nlp(string)
                            for token in doc:
                                if (token.pos_  in ('NOUN', 'X', 'PROPN')):
                                    cleaned_string.append(str(token))
                                    #print(token.text, token.pos_, token.dep_)
                    except:
                        cleaned_string = "Failed"

                self.changed_data.at[idx,col]=cleaned_string
                #print(cleaned_string)

    #second cleanup of columns Services and Service-subdirectory - text adjustment
    def specific_clean(self,columns = ["Services","Service_subdirectory"]):
        for col in columns:
            for idx,row in enumerate(self.changed_data[col]):
                if ("No Website" in row or "No Services" in row or "Failed" in row):
                    continue
                elif row:
                    rows = [r.lower() for r in row]
                    self.changed_data.at[idx,col]=rows
                    #print(rows)

    #Categorization of cleaned data by services based on given Services.csv (self.services)
    def filter_services(self):
        service_list = list(map(str.lower, self.services['Service'].tolist()))
        service_group_list = list(map(str.lower, self.services['Group'].tolist()))
        service_cat_list = list(map(str.lower, self.services['Category'].tolist()))

        check_service = lambda x: ",".join(list(set(x).intersection(service_list))) if (x != None and x != "No Website/Services" and x!= "Failed") else "No Website/Services"
        check_service_cat =  lambda x: ",".join(list(set(x).intersection(service_cat_list))) if (x != None and x != "No Website/Services" and x!= "Failed") else "No Website/Services"
        check_service_group = lambda x: ",".join(list(set(x).intersection(service_group_list))) if (x != None and x != "No Website/Services" and x!= "Failed") else "No Website/Services"
        check_service_all = lambda x: ",".join(list(set(list(set(x).intersection(service_list))+list(set(x).intersection(service_cat_list))+list(set(x).intersection(service_group_list)))))if (x != None and x != "No Website/Services" and x!= "Failed") else "No Website/Services"

        #self.data["Services_list"] = self.data["Services"].apply(check_service)
        #self.data["Services_category"] = self.data["Services"].apply(check_service_cat)
        #self.data["Services_group"] = self.data["Services"].apply(check_service_group)

        self.changed_data['Servicelist'] = self.changed_data["Services"]+self.changed_data["Service_subdirectory"]
        self.changed_data['Servicelist'] = self.changed_data['Servicelist'].apply(check_service_all).fillna("No Service")

    #save cleaned and categorized data
    def save_data(self):
        print(self.changed_data.columns)
        self.changed_data.to_csv(r'../data/cleaned_data.csv', index = None, header=['Seller', 'Services', 'Website', 'Website_List', 'Service_directory', 'Service_subdirectory', 'Servicelist'])
        print(self.changed_data.head(3))

    #Run of Service class for clean-up and categoization
    #Step 1: Clean specified columns containing html text. output: pure text
    #Step 2: Use nlp for pos tagging: Selection of all noun and pronouns
    #Step 3: Second clean of text: adapt for service comparison/alignment
    #Step 4: Filter and categorization of pure text with provided service list -
        #service list has been predefined and categorized based on services of FairGarage#
    #Step 5: Save categorized data as csv
    def run(self):
        self.pre_clean_data()
        self.clean_by_tag()
        self.specific_clean()
        self.filter_services()

#Main - Init a Service object with given services 'Services.csv'
# Cleans text, categorize text and saves all information (run)
if __name__ == "__main__":
    service = Service()
    service.run()
    print(service.changed_data)
    try:
        service.save_data()
    except:
        print("Data save did not work!")





