from dash import Dash, dash_table, dcc, html, Input, Output, callback
import pandas as pd
import dash_auth
from utils.supabase import supabase_auth

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

VALID_USERNAME_PASSWORD_PAIRS = {
    'admin': 'admin'
}

app = Dash(__name__, external_stylesheets=external_stylesheets)

auth = dash_auth.BasicAuth(
    app,
    VALID_USERNAME_PASSWORD_PAIRS
)

# Load your data
csv = './data.csv'
df = pd.read_csv(csv)

df = df[['linkname', 'linkdescription', 'category', 'link']]
df['id'] = df['linkname']
df.set_index('id', inplace=True, drop=False)

# Format the 'link' column to be Markdown clickable links
df['link'] = df['link'].apply(lambda x: f"[{x}]({x})")

app.layout = html.Div([
    dash_table.DataTable(
        id='datatable-interactivity',
        columns=[
            {
                "name": i, 
                "id": i, 
                "deletable": True, 
                "selectable": True,
                "presentation": "markdown" if i == "link" else "input"  # Handle links as markdown
            } for i in df.columns if i != 'id'  # Exclude 'id' column
        ],
        data=df.to_dict('records'),
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
            'maxWidth': '300px',  # Limit the max width of each cell
            'whiteSpace': 'normal',  # Enable wrapping
            'overflow': 'hidden',
            'textOverflow': 'ellipsis',  # Use ellipsis for overflow text
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
    html.Div(id='datatable-interactivity-container')
], style={'width': '100%', 'display': 'block', 'padding': '20px'})  # Ensuring full width and padding

@callback(
    Output('datatable-interactivity', 'style_data_conditional'),
    Input('datatable-interactivity', 'selected_columns')
)
def update_styles(selected_columns):
    return [{
        'if': {'column_id': i},
        'backgroundColor': '#D2F3FF'
    } for i in selected_columns]

@callback(
    Output('datatable-interactivity-container', "children"),
    Input('datatable-interactivity', "derived_virtual_data"),
    Input('datatable-interactivity', "derived_virtual_selected_rows"))
def update_graphs(rows, derived_virtual_selected_rows):
    
    if derived_virtual_selected_rows is None:
        derived_virtual_selected_rows = []

    dff = df if rows is None else pd.DataFrame(rows)

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

if __name__ == '__main__':
    app.run(debug=True)
