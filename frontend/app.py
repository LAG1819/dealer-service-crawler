from dash import Dash, html, dcc, Input, Output,dash_table, State
import dash
import plotly.express as px
import pandas as pd
import dash_bootstrap_components as dbc
from visualizations import Chart

#Final Website based on Dash - Multipage Website with 3 pages - homepage, page1, page2
# each page has its own layout
# page1: shows piechart, kpis and  DataTabel containing all Seller and and their services
# page2: shows kpis and does a search (crawl and clean-up/categorization) of a user input
# page3: bar chart containg all services per seller

app = Dash(external_stylesheets=[dbc.themes.LUX])
server = app.server
app.config.suppress_callback_exceptions = True

chart = Chart()
table_data = chart.table()
pieGraph = chart.pieChart()
ts,tn,bs,bn = chart.get_top_bottom()

# the style arguments for the sidebar. We use position:fixed and a fixed width
SIDEBAR_STYLE = {
    "position": "fixed",
    "top": 0,
    "left": 0,
    "bottom": 0,
    "width": "16rem",
    "padding": "2rem 1rem",
    "background-color": "#dedfe0",
}

# the styles for the main content position it to the right of the sidebar and
# add some padding.
CONTENT_STYLE = {
    "margin-left": "18rem",
    "margin-right": "2rem",
    "padding": "2rem 1rem",
}

sidebar = html.Div(
    [
        html.H4("Services", className="display-6"),
        html.H5("of car sellers in Germany"),
        html.Hr(),
        html.P(
            "Luisa Gloger", className="lead"
        ),
        dbc.Nav(
            [
                dbc.NavLink("Overview", href="/", active="exact"),
                dbc.NavLink("Search", href="/page-1", active="exact"),
                dbc.NavLink("Services", href="/page-2", active="exact"),
            ],
            vertical=True,
            pills=True,
        ),
        html.P("Hochschule der Medien -",style = {'bottom':'40px', 'position':'fixed', 'font-size':'10pt'}),
        html.P("Web- and Socialmedia Analytics",style = {'bottom':'20px', 'position':'fixed', 'font-size':'10pt'}),
        html.P("©2022 Promotor XD GmbH",style = {'bottom':'0px', 'position':'fixed', 'font-size':'10pt'}),
    ],
    style=SIDEBAR_STYLE,
)

content = html.Div(id="page-content", style=CONTENT_STYLE)

homepage = html.Div([
    dbc.Row(
        [
            dbc.Col(html.Div([
                html.P("Top 10 Services"),
                dcc.Graph(
                    id='pie',
                    figure=pieGraph,
                    style={"margin-top":"-10pt"}
                )
            ],style ={'align':'center','borderRight': "1px solid lightgrey","width": "100%"})),
            dbc.Col([
                html.P("Most/Least Services"),
                dbc.Row([dbc.Col(tn, style={"font-size":"55pt", "text-align":"center"}),dbc.Col(bn,style={"font-size":"55pt", "text-align":"center"})],style ={'text-align':'left'}),
                dbc.Row([dbc.Col(ts,style={"font-size":"9pt"}),dbc.Col(bs,style={"font-size":"9pt"})],style ={'text-align':'center'}),
            ],style ={'borderRight': "1px solid lightgrey","width": "100%"}),
            dbc.Col([
                html.P( "Total of Car Seller"),
                html.P(str(chart.data.shape[0]), style = {'margin-top':'3%',"font-size":"80px",'text-align':'center'})
            ]),
        ],style={'text-align':'center'}
    ),
    dbc.Row(html.Hr(style ={'borderWidth': "0.3vh", "width": "100%"})),
    dbc.Row([
        html.P("Car Seller"),
        dash_table.DataTable(
            data = table_data.to_dict('records'),
            columns = [{"name": i, "id": i} for i in table_data.columns],
            page_size=10,
            style_table={
                'width': '100%',
                'minWidth': '100%',
                'overflowX': 'auto'
            },
            style_header={
                'fontWeight': 'bold'
            },
            style_cell={
                'fontSize': '12px',
                'textAlign': 'left',
            },
            style_cell_conditional=[
                {'if': {'column_id': 'Seller_Names'},
                 'width': '15%'},
                {'if': {'column_id': 'City'},
                 'width': '10%'},
                {'if': {'column_id': 'Website'},
                 'width': '15%'},
            ],
            fill_width=False,
            tooltip_data=[
                {'Seller_Names': {'value': '**{} {} {} {} {} {} {} {} {} {} {} {}** '.format(row['Service_0'],row['Service_1'],
                                                                                    row['Service_2'],row['Service_3'],
                                                                                    row['Service_4'],row['Service_5'],
                                                                                    row['Service_6'],row['Service_7'],
                                                                                    row['Service_8'],row['Service_8'],
                                                                                    row['Service_10'],row['Service_11']),
                            'type': 'markdown'}
                } for row in table_data.to_dict('records')
            ],
            tooltip_duration=None,
            sort_action='native',
            filter_action="native",
            style_as_list_view=True,
            fixed_columns={'headers': True, 'data': 1},
            id = 'DataTable'
        )
    ])
]

)

page1 =html.Div([
    dbc.Row(
        [
            dbc.Col([
                html.P("Services of Seller"),
                dcc.Graph(
                    figure=chart.pieChart(),
                    id='pieSeller',
                    style={"margin-top":"-10pt"}
                )
            ],style ={'align':'center','borderRight': "1px solid lightgrey","width": "100%"}),
            dbc.Col([
                html.P("Most/Least Services"),
                dbc.Row([dbc.Col(tn, style={"font-size":"55pt", "text-align":"center"}),dbc.Col(bn,style={"font-size":"55pt", "text-align":"center"})],style ={'text-align':'left'}),
                dbc.Row([dbc.Col(ts,style={"font-size":"9pt"}),dbc.Col(bs,style={"font-size":"9pt"})],style ={'text-align':'center'}),
            ],style ={'borderRight': "1px solid lightgrey","width": "100%"}),
            dbc.Col(html.Div([
                html.P( "Total of Car Seller"),
                html.P(str(chart.data.shape[0]), style = {'margin-top':'3%',"font-size":"80px",'text-align':'center'})
            ])),
        ],style={'text-align':'center'}
    ),
    dbc.Row(html.Hr(style ={'borderWidth': "0.3vh", "width": "100%"})),
    dbc.Row([
        dbc.Row([
            dbc.Col(html.Div(
            [
                dbc.Label("Search new Seller"),
                dbc.Input(placeholder="Name+City", type="text", id="search-input"),
                dbc.FormText("Please type Name and City in the box above. Example: Musterautohaus+Musterstadt"),
            ],style={"width":"700px"})),
            dbc.Col([
                html.Hr(style = {"color": "white"}),
                dbc.Button(children="Search",id="search-button", className="me-2",n_clicks=0),
            ])
        ]),
        html.Hr(style = {"color": "white"}),
        html.Hr(style ={'borderWidth': "0.3vh", "width": "100%"}),
        html.Hr(style = {"color": "white"}),
        dbc.Spinner(html.Div(id="loading-output")),
        html.P(id="output"),
        html.Div(id = 'table1',style={"overflow": "auto"})

    ])
])

page2 =html.Div([
    dbc.Row(
        [
            html.P("Services per Seller - Categories", style = {"font-size": "20pt"})

        ],style={'text-align':'center'}
    ),
    dbc.Row(" "),
    dbc.Row(" "),
    dbc.Row(html.Hr(style ={'borderWidth': "0.3vh", "width": "100%"})),
    dbc.Row([
        dbc.Row([
            #dbc.Label("Select Seller"),
            dcc.Dropdown(
                ["Overview"]+chart.data['Seller'].tolist(),
                placeholder= "Select Seller...",
                searchable=False,
                id = 'dropdown'
            )
            ]),
        dbc.Row(html.Hr(style ={'color':'white', "width": "100%"})),
        html.P(id="output",style={"font-weight":"bold"}),
        dcc.Graph(
            figure=chart.bar_chart(),
            id='Barchart',
            style={'height': '442pt', 'width': '100%'}
        )
    ])
])
####final layout of website#####
app.layout = html.Div([dcc.Location(id="url"), sidebar, content])

@app.callback(Output('Barchart', 'figure'), Input('dropdown', 'value'))
def update_barchart(seller):
    new_bar = chart.bar_chart(filter=seller)
    return new_bar

####call of webpage#####
@app.callback(Output("page-content", "children"), [Input("url", "pathname")])
def render_page_content(pathname):
    if pathname == "/":
        return homepage
    elif pathname == "/page-1":
        return page1
    elif pathname == "/page-2":
        return page2
    # If the user tries to reach a different page, return a 404 message
    return dbc.Jumbotron(
        [
            html.H1("404: Not found", className="text-danger"),
            html.Hr(),
            html.P(f"The pathname {pathname} was not recognised..."),
        ]
    )

@app.callback([Output("table1", "children"),Output("output", "children"),Output("pieSeller", 'figure'),Output("loading-output", "children")],
              [Input("search-button","n_clicks"),State("search-input", "value")])
def crawl(n,value):
    if  n is None:
        return dash.no_update,dash.no_update, dash.no_update,dash.no_update
    elif n == 0:
        return dash.no_update,dash.no_update, dash.no_update,dash.no_update
    else:
        name = str(value).split("+")[0]

        sellerdata,piedata = chart.search_table([value])
        #tdata = sellerdata.to_dict('records'),
        #tcolumns = [{"name": i, "id": i} for i in sellerdata.columns]

        table = dbc.Table.from_dataframe(sellerdata, striped=True, bordered=True, hover=True)

        piefig = chart.pieChart(inputData=piedata)
        piefig = piefig.update_traces(textposition='inside', textinfo='label',insidetextorientation='horizontal')

        print("Done Updating")
        return table,name,piefig,""


# @app.callback([Output("pie", "figure"), Output('DataTable','data')], [Input("url", "pathname")])
# def update_homepage(pathname):
#     if pathname == "/":
#         c = Chart()
#         new_table = c.table()
#         new_pie = c.pieChart()
#         return new_pie, new_table.to_dict('records')
#     else:
#         return dash.no_update, dash.no_update


if __name__ == '__main__':
    app.run_server(debug=True)

