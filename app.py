#!/usr/bin/env python3
# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.

import argparse
import os
import os.path as path

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

import tanager.components as tc
import tanager.plots as tp
import tanager.utils as tu


def get_projects(path: str):
    projects = []
    if os.path.exists(path):
        directory_contents = os.listdir(path)
        for item in directory_contents:
            item_path = f'{path}/{item}'
            if os.path.isdir(item_path):
                projects.append(item)
    return projects


def prepare_dash_server(projects):
    external_stylesheets = [
        "https://use.fontawesome.com/releases/v5.15.3/css/all.css"
    ]

    app = dash.Dash('Tanager', meta_tags=[
        {'name': 'viewport',
         'content': 'width=device-width, initial-scale=1.0'
         }
    ], external_stylesheets=external_stylesheets)

    navbar = populate_nav_bar(projects)

    app.layout = html.Div(children=[
        dcc.Location(id='url', refresh=False),
        tc.navbar(id='experiment-nav', children=navbar),
        # content will be rendered in this element
        html.Div(id='page-content', children=tc.get_default_page(), className='w-full bg-gray-100 pl-20')
    ], className='min-h-screen flex flex-row')

    return app


def get_tanager_layouts():
    tanager_layouts = {}

    tanager_layouts['Project'] = html.Div(children=[
        html.Main(children=[
            tc.graph_panel(children=[
                tp.generation_distribution('Rastrigin')
            ]),
            tc.graph_panel(children=[
                tp.fitness_vs_generation('Rastrigin')
            ])
        ], className='grid grid-cols-2 gap-6 mt-20 mr-20'),
        html.Div(children=[
            tc.graph_panel(children=[
                tp.generate_nework_graph('Rastrigin')
            ])], className='gap-6')
    ], className='w-full bg-gray-100 pl-20')

    return tanager_layouts


def populate_nav_bar(projects):
    tanager_nav_children = []
    projects.sort()

    for project in projects:
        nav_bar_item = tc.navbar_item(project, href=f'/{project}')
        tanager_nav_children.append(nav_bar_item)

    return tanager_nav_children


# Global Area
# Create the parser
parser = argparse.ArgumentParser(
    prog='app',
    usage='%(prog)s [options] dir',
    description='Tanager - visualize Inspyred evolutionary computations.')

parser.add_argument('-debug', action="store_true", default=False, help="Run in debug mode.")
parser.add_argument('dir', type=str, help="Directory containing observer files.")
args = parser.parse_args()

if __name__ == '__main__':
    projects = get_projects(args.dir)
    app = prepare_dash_server(projects)


    @app.callback(Output('experiment-nav', 'children'),
                  Input('dir-refresh', 'n_clicks'),
                  Input('experiment-filter', 'value'))
    def refresh_onclick(n_clicks, value):
        if value is None:
            filtered_projects = get_projects(args.dir)
        else:
            filtered_projects = [p for p in get_projects(args.dir) if value in p]
        return populate_nav_bar(filtered_projects)


    @app.callback(Output('page-content', 'children'),
                  [Input('url', 'pathname')])
    def display_page(pathname="/"):
        project_name = pathname.strip('/')
        pathname = path.join(path.normpath(args.dir), project_name)
        if project_name:
            num_generations = tu.num_generations(pathname)
            slider_step = 1
            num_slider_marks = 20
            if num_generations > num_slider_marks:
                slider_step = tu.slider_round(num_generations / num_slider_marks)

            page_layout = html.Div(children=[
                html.H1(f'Project {project_name}', className='text-gray-400 font-bold text-5xl my-10'),
                html.Main(children=[
                    tc.graph_panel(children=[
                        tp.generation_distribution(pathname),
                        html.Div('Select Generation', className='self-start'),
                        dcc.Slider(
                            id='my-slider',
                            className="w-full",
                            min=0,
                            max=num_generations,
                            step=1,
                            value=0,
                            marks={i: f"{i}" for i in range(0, num_generations + 1, slider_step)}
                        )
                    ]),
                    tc.graph_panel(children=[
                        tp.fitness_vs_generation(pathname),
                    ])
                ], className='grid grid-cols-1 xl:grid-cols-2 gap-6 mr-20'),
                html.Div(children=[
                    # tc.graph_panel(children=[
                    #     tp.generate_nework_graph(project_name)
                    # ])
                ], className='gap-6')
            ], className='w-full bg-gray-100 pl-20')
        else:
            page_layout = tc.get_default_page()
        return page_layout


    app.run_server(debug=args.debug)
