"""
File: sankey.py
Author: Bridget Crampton
Description: Build single-layer or multi-layer Sankey diagrams from a DataFrame.
"""

import plotly.graph_objects as go
import plotly.io as pio
import pandas as pd

pio.renderers.default = 'browser'

def _stack_columns(df, *cols, vals=None):
    """ Return stacked edges from adjacent cols; optionally attach weights in `vals`.
    df - Dataframe
    *cols - Ordered categorical columns
    vals - Values column (optional)
    """

    # Removes vals from cols if vals exists so that vals doesn't become a tier in the sankey diagram
    if vals is not None and vals in cols:
        # Asked chatgpt: "How do I filter *cols so it doesn’t include a certain value?"
        cols = tuple(c for c in cols if c != vals)

    # Create an empty list to hold the unique column pairs
    pairs = []

    # Set up pairs of adjacent columns from cols tuple/list
    for i in range(len(cols) - 1):
        src_col = cols[i]
        targ_col = cols[i + 1]

        # Make mini DataFrame with just these two columns
        pair = df[[src_col, targ_col]].copy()
        pair.columns = ["src", "targ"]

        # If vals exists, add a vals column to mini df
        if vals is not None and vals in df.columns:
            pair["vals"] = df[vals].values

        pairs.append(pair)

    # Stack the pairs dataframes together
    stacked = pd.concat(pairs, axis=0, ignore_index=True)
    return stacked

def _code_mapping(df, *cols, vals=None):
    """ Map labels in src and targ columns to integers
    df - Dataframe
    *cols - Ordered categorical columns
    vals - Values column (optional)
    """

    stacked = _stack_columns(df, *cols, vals=vals)

    # Create a list of unique node labels for the sankey diagram
    labels = pd.concat([stacked["src"], stacked["targ"]]).unique().tolist()

    # Get integer codes
    codes = range(len(labels))

    # Create label to code mapping
    lc_map = dict(zip(labels, codes))

    # Substitute names for codes in dataframe
    stacked["source"] = stacked["src"].map(lc_map)
    stacked["target"] = stacked["targ"].map(lc_map)
    # Drop original columns with labels
    stacked.drop(columns=["src", "targ"], inplace=True)

    # Asked Chatgpt: How do I rename a column in Pandas and then aggregate by groups?
    if "vals" in stacked.columns:
        # Rename and aggregate duplicate edges by summing weights
        stacked.rename(columns={"vals": "value"}, inplace=True)
        stacked = stacked.groupby(["source", "target"], as_index=False)["value"].sum()

    # Return the new df along with the list of labels that were converted
    return stacked, labels


def make_sankey(df, *cols, vals=None, **kwargs):
    """ Generate a sankey diagram
    df - Dataframe
    *cols - Ordered categorical columns
    vals - Values column (optional)
    kwargs - optional supported params: pad, thickness, line_color, line_width.
    """

    # Convert column labels to integer codes
    df, labels = _code_mapping(df, *cols, vals=vals)

    # Handle optional vals column
    if vals:
        values = df["value"]
    else:
        values = [1] * len(df)  # all values are identical (e.g., 1)

    # Extract customizations from kwargs
    pad = kwargs.get('pad', 50)
    thickness = kwargs.get('thickness', 50)
    line_color = kwargs.get('line_color', 'black')
    line_width = kwargs.get('line_width', 0)

    # Construct sankey figure
    link = {'source': df['source'], 'target': df['target'], 'value': values,
            'line': {'color': line_color, 'width': line_width}}

    node = {'label': labels, 'pad': pad, 'thickness': thickness,
            'line': {'color': line_color, 'width': line_width}}

    sk = go.Sankey(link=link, node=node)
    fig = go.Figure(sk)

    # Optionally adjusting the width and height of the sankey diagram
    width = kwargs.get('width', 1200)
    height = kwargs.get('height', 800)
    fig.update_layout(
        autosize=False,
        width=width,
        height=height
    )

    # Make sankey simply returns the figure
    # If you want to actually display the figure, use show sankey
    return fig


def show_sankey(df, *cols, vals=None, png=None, **kwargs):
    """
    Make AND Show the sankey diagram.   Optionally save it to a file
    df - The dataframe
    src - The source column
    targ - The target column
    vals - optional values column (line thickness)
    png - name of the .png image file to be generated
    kwargs - optional customizations like thickness, line color, etc.
    """

    fig = make_sankey(df, *cols, vals=vals, **kwargs)
    fig.show()
    if png:
        fig.write_image(png)