from dash import Dash, dash_table, dcc, html, Input, Output, State, callback
import pandas as pd
import dash_auth
import webbrowser
import json
import os
from dotenv import load_dotenv
load_dotenv()

# Path to your CSV file
csv = './data.csv'

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

VALID_USERNAME_PASSWORD_PAIRS = {
    os.getenv('USERNAME'): os.getenv('PASSWORD')
}

app = Dash(__name__, external_stylesheets=external_stylesheets)

auth = dash_auth.BasicAuth(
    app,
    VALID_USERNAME_PASSWORD_PAIRS
)

# Load DataFrame from CSV
def load_data():
    df = pd.read_csv(csv)
    df = df[['linkname', 'linkdescription', 'category', 'link']]
    df['id'] = df['linkname']
    df.set_index('id', inplace=True, drop=False)
    return df

app.layout = html.Div([
    dash_table.DataTable(
        id='datatable-interactivity',
        columns=[
            {
                "name": i,
                "id": i,
                "deletable": True,
                "selectable": True,
                "presentation": "input"  # All columns are editable
            } for i in ['linkname', 'linkdescription', 'category', 'link']
        ],
        data=load_data().to_dict('records'),  # Initial data load
        editable=True,
        filter_action="native",
        sort_action="native",
        sort_mode="multi",
        column_selectable="single",
        row_selectable="multi",
        row_deletable=True,
        selected_columns=[],
        selected_rows=[],
        page_action="native",
        page_current=0,
        page_size=10,
        style_table={'width': '100%', 'overflowX': 'auto'},
        style_cell={
            'textAlign': 'left',
            'maxWidth': '300px',
            'whiteSpace': 'normal',
            'overflow': 'hidden',
            'textOverflow': 'ellipsis',
        },
        style_header={
            'textAlign': 'left',
            'fontWeight': 'bold'
        },
        style_data={
            'whiteSpace': 'normal',
            'height': 'auto',
        },
        css=[{
            'selector': 'td.cell--selected div',
            'rule': 'max-width: 300px; text-overflow: ellipsis; overflow: hidden;'
        }]
    ),
    html.Div(id='datatable-interactivity-container'),
    html.Div(id='hidden-div', style={'display': 'none'})  # Hidden Div for storing URLs
], style={'width': '100%', 'display': 'block', 'padding': '20px'})  # Ensuring full width and padding

# Combined Callback for Loading and Modifying Data
@callback(
    Output('datatable-interactivity', 'data'),
    Input('datatable-interactivity', 'data'),
    State('datatable-interactivity', 'data_previous')
)
def manage_data(current_data, previous_data):
    df = load_data()  # Load the latest data

    # If previous_data is None, it's the initial page load
    if previous_data is None:
        return df.to_dict('records')

    # If there is previous data, handle modifications
    current_df = pd.DataFrame(current_data)
    previous_df = pd.DataFrame(previous_data)

    # Handle deletions: Rows in previous_data but not in current_data
    deleted_rows = previous_df.merge(current_df, how='outer', indicator=True).loc[lambda x: x['_merge'] == 'left_only']
    if not deleted_rows.empty:
        current_df.to_csv(csv, index=False)
        return load_data().to_dict('records')

    # Handle updates: Save all changes back to CSV
    current_df.to_csv(csv, index=False)

    return current_df.to_dict('records')

@callback(
    Output('datatable-interactivity-container', "children"),
    Input('datatable-interactivity', "derived_virtual_data"),
    Input('datatable-interactivity', "derived_virtual_selected_rows"))
def update_graphs(rows, derived_virtual_selected_rows):
    if derived_virtual_selected_rows is None:
        derived_virtual_selected_rows = []

    dff = load_data() if rows is None else pd.DataFrame(rows)

    colors = ['#7FDBFF' if i in derived_virtual_selected_rows else '#0074D9'
              for i in range(len(dff))]

    return [
        dcc.Graph(
            id=column,
            figure={
                "data": [
                    {
                        "x": dff["category"],
                        "y": dff[column],
                        "type": "bar",
                        "marker": {"color": colors},
                    }
                ],
                "layout": {
                    "xaxis": {"automargin": True},
                    "yaxis": {
                        "automargin": True,
                        "title": {"text": column}
                    },
                    "height": 250,
                    "margin": {"t": 10, "l": 10, "r": 10},
                },
            },
        )
        for column in ["pop", "lifeExp", "category"] if column in dff
    ]

# Callback to open URLs in a new tab
@callback(
    Output('hidden-div', 'children'),
    Input('datatable-interactivity', 'selected_rows'),
    State('datatable-interactivity', 'data')
)
def open_links(selected_rows, data):
    if selected_rows:
        df = pd.DataFrame(data)
        urls = df.loc[selected_rows, 'link'].tolist()
        for url in urls:
            webbrowser.open(url, new=2)  # Open URL in a new tab of the default browser
    return json.dumps({"status": "done"})  # Return some value to trigger the callback

if __name__ == '__main__':
    app.run_server(debug=True)
