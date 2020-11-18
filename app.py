# -*- coding: utf-8 -*-
"""
Created on Wed Nov 18 13:18:08 2020

@author: Claytonious
"""

import dash
import dash_core_components as dcc
import dash_html_components as html
import networkx as nx
import plotly.graph_objs as go

import pandas as pd
from colour import Color
from datetime import datetime
from textwrap import dedent as d
import json
import ast


# import the css template, and pass the css template into dash
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.title = "Transaction Network"

YEAR=[2006, 2019]
PERSON="Kim Jong Un"

##############################################################################################################################################################
def network_graph(yearRange, AccountToSearch):

    network = pd.read_csv('kcna_test.csv')
    

    # filter the record by datetime, to enable interactive control through the input box
    network['Datetime'] = "" # add empty Datetime column to edge1 dataframe
    accountSet=set() # contain unique account
    for index in range(0,len(network)):
        network['Datetime'][index] = datetime.strptime(str(network['year'][index]), '%Y')
        if network['Datetime'][index].year<yearRange[0] or network['Datetime'][index].year>yearRange[1]:
            network.drop(axis=0, index=index, inplace=True)
            continue
        entities = ast.literal_eval(network['entities'][index])
        for entity in entities:
            accountSet.add(entity)


    # to define the centric point of the networkx layout
    shells=[]
    shell1=[]
    shell1.append(AccountToSearch)
    shells.append(shell1)
    shell2=[]
    for ele in accountSet:
        if ele!=AccountToSearch:
            shell2.append(ele)
    shells.append(shell2)


    #network graph
    G = nx.Graph()
    #add entities as nodes
    for entities in network['entities']:
        entities = ast.literal_eval(entities)
        G.add_nodes_from(entities)
    #add edges
    for entities in network['entities']:
        entities = ast.literal_eval(entities)
        if len(entities) > 1:
            for i in range(len(entities)-1):
                G.add_edges_from([(str(entities[i]),str(entities[i+1]))])
    # pos = nx.layout.spring_layout(G)
    # pos = nx.layout.circular_layout(G)
    # nx.layout.shell_layout only works for more than 3 nodes
    if len(shell2)>1:
        pos = nx.drawing.layout.shell_layout(G, shells)
    else:
        pos = nx.drawing.layout.spring_layout(G)
    for node in G.nodes:
        G.nodes[node]['pos'] = list(pos[node])


    if len(shell2)==0:
        traceRecode = []  # contains edge_trace, node_trace, middle_node_trace

        node_trace = go.Scatter(x=tuple([1]), y=tuple([1]), text=tuple([str(AccountToSearch)]), textposition="bottom center",
                                mode='markers+text',
                                marker={'size': 50, 'color': 'LightSkyBlue'})
        traceRecode.append(node_trace)

        node_trace1 = go.Scatter(x=tuple([1]), y=tuple([1]),
                                mode='markers',
                                marker={'size': 50, 'color': 'LightSkyBlue'},
                                opacity=0)
        traceRecode.append(node_trace1)

        figure = {
            "data": traceRecode,
            "layout": go.Layout(title='Association Visualization', showlegend=False,
                                margin={'b': 40, 'l': 40, 'r': 40, 't': 40},
                                xaxis={'showgrid': False, 'zeroline': False, 'showticklabels': False},
                                yaxis={'showgrid': False, 'zeroline': False, 'showticklabels': False},
                                height=600
                                )}
        return figure


    traceRecode = []  # contains edge_trace, node_trace, middle_node_trace
    ############################################################################################################################################################
    colors = list(Color('lightcoral').range_to(Color('darkred'), len(G.edges())))
    colors = ['rgb' + str(x.rgb) for x in colors]

    index = 0
    for edge in G.edges:
        x0, y0 = G.nodes[edge[0]]['pos']
        x1, y1 = G.nodes[edge[1]]['pos']
        weight = 5
        trace = go.Scatter(x=tuple([x0, x1, None]), y=tuple([y0, y1, None]),
                           mode='lines',
                           line={'width': weight},
                           marker=dict(color=colors[index]),
                           line_shape='spline',
                           opacity=1)
        traceRecode.append(trace)
        index = index + 1
    ###############################################################################################################################################################
    node_trace = go.Scatter(x=[], y=[], hovertext=[], text=[], mode='markers+text', textposition="bottom center",
                            hoverinfo="text", marker={'size': 50, 'color': 'LightSkyBlue'})
    
    index = 0
    for node in G.nodes():
        x, y = G.nodes[node]['pos']
        hovertext = "Name: " + str(node)
        text = str(node)
        node_trace['x'] += tuple([x])
        node_trace['y'] += tuple([y])
        node_trace['hovertext'] += tuple([hovertext])
        node_trace['text'] += tuple([text])
        index = index + 1

    traceRecode.append(node_trace)
    ################################################################################################################################################################
    # middle_hover_trace = go.Scatter(x=[], y=[], hovertext=[], mode='markers', hoverinfo="text",
    #                                 marker={'size': 20, 'color': 'LightSkyBlue'},
    #                                 opacity=0)

    # index = 0
    # for edge in G.edges:
    #     x0, y0 = G.nodes[edge[0]]['pos']
    #     x1, y1 = G.nodes[edge[1]]['pos']
    #     hovertext = "From: " + str(G.edges[edge]['Source']) + "<br>" + "To: " + str(
    #         G.edges[edge]['Target']) + "<br>" + "TransactionAmt: " + str(
    #         G.edges[edge]['TransactionAmt']) + "<br>" + "TransactionDate: " + str(G.edges[edge]['Date'])
    #     middle_hover_trace['x'] += tuple([(x0 + x1) / 2])
    #     middle_hover_trace['y'] += tuple([(y0 + y1) / 2])
    #     middle_hover_trace['hovertext'] += tuple([hovertext])
    #     index = index + 1

    # traceRecode.append(middle_hover_trace)
    #################################################################################################################################################################
    figure = {
        "data": traceRecode,
        "layout": go.Layout(title='Interactive Network Visualization', showlegend=False, hovermode='closest',
                            margin={'b': 40, 'l': 40, 'r': 40, 't': 40},
                            xaxis={'showgrid': False, 'zeroline': False, 'showticklabels': False},
                            yaxis={'showgrid': False, 'zeroline': False, 'showticklabels': False},
                            height=600,
                            clickmode='event+select',
                            annotations=[
                                dict(
                                    ax=(G.nodes[edge[0]]['pos'][0] + G.nodes[edge[1]]['pos'][0]) / 2,
                                    ay=(G.nodes[edge[0]]['pos'][1] + G.nodes[edge[1]]['pos'][1]) / 2, axref='x', ayref='y',
                                    x=(G.nodes[edge[1]]['pos'][0] * 3 + G.nodes[edge[0]]['pos'][0]) / 4,
                                    y=(G.nodes[edge[1]]['pos'][1] * 3 + G.nodes[edge[0]]['pos'][1]) / 4, xref='x', yref='y',
                                    showarrow=True,
                                    arrowhead=3,
                                    arrowsize=4,
                                    arrowwidth=1,
                                    opacity=1
                                ) for edge in G.edges]
                            )}
    return figure
######################################################################################################################################################################
# styles: for right side hover/click component
styles = {
    'pre': {
        'border': 'thin lightgrey solid',
        'overflowX': 'scroll'
    }
}

app.layout = html.Div([
    #########################Title
    html.Div([html.H1("KCNA Named Entity Network")],
             className="row",
             style={'textAlign': "center"}),
    #############################################################################################define the row
    html.Div(
        className="row",
        children=[
            ##############################################left side two input components
            html.Div(
                className="two columns",
                children=[
                    dcc.Markdown(d("""
                            **Time Range To Visualize**

                            Slide the bar to define year range.
                            """)),
                    html.Div(
                        className="twelve columns",
                        children=[
                            dcc.RangeSlider(
                                id='my-range-slider',
                                min=2006,
                                max=2019,
                                step=1,
                                value=[2006, 2019],
                                marks={
                                    2006: {'label': '2006'},
                                    2009: {'label': '2009'},
                                    2011: {'label': '2011'},
                                    2015: {'label': '2015'},
                                    2017: {'label': '2017'},
                                    2019: {'label': '2019'}
                                }
                            ),
                            html.Br(),
                            html.Div(id='output-container-range-slider')
                        ],
                        style={'height': '300px'}
                    ),
                    html.Div(
                        className="twelve columns",
                        children=[
                            dcc.Markdown(d("""
                            **Account To Search**

                            Input the account to visualize.
                            """)),
                            dcc.Input(id="input1", type="text", placeholder="Account"),
                            html.Div(id="output")
                        ],
                        style={'height': '300px'}
                    )
                ]
            ),

            ############################################middle graph component
            html.Div(
                className="eight columns",
                children=[dcc.Graph(id="my-graph",
                                    figure=network_graph(YEAR, PERSON))],
            ),

        ]
    )
])

###################################callback for left side components
@app.callback(
    dash.dependencies.Output('my-graph', 'figure'),
    [dash.dependencies.Input('my-range-slider', 'value'), dash.dependencies.Input('input1', 'value')])
def update_output(value,input1):
    YEAR = value
    PERSON = input1
    return network_graph(value, input1)
    # to update the global variable of YEAR and ACCOUNT
################################callback for right side components
@app.callback(
    dash.dependencies.Output('hover-data', 'children'),
    [dash.dependencies.Input('my-graph', 'hoverData')])
def display_hover_data(hoverData):
    return json.dumps(hoverData, indent=2)


@app.callback(
    dash.dependencies.Output('click-data', 'children'),
    [dash.dependencies.Input('my-graph', 'clickData')])
def display_click_data(clickData):
    return json.dumps(clickData, indent=2)



if __name__ == '__main__':
    app.run_server(debug=False)
