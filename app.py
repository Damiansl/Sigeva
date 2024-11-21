# Import packages
from dash import Dash, html, dash_table, dcc, callback, Output, Input
import pandas as pd
import plotly.express as px
from datetime import date
import plotly.graph_objects as go
from dash.dash_table import DataTable

df = pd.read_excel('./assets/SIGEVA_REPORTE_COMPLETO.xlsx')

df['categoria'] = df['categoria'].astype(str)
df['descripcion'] = df['descripcion'].astype(str)
df['anio_publicacion'] = pd.to_numeric(df['anio_publicacion'], errors='coerce')  # Convertir a numérico
df['revista'] = df['revista'].fillna('Sin datos')
df['revista'] = df['revista'].astype(str)

#conteo de categorias
categoria_counts = df.groupby(['apellido','categoria']).size().reset_index(name='Cantidad')
categoria_counts_anio = df.groupby(['apellido','categoria','anio_publicacion']).size().reset_index(name='Cantidad')
#Valores de los dropdowns
optionsApellido = [{'label': apellido, 'value': apellido} for apellido in df['apellido'].unique() if isinstance(apellido, str)]
optionsAnio = [{'label': anio, 'value': anio} for anio in df['anio_publicacion'].astype(str).str[:4].unique() if anio.isdigit()]  # Filtrar solo valores que sean dígitos
categories = [{'label': categoria, 'value': categoria} for categoria in df['categoria'].unique() if isinstance(categoria, str)]
categoria_counts['Cantidad'] = pd.to_numeric(categoria_counts['Cantidad'], errors='coerce').fillna(0).astype(int)


#Categorias a mostrar de inicio
default_categories = [
    {'Label': 'Artículo de Revista', 'value': 'Artículo de Revista'},
    {'Label': 'Capítulo de Libro', 'value': 'Capítulo de Libro'},
    {'Label': 'Libros', 'value': 'Libros'},
    {'Label': 'Proyectos de Investigación', 'value': 'Proyectos de Investigación'},
    {'Label': 'Eventos Científicos', 'value': 'Eventos Científicos'},
    {'Label': 'Participación en Eventos Científicos', 'value': 'Participación en Eventos Científicos'}
]

categoria_counts_per_year = df.groupby('anio_publicacion').size().reset_index(name='cantidadAnio')

fig_bar = px.bar(categoria_counts_per_year,x="anio_publicacion", y="cantidadAnio",title="Categorias por año")
fig_bar.update_layout(
    width=450,
    height=400,
    showlegend=False,
    xaxis=dict(range=[1985, 2026]),  # Establecer el rango de años de 2019 a 2023
    yaxis=dict(range=[0, 2000]),         # Establecer el rango de cantidades de 0 a 15
    plot_bgcolor="white",
    autosize=False,
)
fig_bar.update_traces(marker_color="#45a4d2")
# Crea una figura con Plotly Express
fig = go.Figure()

fig.update_layout(
    autosize=False,
    minreducedwidth=250,
    minreducedheight=250,
    width=500,
    height=450,
    paper_bgcolor="lightgray"
)
app = Dash()

app.layout = [
    #div general
    html.Div(className='bodydiv',children=[
        #Header
        html.Div(className='header',
            children=[
                 html.Img(src='/assets/logo-unnoba.png', style={'height': '40px'})
            ]
        ),
        #Sidebar
        html.Div(
            className='sidebar',
            children=[
                html.H2("Menú"),
                html.Div(className='sidebar-link', children=[html.Img(src='/assets/home.svg', style={'height': '30px'}), dcc.Link("Inicio", href='/', className='sidebar-link')]),
                html.Div(className='sidebar-link', children=[html.Img(src='/assets/search.svg', style={'height': '30px'}), dcc.Link("Buscar", href='/', className='sidebar-link')]),
                html.Div(className='sidebar-link', children=[html.Img(src='/assets/settings.svg', style={'height': '30px'}), dcc.Link("Ajustes", href='/', className='sidebar-link')]),
            ]
        ),
        html.Div( className='content',children=[
            #div dropdown por año
            html.Div([ 
                html.Div([
                html.Label("Año"),
                dcc.Dropdown(
                    id="anio-dropdown",
                    options=optionsAnio,
                    value=None, 
                    className="dropdown")
                ]), 
                #div dropdown apellidos
                html.Div([
                html.Label("Apellido"),
                dcc.Dropdown(
                id='apellido-dropdown',
                options=optionsApellido,
                value=None,  # Valor predeterminado
                className="dropdown"
                )]),
                html.Div([
                html.Label("Categoria"),
                dcc.Dropdown(id='categoria-select-dropdown',
                    options=[cat['value'] for cat in default_categories],
                    multi=True,
                    value=None,
                    className="dropdown")
                ]),
                #div dropdown categorias predeterminadas
                html.Div([
                dcc.Dropdown(id='categoria-dropdown',
                    options=categories,
                    multi=True,  # Permitir selección múltiple
                    value=[cat['value'] for cat in default_categories], className="dropdown categorias")])
            ],className="divi"),
            #div que contiene el grafico de torta
            html.Div([
            html.Div(dcc.Graph(id='categoria-graph'),className="graph-container"),
            html.Div(dcc.Graph(id='bar-graph',
                            figure=fig_bar,
                            className='graph',
                            config={'displayModeBar': False},
                            style={"width": "100%", "height": "100%"}),
                            className="graph-container")
            ],className="graph-row"),
            #Div que contiene la tabla
            html.Div([
                DataTable(
                    id='categoriaTable',
                    style_data={
                        'whiteSpace': 'normal',
                        'height': 'auto',
                        'textAlign': 'left',
                    },
                    columns=[
                        {'name': 'Categoría', 'id': 'categoria'},
                        {'name': 'Descripción', 'id': 'descripcion'},
                        {'name': 'Año de Publicación', 'id': 'anio_publicacion'},
                        {'name': 'Revista', 'id': 'revista'}
                    ],
                    page_size=10,
                    style_table={'overflowX': 'auto'},
                    style_cell={'textAlign': 'left'} 
                )
            ], id='table-container')
        ])
    ])
    
]

#llamadas
@app.callback(
    Output('categoriaTable', 'data'),
    Input('apellido-dropdown', 'value'),
    Input('categoria-dropdown', 'value'),
    Input('anio-dropdown', 'value')
)
def update_table(selected_apellido, selected_categories, selected_anio):
    filtered_df = df.copy()
    if selected_apellido:
        filtered_df = filtered_df[filtered_df['apellido'] == selected_apellido]
    
    if selected_anio:
        filtered_df = filtered_df[filtered_df['anio_publicacion'].astype(str).str[:4] == str(selected_anio)]
    
    if selected_categories:
        filtered_df = filtered_df[filtered_df['categoria'].isin(selected_categories)]

    # Asegurarte de que los valores sean 'Sin datos' si son NaN
    filtered_df = filtered_df.fillna('Sin datos')

    # Convertir los datos en un formato que Dash pueda usar (lista de diccionarios)
    categoriaTable_data = filtered_df[['categoria', 'descripcion', 'anio_publicacion', 'revista']].to_dict('records')

    # Asegurarte de devolver los datos en el formato correcto:
    return categoriaTable_data    # Los datos deben ir dentro de un diccionario con la clave 'data'


@app.callback(
    Output('categoria-graph', 'figure'),
    Input('apellido-dropdown', 'value'),
    Input('categoria-dropdown', 'value'),
    Input('anio-dropdown', 'value')
)   

#actualizar y crear el grafico con la cantidad de categorias y los filtros seleccionados
def update_graph(selected_apellido, selected_categories,selected_anio):
    if not isinstance(selected_categories, list) or len(selected_categories) == 0:
        return go.Figure()  # Retornar figura vacía si no se seleccionan categorías
    # Filtrar los datos

    #datos de todos(se muestra al entrar en la página)
    filtered_df = categoria_counts[categoria_counts['categoria'].isin(selected_categories)]

    title = 'Cantidad de publicaciones por categoría'
    if selected_anio:
        filtered_df = categoria_counts_anio[categoria_counts_anio['categoria'].isin(selected_categories)]
        filtered_df = filtered_df[filtered_df['anio_publicacion'].astype(str).str[:4] == str(selected_anio)]


    if selected_apellido:
        # Filtrar solo por apellido
        filtered_df = filtered_df[filtered_df['apellido'] == selected_apellido]
        selected_nombre = df[df['apellido'] == selected_apellido]
        if not selected_nombre.empty:
            selected_nombre = selected_nombre['nombre'].values[0]
            title += f' para {selected_nombre} {selected_apellido}'
        else:
            title += ' (Apellido no encontrado)'
    if selected_anio and selected_apellido:
        filtered_df = filtered_df[(filtered_df['anio_publicacion'].astype(str).str[:4] == str(selected_anio)) & (filtered_df['apellido'] == selected_apellido)]

    #crea el grafico
    fig = px.pie(filtered_df, names='categoria', values='Cantidad', title=title)    
    fig.update_layout(
    autosize=False,
    minreducedwidth=250,
    minreducedheight=250,
    width=500,
    height=320
    )
    return fig

# Callback para actualizar el gráfico de barras
@app.callback(
    Output('bar-graph', 'figure'),
    Input('anio-dropdown', 'value'),
    Input('apellido-dropdown', 'value'),
    Input('categoria-select-dropdown', 'value')
)
def update_bar_graph(selected_anio, selected_apellido,selected_categories):
    # Filtrar los datos según el año y apellido seleccionados
    filtered_df = df.copy()
    
    # Aplicar filtro por año
    if selected_anio:
        filtered_df = filtered_df[filtered_df['anio_publicacion'].astype(str).str[:4] == str(selected_anio)]
    
    # Aplicar filtro por apellido
    if selected_apellido:
        filtered_df = filtered_df[filtered_df['apellido'] == selected_apellido]
    
    if selected_anio and selected_apellido:
        filtered_df = filtered_df[(filtered_df['anio_publicacion'].astype(str).str[:4] == str(selected_anio)) & (filtered_df['apellido'] == selected_apellido)]
    
    # Filtrar solo las categorías predeterminadas (default_categories)
    default_category_values = [cat['value'] for cat in default_categories]
    filtered_df = filtered_df[filtered_df['categoria'].isin(default_category_values)]
    # Agrupar los datos por año de publicación y contar para todas las categorías
    categoria_counts_per_year = filtered_df.groupby('anio_publicacion').size().reset_index(name='cantidad')

    # Crear la figura del gráfico de barras
    fig_bar = go.Figure()

    max_value = categoria_counts_per_year['cantidad'].max()
    # Trazar el total de publicaciones por año para todas las categorías
    fig_bar.add_trace(
        go.Bar(
            x=categoria_counts_per_year['anio_publicacion'],
            y=categoria_counts_per_year['cantidad'],
            name="Total de publicaciones",
            marker_color="#45a4d2",
        )
    )


    # Filtrar y agrupar los datos para las categorías seleccionadas, si se eligen

    if selected_categories:
        selected_categoria_counts = filtered_df[filtered_df['categoria'].isin(selected_categories)]
        selected_categoria_counts_per_year = selected_categoria_counts.groupby('anio_publicacion').size().reset_index(name='cantidad')

        # Añadir traza específica para las categorías seleccionadas
        fig_bar.add_trace(
            go.Bar(
                x=selected_categoria_counts_per_year['anio_publicacion'],
                y=selected_categoria_counts_per_year['cantidad'],
                name="Publicaciones(Categorías seleccionadas)",
                marker_color="orange",
                opacity=1.0
            )
        )
    # Crear el gráfico de barras
    fig_bar.update_layout(
        title="Cantidad de publicaciones por año para todas las categorías",
        width=500,
        height=320,
        barmode='overlay',
        showlegend=True,
        xaxis=dict(range=[1985, 2026]),
        yaxis=dict(range=[0, max_value]),
        plot_bgcolor="white",
        autosize=False,
    )
    return fig_bar
    

# Run the app
if __name__ == '__main__':
    app.run(debug=True)