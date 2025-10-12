import panel as pn
import sankey as sk
import pandas as pd


# Loads javascript dependencies and configures Panel (required)
pn.extension()


# Load the Data
df = pd.read_csv("data/most_used_beauty_cosmetics_products_extended.csv")


# WIDGET DECLARATIONS

# Search & filtering Widgets

# brand = pn.widgets.Select(name="Brand", options=df.get_phenotypes(), value='asthma')


# Plotting widgets
width = pn.widgets.IntSlider(name="Width", start=250, end=2000, step=250, value=1500)
height = pn.widgets.IntSlider(name="Height", start=200, end=2500, step=100, value=800)




# CALLBACK FUNCTIONS
'''def get_catalog(phenotype, min_pub, singular):
    global local
    local = api.extract_local_network(phenotype, min_pub, singular)
    table = pn.widgets.Tabulator(local, selectable=False)
    return table'''


def get_plot(df, *cols):
    global local
    fig = sk.make_sankey(df, "Brand", "Category", "Rating", "Number_of_Reviews", width=width, height=height)
    return fig


# CALLBACK BINDINGS (Connecting widgets to callback functions)
# catalog=pn.bind(get_catalog, phenotype, min_pub, singular)

plot = pn.bind(get_plot, width, height)
# DASHBOARD WIDGET CONTAINERS ("CARDS")

card_width = 320

search_card = pn.Card(
    pn.Column(
        # Widget 1

        # Widget 2

        # Widget 3

    ),
    title="Search", width=card_width, collapsed=False
)


plot_card = pn.Card(
    pn.Column(
        # Widget 1
        width,
        # Widget 2
        height
        # Widget 3
    ),

    title="Plot", width=card_width, collapsed=True
)


# LAYOUT

layout = pn.template.FastListTemplate(
    title="Makeup Dashboard",
    sidebar=[
        search_card,
        plot_card,
    ],
    theme_toggle=False,
    main=[
        pn.Tabs(
            ("Network", plot),  # Replace None with callback binding
            active=1  # Which tab is active by default?  (count starts at 0)
        )

    ],
    header_background='#a93226'

).servable()

layout.show()
