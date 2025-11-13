import pandas as pd
from plotly import *
import plotly.express as px
from collections import Counter
pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)
import sys
#sys.path.insert(0, '/backend/')
from backend.seller_scraper import Scraper
from backend.data_cleaning import Service

# Graph Creator - creates all graphs for app.py
# :param data: dataframe containing cleaned data
# :type data: pandas dataframe
class Chart:
    def __init__(self):
        self.data = pd.read_csv("../Website_Gloger/data/cleaned_data.csv",header=0)
        self.data['Servicelist'] = self.data['Servicelist'].fillna("No Service")

    #creates a pie chart based on cleaned data
    def pieChart(self, inputData = pd.DataFrame()):
        if inputData.empty:
            try:
                lists = [d.split(",") for d in self.data["Servicelist"]]
            except:
                lists = self.data["Servicelist"].tolist()
            data = [x for xs in lists for x in xs]
        else:
            try:
                lists = [d.split(",") for d in inputData["Servicelist"]]
            except:
                lists = inputData["Servicelist"].tolist()
            data = [x for xs in lists for x in xs]

        counts = Counter(data)

        services=[]
        services_nr=[]
        for key in counts:
            if key == "nan":
                services_nr.append(int(counts[key]))
                key = "no Website/Service"
                services.append(key.capitalize())
            else:
                services.append(key.capitalize())
                services_nr.append(int(counts[key]))

        data = {'Services':services,
                'Ratio': services_nr}
        df = pd.DataFrame(data).dropna().sort_values(by='Ratio', ascending= False).head(10)
        s= df['Services'].tolist()
        r=df['Ratio'].tolist()

        fig = px.pie(df, values="Ratio", names="Services",
                     hover_data=['Services'],
                     color_discrete_sequence=px.colors.sequential.Teal_r)

        fig = fig.update_layout(showlegend=False)
        fig = fig.update_traces(textposition='inside', labels = s, values = r,
                                textinfo='label+percent',insidetextorientation='horizontal')#

        fig = fig.update_layout(height=200,uniformtext_minsize=8,uniformtext_mode='show')
        fig = fig.update_layout(margin=dict(l=0, r=0.5, t=0, b=5))
        # fig = fig.update_layout(legend=dict(orientation = "h", yanchor="bottom",y=-1.1,xanchor="left", x=0))

        return fig

    #prepares/adapts cleaned data for dash DataTable
    def table(self):
        data = self.data
        data[['Seller','City']] = data['Seller'].str.split('+',expand=True)
        #data['Service'] = data['Servicelist']
        data['Servicelist'] = data['Servicelist'].str.split(pat = ",")
        service_df = pd.DataFrame(data.Servicelist.values.tolist()).add_prefix('Service_').fillna('')
        service_df['Seller'] = data['Seller']
        data = data.join(service_df, lsuffix='_Names', rsuffix='_other')

        data1 = data[['Seller_Names','City','Website','Service_0', 'Service_1', 'Service_2', 'Service_3', 'Service_4',
                     'Service_5', 'Service_6', 'Service_7', 'Service_8', 'Service_9',
                     'Service_10', 'Service_11']]
        #data2 = data[['Seller_Names','Website','Service']]
        return data1

    #Core: Performs crawling and categorization/cleaning of an input (seller+city)
    # outputs a dataframe with the result data for a dbc table
    def search_table(self,search):
        scraper = Scraper(searchlist=search)
        scraper.run()
        df = scraper.create_dataframe()

        cleaner = Service(data = df)
        cleaner.run()
        data = cleaner.changed_data
        piedata = cleaner.changed_data

        self.add_to_dataframe(cleaner.changed_data)

        piedata['Servicelist'] = piedata['Servicelist'].fillna("No Service")
        data['Servicelist'] = data['Servicelist'].fillna("No Service")

        data[['Seller','City']] = data['Seller'].str.split('+',expand=True)
        #data['Service'] = data['Servicelist']
        data['Servicelist'] = data['Servicelist'].str.split(pat = ",")

        service_df = pd.DataFrame(data.Servicelist.values.tolist()).add_prefix('Service_').fillna('')
        data = data[['Seller','City','Website']]
        service_df['Seller'] = data['Seller']
        data = data.join(service_df, lsuffix='_Names', rsuffix='_other')
        data = data.drop(['Seller_other'],axis = 1)

        return data,piedata

    #Addition to search_table().Adds the new data row of the new seller to the inventory data
    def add_to_dataframe(self,newData):
        sname = newData['Seller'].tolist()[0].split("+")[0]
        if self.data['Seller'].str.contains(sname).any():
            print(str(sname) +" already in Dataframe!")
        else:
            self.data = pd.concat([self.data,newData], ignore_index=True)

            print(self.data['Servicelist'][0])
            print(type(self.data['Servicelist'][0]))

            #self.data.to_csv(r'../Website_Gloger/data/cleaned_data.csv', index = None)
            print(str(sname) +" saved in Dataframe!")

    #Generates a bar chart of services across all dealers
    def bar_chart(self, filter = None):
        data = pd.read_csv("../Website_Gloger/data/cleaned_data.csv",header=0)
        data['Servicelist'] = data['Servicelist'].fillna("No Service")

        data['ServicelistS'] = data['Servicelist'].str.split(pat = ",")
        data['ServicelistS'] = data['ServicelistS'].fillna('No Service')
        data['N_Services'] = data['ServicelistS'].map(len)#.str.len()
        service_df = pd.DataFrame(data.ServicelistS.values.tolist()).add_prefix('Service_').fillna('None')

        service_df['Seller'] = data['Seller']
        joined_data = data.join(service_df, lsuffix='_Names', rsuffix='_o')
        df_s = joined_data[['Seller_Names', 'N_Services']]

        melted = joined_data.melt(id_vars = ['Seller_Names'],
                                 value_vars = ['Service_0', 'Service_1', 'Service_2', 'Service_3',
                                               'Service_4', 'Service_5', 'Service_6', 'Service_7',
                                               'Service_8', 'Service_9', 'Service_10', 'Service_11'])

        selected = melted.join(df_s,lsuffix='', rsuffix='_other')

        sorted = selected.sort_values(by='N_Services',ascending=False)

        df = sorted[sorted.value != 'None']
        fig = px.bar(df,x = 'value', y = 'Seller_Names', color = 'Seller_Names')

        if filter and filter != "Overview":
            df = df[df.Seller_Names.str.contains(str(filter))]
            df['count'] = 1
            fig = px.bar(df,x = 'value', y = 'count', color = 'value',
                         color_discrete_sequence= ["#115f9a", "#1984c5", "#22a7f0", "#48b5c4", "#76c68f", "#a6d75b", "#c9e52f", "#d0ee11", "#d0f400"])
            fig =fig.update_yaxes(visible = False)
            fig =fig.update_xaxes(title='')
            fig = fig.update_layout(showlegend = False,margin=dict(l=0, r=0, t=0, b=0))

        else:
            fig = px.bar(df,x = 'value', y = 'Seller_Names', color = 'Seller_Names',
                         color_discrete_sequence=["#1f77b4", "#aec7e8", "#ff7f0e", "#ffbb78", "#2ca02c", "#98df8a", "#d62728", "#ff9896", "#9467bd", "#c5b0d5", "#8c564b", "#c49c94", "#e377c2", "#f7b6d2", "#7f7f7f", "#c7c7c7", "#bcbd22", "#dbdb8d", "#17becf", "#9edae5"])
            fig =fig.update_yaxes(visible = False)
            fig =fig.update_xaxes(title='')
            fig = fig.update_layout(showlegend = False,margin=dict(l=0, r=0, t=0, b=0))

        #fig.show()
        return fig

    # Get KPIs by Top/Least most number of services and the related seller
    def get_top_bottom(self):
        data = self.data
        data['N_Services'] = data['Servicelist'].map(len)
        sorted = data.sort_values(by='N_Services',ascending=False)

        top_seller = sorted['Seller'].head(1).values[0].split("+")[0]
        top_number = sorted['N_Services'].head(1).values[0]
        bottom_seller = sorted['Seller'].tail(1).values[0].split("+")[0]
        bottom_number = sorted['N_Services'].tail(1).values[0]

        return top_seller,top_number,bottom_seller,bottom_number

#Main - Used for testing of functions
if __name__ == "__main__":
     v = Chart()
     v.bar_chart()
     p = v.pieChart()
     p.show()
     v.table()
     r, piedata = v.search_table(search = ["Hahn Automobile+Esslingen"])


