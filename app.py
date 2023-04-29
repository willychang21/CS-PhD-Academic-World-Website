from dash import Dash, html, dcc, Input, Output, dash_table, State, ctx
from mongodb_utils import get_mongodb_data
from neo4j_utils import get_faculties, get_all_keywords, get_all_universities
from neo4j_utils import get_top_10_schools_by_keyword_and_year
from neo4j_utils import get_keyword_scores_by_school
from neo4j_utils import get_keyword_scores_by_faculty_and_year
from mysql_utils import fetch_all_favorite_keywords, add_favorite_keyword, delete_favorite_keyword
from mysql_utils import top10_faculty_related_favorite_keywords, top10_unversity_related_favorite_keywords
import dash_bootstrap_components as dbc
import plotly.express as px

# create the Dash app
app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

### MongoDB Data###
# get the data from MongoDB
data = get_mongodb_data()

# create a list of dictionaries to use as the data source for the DataTable
table_data = []
for row in data:
    table_data.append({
        'Keyword': row['keyword'],
        'Publication Count': row['publication count']
    })

### Neo4j Data###
keyword_options = [{'label': name, 'value': name}
                   for name in get_all_keywords()]

university_options = [{"label": school, "value": school}
                      for school in get_all_universities()]

faculties_options = [{'label': faculty, 'value': faculty}
                     for faculty in get_faculties()]

# create the layout
app.layout = dbc.Container([
    dbc.Row([
        html.H1("Finding most match universities and faculties for CS PhD application",
                style={'textAlign': 'center'}),
    ], align="center", justify="center", class_name='pt-3'),

    ### First Row ###
    dbc.Row([
        ### First widget ###
        dbc.Col([
            html.H1('Top 10 most popular research keywords'),
            dbc.Row([
                dcc.RangeSlider(
                    id='year-slider',
                    min=1982,
                    max=2023,
                    value=[1982, 2023],
                    marks={str(year): str(year)
                           for year in range(1982, 2024, 5)},
                    tooltip={"placement": "top", "always_visible": True}
                )
            ], class_name='my-3'),
            dash_table.DataTable(
                id='keyword-table',
                columns=[{'name': i, 'id': i} for i in table_data[0].keys()],
                data=table_data,
                editable=False,
                row_deletable=False,
                style_cell={'textAlign': 'left'},
                style_header={
                    'backgroundColor': 'rgb(30, 30, 30)', 'color': 'white', 'textAlign': 'center'},
            )
        ], width=5),
        ### Second Widget ###
        dbc.Col([
            html.H1("Top 10 Universities by Keyword and Year"),
            dbc.Row([
                    html.H3("Keyword"),
                    dcc.Dropdown(
                        id="keyword-dropdown",
                        options=keyword_options,
                        value=keyword_options[0]['value']
                    )
                    ], class_name='my-3'),

            dbc.Row([
                html.H3("Year Range"),
                dcc.RangeSlider(
                    id="year-range-slider",
                    min=1982,
                    max=2023,
                    step=1,
                    value=[1982, 2023],
                    marks={
                        str(year): str(year)
                        for year in range(1982, 2024, 5)
                    }
                )
            ], class_name='my-3'),

            dash_table.DataTable(
                id="results-table",
                columns=[{"name": "University", "id": "university"},
                         {"name": "Publication Count", "id": "count"},],
                editable=False,
                row_deletable=False,
                style_cell={'textAlign': 'left'},
                style_header={
                    'backgroundColor': 'rgb(30, 30, 30)', 'color': 'white', 'textAlign': 'center'},
            )
        ], width=5),
    ], class_name='p-3 d-flex justify-content-around'),

    ### Second Row ###
    dbc.Row([
        ### Third Widget ###
        dbc.Col([
            html.H1("Top 10 Keywords by School"),
            html.Div([
                html.H3("University"),
                dcc.Dropdown(
                    id="university",
                    options=university_options,
                    value=university_options[0]["value"],
                )
            ]),
            html.Div([
                dcc.Graph(
                    id="keyword-scores",
                    figure={}
                )
            ]),
        ], width=5),

        ### Fourth Widget ###
        dbc.Col([
            ### Fourth widget ###
            html.H1('Top 10 Keywords of Given year & Faculty'),
            dbc.Row([
                html.H3("Faculty"),
                dcc.Dropdown(
                    id="faculty-dropdown",
                    options=faculties_options,
                    value=faculties_options[2]["value"],
                )
            ], className='my-3'),

            dbc.Row([
                html.H3("Year Range"),
                dcc.RangeSlider(
                    id="year-range-slider-2",
                    min=1982,
                    max=2023,
                    step=1,
                    value=[1982, 2023],
                    marks={
                        str(year): str(year)
                        for year in range(1982, 2024, 5)
                    }
                )
            ], class_name='my-3'),

            html.Div(id='table-container')
        ], width=5),
    ], class_name='p-3 d-flex justify-content-around'),

    ### Third Row ###
    dbc.Row([
        html.H1("Favorite Keywords Recommendation",
                style={'textAlign': 'center'}),
    ], align="center", justify="center", class_name='pt-3'),

    dbc.Row([

        ### Add to Favorite Keywords ###
        dbc.Col([
            html.H2("Favorite Keywords"),
            dbc.Row([
                dbc.Col([
                    dcc.Dropdown(
                        id='keyword-dropdown-2',
                        options=keyword_options,
                        value='',
                    ),
                ]),
                dbc.Col([
                    dbc.Button('Add to Favorites', id='add-to-fav-button',
                               n_clicks=0, color='primary', className='mr-2')
                ]),
            ], className='my-3'),
            dash_table.DataTable(
                id='fav-keywords-table',
                columns=[{"name": "Favorite Keywords", "id": "keywords"}],
                data=[{"keywords": k}
                      for k in fetch_all_favorite_keywords()],
                editable=True,
                sort_action="native",
                sort_mode="multi",
                row_deletable=True,
                page_size=10,
                selected_rows=[],
                style_cell={'textAlign': 'left'},
                style_header={
                    'backgroundColor': 'rgb(30, 30, 30)', 'color': 'white', 'textAlign': 'center'},

            ),
        ], width=3),
        ### Fifth Widget ###
        dbc.Col([
            html.H2("Top 10 Recommended Faculty"),
            dash_table.DataTable(
                id='top-faculty-table',
                columns=[{"name": "Faculty-Related Keywords", "id": "keywords"}],
                data=[{"keywords": k}
                      for k in top10_faculty_related_favorite_keywords()],
                sort_action="native",
                sort_mode="multi",
                page_size=10,
                style_cell={'textAlign': 'left'},
                style_header={
                    'backgroundColor': 'rgb(30, 30, 30)', 'color': 'white', 'textAlign': 'center'},
            ),
        ], width=3),

        ### Sixth Widget ###
        dbc.Col([
            html.H2("Top 10 Recommended University"),
            dash_table.DataTable(
                id='top-university-table',
                columns=[
                    {"name": "University-Related Keywords", "id": "keywords"}],
                data=[{"keywords": k}
                      for k in top10_unversity_related_favorite_keywords()],
                sort_action="native",
                sort_mode="multi",
                page_size=10,
                style_cell={'textAlign': 'left'},
                style_header={
                    'backgroundColor': 'rgb(30, 30, 30)', 'color': 'white', 'textAlign': 'center'},
            ),
        ], width=3),
    ], class_name='p-3 d-flex justify-content-around'),
], fluid=True)

### First Widget Callbacks ###


@app.callback(
    Output('keyword-table', 'data'),
    Input('year-slider', 'value')
)
def update_table_data(year_range):
    # get the data from MongoDB based on the selected year range
    data = get_mongodb_data(year_range[0], year_range[1])
    # create a list of dictionaries to use as the data source for the DataTable
    table_data = []
    for row in data:
        table_data.append({
            'Keyword': row['keyword'],
            'Publication Count': row['publication count']
        })
    return table_data

### Second Widget Callbacks ###


@app.callback(
    Output("results-table", "data"),
    [Input("keyword-dropdown", "value"),
     Input("year-range-slider", "value")]
)
def update_results_table(keyword, year_range):
    start_year, end_year = year_range
    # query the neo4j database for the top 10 schools
    df = get_top_10_schools_by_keyword_and_year(keyword, start_year, end_year)

    # return the data for the dash_table component
    return df.to_dict("records")

### Third Widget Callbacks ###


@app.callback(
    Output(component_id='keyword-scores', component_property='figure'),
    [Input(component_id='university', component_property='value')]
)
def update_keyword_scores(university):
    df = get_keyword_scores_by_school(university)
    fig = {
        'data': [{
            'values': df['total score'],
            'labels': df['keyword'],
            'type': 'pie',
            'marker': {'colors': ['blue', 'red', 'green', 'orange', 'purple', 'pink', 'brown', 'gray', 'yellow', 'teal']}
        }],
        'layout': {
            'title': f'Top 10 keyword scores for {university}'
        }
    }
    return fig

### Fourth Widget Callbacks ###
# define the callback to update the table


@app.callback(
    Output('table-container', 'children'),
    Input('faculty-dropdown', 'value'),
    Input('year-range-slider-2', 'value')
)
def update_table(faculty, year_range):
    start_year, end_year = year_range
    df = get_keyword_scores_by_faculty_and_year(faculty, start_year, end_year)
    table = dash_table.DataTable(
        data=df.to_dict('records'),
        columns=[{'name': col, 'id': col} for col in df.columns],
        style_cell={'textAlign': 'left'},
        style_header={
            'backgroundColor': 'rgb(30, 30, 30)', 'color': 'white', 'textAlign': 'center'},
        style_data_conditional=[
            {'if': {'row_index': 'odd'}, 'backgroundColor': 'rgb(248, 248, 248)'}]
    )
    return table

### fifth and sixth widgets callbacks ###
# callback to add keyword to favorite table on button click


@app.callback(
    [Output('fav-keywords-table', 'data', allow_duplicate=True),
     Output('top-faculty-table', 'data', allow_duplicate=True),
     Output('top-university-table', 'data', allow_duplicate=True)],
    [Input('add-to-fav-button', 'n_clicks')],
    [State('keyword-dropdown-2', 'value'),
     State('fav-keywords-table', 'data')],
    prevent_initial_call=True
)
def update_favorite_table(n_clicks, selected_keyword, table_data):
    if n_clicks is None:
        print("no click")
        # This means that the callback was triggered by something other than the button click
        return table_data, [], []

    if 'add-to-fav-button' == ctx.triggered_id and selected_keyword:
        print("click btn")
        if {'keywords': selected_keyword} not in table_data:
            add_favorite_keyword(selected_keyword)
            table_data.append({'keywords': selected_keyword})
            top_faculty = [{"keywords": k}
                           for k in top10_faculty_related_favorite_keywords()]
            top_university = [{"keywords": k}
                              for k in top10_unversity_related_favorite_keywords()]
            print("top faculty", top_faculty)
            print("top university", top_university)
            return table_data, top_faculty, top_university

    print('error return empty')
    return table_data, [], []

# callback to delete keyword from favorite table on row delete


@app.callback(
    [Output('fav-keywords-table', 'data', allow_duplicate=True),
     Output('top-faculty-table', 'data', allow_duplicate=True),
     Output('top-university-table', 'data', allow_duplicate=True)],
    [Input('fav-keywords-table', 'data'),
     Input('top-faculty-table', 'data'),
     Input('top-university-table', 'data')],
    prevent_initial_call=True
)
def delete_favorite_keyword_callback(data, faculty_data, university_data):
    # get list of keywords in the table before the row was deleted
    keywords_before_delete = fetch_all_favorite_keywords()

    # get list of keywords in the table after the row was deleted
    keywords_after_delete = [row['keywords'] for row in data]

    # find the keyword that was deleted
    deleted_keyword = None
    if len(set(keywords_before_delete).difference(set(keywords_after_delete))) > 0:
        deleted_keyword = set(keywords_before_delete).difference(
            set(keywords_after_delete)).pop()

    # delete the keyword from the database
    if deleted_keyword:
        delete_favorite_keyword(deleted_keyword)
        top_faculty = [{"keywords": k}
                       for k in top10_faculty_related_favorite_keywords()]
        top_university = [{"keywords": k}
                          for k in top10_unversity_related_favorite_keywords()]
        return data, top_faculty, top_university

    print('error return empty')
    # return the updated table data
    return data, faculty_data, university_data


if __name__ == "__main__":
    app.run_server(debug=True)
