import glob as glob
import os.path as path
import sys

import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly.figure_factory as ff
import plotly.graph_objects as go


def fitness_vs_generation(basedir, project_name):
    stats_path = path.join(path.normpath(basedir), project_name, 'tanager-statistics-file-*.csv')
    data_files = glob.glob(stats_path, recursive=False)
    try:
        if len(data_files) >= 1:
            if len(data_files) > 1:
                print(f"More than one statistics file found in {path.dirname(stats_path)}.", file=sys.stderr)
                print("Only one file will be used.", file=sys.stderr)
            file = data_files[0]
            print(f"Reading in {file}")
            df = pd.read_csv(file)
            x = df['num_generations']
            y = df['average_fit']
            y_upper = y + df['std_fit']
            y_lower = y - df['std_fit']
            fig = go.Figure([
                go.Scatter(
                    name='Fitness',
                    x=x, y=y,
                    mode='lines',
                    line=dict(color='rgb(31, 119, 180)'),
                ),
                go.Scatter(
                    name='Upper Bound',
                    x=x, y=y_upper,
                    mode='lines',
                    marker=dict(color="#444"),
                    line=dict(width=0),
                    showlegend=False
                ),
                go.Scatter(
                    name='Lower Bound',
                    x=x, y=y_lower,
                    marker=dict(color="#444"),
                    line=dict(width=0),
                    mode='lines',
                    fillcolor='rgba(68, 68, 68, 0.3)',
                    fill='tonexty',
                    showlegend=False
                )
            ])
            fig.update_layout(
                yaxis_title='Fitness',
                title='Average Fitness vs Generation',
                hovermode="x"
            )
            return dcc.Graph(id='fitness_vs_generation', figure=fig, responsive=True, className="h-full w-full")
        else:
            print(f"No stats files found in {path.dirname(stats_path)}", file=sys.stderr)
    except IOError as e:
        return html.H3(f"ERROR: Caught an IOError while reading {file}:\n{e}")
    except ValueError as e:
        return html.H3(f"ERROR: Caught a ValueError while reading {file}:\n{e}")
    return html.H3(f'Error reading stats file.')


def generation_distribution(project_name):
    # print(request.host_url)
    print(project_name)
    df = pd.read_csv('data/experiment_1/sample_10i_10g.tsv', sep='\t')
    fig = ff.create_distplot([df.iloc[9, 1:-2]], ['distplot'], show_rug=False, show_hist=False, curve_type="normal")
    return dcc.Graph(id='generation_distribution', figure=fig, responsive=True, className="h-full w-full")
