from flask import Flask, jsonify, render_template
from flask_cors import CORS
import pandas as pd
import json
import plotly
import plotly.express as px
from collections import Counter
import plotly.graph_objects as go
from plotly import io

####Deprecated Flask Website - New Version: app.py#######

def get_data():
	data =pd.read_csv(r'C:\Users\Luisa\Documents\DataScience_M.Sc._HDM\Web- and Socialmedia Analytics\result.csv', header=0,index_col=None, squeeze=True)
	#json = data.to_json(orient = 'columns')
	return data

def calc_pieChart_data():
	data = get_data()["Services_all"].tolist()
	seller_nr = len(data)
	data = [str(d).split(",") for d in data]
	data = [x for xs in data for x in xs]
	counts = Counter(data)

	services=[]
	services_nr=[]
	for key in counts:
		services.append(key.capitalize())
		services_nr.append(int(counts[key])/seller_nr)
	return services,services_nr


app = Flask(__name__)
CORS(app)

@app.route("/getData1")
def helloWorld():
	data = {"A": 12, "B": 34}
	data = jsonify(data)	
	return data

@app.route("/pieChart")
def getPieChart():
	df = get_data()[['Seller','Service_subdirectory','Services_all']].to_dict('records')
	data = jsonify(df)
	return data

@app.route("/")
def table():
	data = get_data()[['Seller','Service_subdirectory','Services_all']]
	columns = ("Händler", "Leistungsverzeichnis", "Leistungen")
	data = tuple(data.to_records(index=False))

	return render_template("index.html", heading = columns, data = data)


@app.route("/piechart")
def piechart():
	s, n = calc_pieChart_data()
	data = {'Services':s,
			'Ratio': n}
	df = pd.DataFrame(data)
	pieChart = px.pie(df, values='Ratio', names='Services', title='Angebotene Serviceleistungen')
	#pieChart = pieChart.update_xaxes(rangeslider_visible=True)
	#pieChart.update_layout(autosize = True)#width=100, height=100)

	#fig = go.Figure(go.Pie(labels=df["Services"], values=df["Ratio"]))
	# fig = go.Pie(labels = df["Services"], values=df["Ratio"])
	#piechartJSON = io.to_html.plot(fig, show_link=False, output_type="div", include_plotlyjs=False)
	#return piechartJSON
	#piechartJSON = json.dumps(pieChart, cls=plotly.utils.PlotlyJSONEncoder)
	#return render_template('index.html', graphJSON=piechartJSON)



if __name__ == '__main__':
	app.run(debug=True)#,host='0.0.0.0',port=5000)

