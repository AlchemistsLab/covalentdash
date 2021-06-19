# -*- coding: utf-8 -*-
import json
import base64
import datetime
import requests
import pathlib
import math
import pandas as pd
import flask
import dash
import dash_core_components as dcc
import dash_html_components as html

import plotly.graph_objs as go
import dash_bootstrap_components as dbc
import plotly.express as px
from dash.dependencies import Input, Output, State
from plotly import tools


def fig1(data):
    colors = {
    'background': '#000220',
    'text': '#FFFFFF'
}

    today=datetime.datetime.today().strftime("%Y -%m -%d")
    df_nested=data
    df = df_nested.loc[df_nested['timestamp']>=today].groupby(['contract_name','contract_ticker_symbol']).mean('close.quote').reset_index()
    fig = px.pie(df, values='close.quote', names='contract_name',labels={             "contract_name":'Contract Name',
                     "close.quote": "USD Value"} , title='Asset Allocation', color_discrete_sequence=px.colors.sequential.Plasma)
    fig.update_traces(textposition='inside')
    # fig.update_layout(uniformtext_minsize=12, uniformtext_mode='hide')
    fig.update_layout(plot_bgcolor=colors['background'], paper_bgcolor=colors['background'],font_color=colors['text']
)
    
    return fig


def fig2(data):
    colors = {
    'background': '#000220',
    'text': '#FFFFFF'
}

    df_nested=data

    fig2=px.line(df_nested, x="timestamp", y="close.quote", color="contract_name",line_group="contract_ticker_symbol",labels={
                    "contract_name":'Contract Name',
                     "timestamp": "Date",
                     "close.quote": "USD Value",
                     "contract_ticker_symbol": "Ticker"
                 }, title='Asset Value Over Time', hover_name="contract_ticker_symbol",)
    fig2.update_layout(plot_bgcolor=colors['background'], paper_bgcolor=colors['background'],font_color=colors['text'])
    
    return fig2


app = dash.Dash(
    __name__, meta_tags=[{"name": "viewport", "content": "width=device-width"}],
)
app.title = ""

server = app.server

PATH = pathlib.Path(__file__).parent


# API Requests for news div
news_requests = requests.get(
    "https://newsapi.org/v2/top-headlines?sources=bbc-news&apiKey=da8e2e705b914f9f86ed2e9692e66012"
)

# API Call to update news
def update_news():
    json_data = news_requests.json()["articles"]
    df = pd.DataFrame(json_data)
    df = pd.DataFrame(df[["title", "url"]])
    max_rows = 10
    return html.Div(
        children=[
            html.P(className="p-news", children="Headlines"),
            html.P(
                className="p-news float-right",
                children="Last update : "
                + datetime.datetime.now().strftime("%H:%M:%S"),
            ),
            html.Table(
                className="table-news",
                children=[
                    html.Tr(
                        children=[
                            html.Td(
                                children=[
                                    html.A(
                                        className="td-link",
                                        children=df.iloc[i]["title"],
                                        href=df.iloc[i]["url"],
                                        target="_blank",
                                    )
                                ]
                            )
                        ]
                    )
                    for i in range(min(len(df), max_rows))
                ],
            ),
        ]
    )

# Dash App Layout
app.layout = html.Div(
    className="row",
    children=[
        # Interval component for live clock
        dcc.Interval(id="interval", interval=1 * 1000, n_intervals=0),
        # Interval component for ask bid updates
        dcc.Interval(id="i_bis", interval=1 * 2000, n_intervals=0),
        # Interval component for graph updates
        dcc.Interval(id="i_tris", interval=1 * 5000, n_intervals=0),
        # Interval component for graph updates
        dcc.Interval(id="i_news", interval=1 * 60000, n_intervals=0),
        # Left Panel Div
        html.Div(
            className="three columns div-left-panel",
            children=[
                # Div for Left Panel App Info
                html.Div(
                    className="div-info",
                    children=[
                        html.Img(
                            className="logo", src=app.get_asset_url("covalent.png")
                        ),
                        html.H6(className="title-header", children="Covalent Vision"),
                        html.P(
                            """
                            Covalent Dashboard provides portfolio tracking services across chains
                            """
                        ),
                       
                    ],
                ),

                # Div for News Headlines
                html.Div(
                    className="div-news",
                    children=[html.Div(id="news", children=update_news())],
                ),
            ],
        ),
        # Right Panel Div
        html.Div(
            className="nine columns div-right-panel",
            children=[
               
             
                # Panel for orders
                html.Div(
                    id="bottom_panel",
                    className="row div-bottom-panel",
                    children=[
                        html.Div(
                            className="display-inlineblock",
                            children=[
                                dcc.Input(id="address", placeholder="Enter wallet address...", type="text"),
                                dcc.Dropdown(id='chain_id',placeholder="Select Chain", options = [
                                            {"label": "Ethereum", "value": "1"},
                                            {"label": "Matic", "value": "137"},
                                            {"label": "Binance Smart Chain", "value": "56"},
                                            {"label": "Avalanche", "value": "43114"},
                                            {"label": "Fantom", "value": "250"}
                                        ],
                                    value=[],
                
        ),
    

               
                            ],
                        ),
                        html.Div(
                            className="display-inlineblock float-right",
                            children=[
                               html.Button('Add Wallet', id='btn-1', n_clicks=0)
                                
                            ],
                        ),
                        html.Div(id='container'),
                    ],
                ),
            ],
        ),
       
        
    ],
)


def normalize(data):
    df=pd.json_normalize(data,record_path=['holdings'],meta=['contract_ticker_symbol','contract_name',"contract_address"])
    df=df[['contract_ticker_symbol','contract_name',"contract_address",'timestamp','close.quote']]
    return df

def set_time(data):
    return pd.to_datetime(data['timestamp'])

@app.callback(Output('container', 'children'),
              Input("chain_id", "value"),
               Input("address", "value"),)

def display(value,address):
    ctx = dash.callback_context
  
    api_key= 'ckey_57eeb470248541708eeaf028c9d'
 

    if not ctx.triggered:
       pass
    else:
        chain_id= value
        address= address
        response = requests.get(f"https://api.covalenthq.com/v1/{chain_id}/address/{address}/portfolio_v2/?format=format%3Dcsv&key={api_key}").json()

        data=response['items']
        data=normalize(data)
        data['timestamp']=set_time(data)

   
    return [

        dcc.Graph(
            id='graph1',
            figure=fig1(data)
        ),  

        dcc.Graph(
            id='graph2',
            figure=fig2(data)
        ),  
    
    ]

# Dynamic Callbacks









# Function to open or close STYLE or STUDIES menu
def generate_open_close_menu_callback():
    def open_close_menu(n, className):
        if n == 0:
            return "not_visible"
        if className == "visible":
            return "not_visible"
        else:
            return "visible"

    return open_close_menu


# Function for hidden div that stores the last clicked menu tab
# Also updates style and studies menu headers
def generate_active_menu_tab_callback():
    def update_current_tab_name(n_style, n_studies):
        if n_style >= n_studies:
            return "Style", "span-menu selected", "span-menu"
        return "Studies", "span-menu", "span-menu selected"

    return update_current_tab_name


# Function show or hide studies menu for chart
def generate_studies_content_tab_callback():
    def studies_tab(current_tab):
        if current_tab == "Studies":
            return {"display": "block", "textAlign": "left", "marginTop": "30"}
        return {"display": "none"}

    return studies_tab


# Function show or hide style menu for chart
def generate_style_content_tab_callback():
    def style_tab(current_tab):
        if current_tab == "Style":
            return {"display": "block", "textAlign": "left", "marginTop": "30"}
        return {"display": "none"}

    return style_tab





# Callback to update news
@app.callback(Output("news", "children"), [Input("i_news", "n_intervals")])
def update_news_div(n):
    return update_news()


if __name__ == "__main__":
    app.run_server(debug=False)
