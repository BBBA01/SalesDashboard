# import all the modules
from distutils.log import debug
from turtle import color, position, width
from click import style
import dash
from dash import dcc, html
from flask import Flask
from dash.dependencies import Input, Output
import pickle
import mysql.connector
from matplotlib.pyplot import figure
import plotly.express as px
import pandas as pd


# SQL connection
cnx = mysql.connector.connect(user='aniket', password='ani261201',
                              host='localhost', database='sales_db')
cursor = cnx.cursor()

query = "SELECT `Order ID`, `Order Date`, `Purchase Address`, `Product`, `Quantity Ordered`, `Price Each`, `Sales`, `City`, `Hour`, `Month`, `Count` FROM `orders`;"
cursor.execute(query)


df = pd.DataFrame(cursor.fetchall(), columns=['Order ID', 'Order Date', 'Purchase Address', 'Product', 'Quantity Ordered', 'Price Each', 'Sales', 'City', 'Hour', 'Month', 'Count'])

cursor.close()
cnx.close()

with open('figures.pickle', 'rb') as handle:
    figures = pickle.load(handle)

product_options = [{'label': product, 'value': product } for product in df['Product'].unique()]

merged_df = df.groupby(["Product", "Month"]).agg({
    "Quantity Ordered": "sum",
    "Price Each": "mean",
    "Sales": "sum",
}).reset_index()

merged_df["Average Purchase Value"] = merged_df["Sales"] / merged_df["Quantity Ordered"]


# Initiate the app
server = Flask(__name__)
app = dash.Dash(__name__, server=server)

# Read the file


# Build the components


# Design the app layout
app.layout = html.Div(children=[
    # header
   html.H1(children=[html.B(html.Span('Sales Analysis', style={'font-size': '2.3rem' ,'font-family': 'Helvetica, Arial, sans-serif','font-weight': 'bold'})), html.Span(' dashboard', style={'font-family': 'Helvetica, Arial, sans-serif', 'font-weight': 'lighter'})], style={'margin-left': '20px', 'background-color': 'black', 'color': 'white'}),

    # First row of graphs
    html.Div(className='row',  children=[
        html.Div(className='col-xs-4', style={'width': '34%'}, children=[
            dcc.Graph(id='graph1', figure=figures['fig1'])
        ]),
        html.Div(className='col-xs-4', style={'width': '31%', 'top': 86, 'position':'absolute', 'right': 522}, children=[
            dcc.Graph(id='graph2', figure=figures['fig2'])
        ]),
        html.Div(className='col-xs-4',style={'width': '50%', 'top': 1429, 'position': 'absolute', 'right': 10},  children=[
            dcc.Graph(id='graph3', figure=figures['fig3'])
        ])
    ]),

    # Second row of graphs
    html.Div(className='row', children=[
        html.Div(className='col-xs-6', style={'width': '50%', 'top': 531, 'position': 'absolute', 'right': 0},  children=[
            dcc.Graph(id='graph4', figure=figures['fig4'])
        ]),
        html.Div(className='col-xs-6',style={'width': '50%'},  children=[
            dcc.Graph(id='graph5', figure=figures['fig5'])
        ]),
        html.Div(className='col-xs-6',style={'width': '50%', 'top': 1429, 'position': 'absolute'},  children=[
            dcc.Graph(id='graph6', figure=figures['fig6'])
        ])
    ]),

    # Third row of graphs
    html.Div(className='row', children=[
        html.Div(className='col-xs-4', style={'width': '110%' , 'top': 979, 'position': 'absolute'},  children=[
            dcc.Graph(id='graph7', figure=figures['fig7'])
        ]),

        html.Div(className='col-xs-8', style={'width': '35%', 'top': 48, 'position': 'absolute', 'right':0}, children=[  
           dcc.Dropdown( 
    id='product-dropdown', 
    options=product_options, 
    value=product_options[0]['value'], 
    style={
        'width': '727px',
        'background-color': 'black',
        'color': 'black',
        'font-family': 'Helvetica, Arial, sans-serif',
        'font-size': '14px',
    }
),
            dcc.Graph(id='graph8', figure={})
        ]),
        
])





], className='container-fluid', style={'background-color': 'black',
    'color': 'white',
    'margin': 0,
    'padding': 0,
    'height': '100vh',
    'width': '100vw',
    'position': 'absolute',
    'top': 0,
    'left': 0})

@app.callback(Output('graph8', 'figure'), [Input('product-dropdown', 'value')])

def update_fig8(product):
    # Filter the data based on the selected product
    filtered_df = merged_df[merged_df['Product'] == product]

    # Create a scatter chart of Average Purchase Value vs Month
    fig = px.scatter(filtered_df, x="Month", y="Average Purchase Value", color="Product", color_discrete_sequence=px.colors.qualitative.Dark24, hover_data=["Month", "Average Purchase Value"])

    fig.update_xaxes(dtick=1)

    fig.update_layout(plot_bgcolor="black", paper_bgcolor="black")

    fig.update_traces(marker=dict(size=10, line=dict(width=1, color="black"), color=filtered_df['Product'].map(lambda p: px.colors.qualitative.Dark24[df['Product'].unique().tolist().index(p)])))

    fig.update_layout(font=dict(color='white'), hoverlabel=dict(font=dict(color='black')))

    fig.update_traces(mode="markers", marker=dict(size=10, line=dict(width=1, color="black")), hovertemplate="Month: %{x}<br>Average Purchase Value: %{y}")

    fig.update_layout(title="<b>Average Purchase Values</b>", title_font=dict(size=20), xaxis_title="Months", yaxis_title="Average Purchase Value", font=dict(size=14))

    color_map = {product_options[i]['value']: px.colors.qualitative.Dark24[i] for i in range(len(product_options))}
    fig.update_traces(marker_color=color_map[product])


    return fig


# Run the app
app.run_server(debug=True)