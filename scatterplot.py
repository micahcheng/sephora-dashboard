import pandas as pd
import panel as pn
import hvplot.pandas

pn.extension()

# Load data
data = pd.read_csv('data/most_used_beauty_cosmetics_products_extended.csv')

# Create filters
brand = pn.widgets.Select(name='Brand', options=['All'] + sorted(data['Brand'].unique().tolist()))
category = pn.widgets.Select(name='Category', options=['All'] + sorted(data['Category'].unique().tolist()))
skin_type = pn.widgets.Select(name='Skin Type', options=['All'] + sorted(data['Skin_Type'].unique().tolist()))
gender = pn.widgets.Select(name='Gender', options=['All'] + sorted(data['Gender_Target'].unique().tolist()))


# Create plot function
@pn.depends(brand, category, skin_type, gender)
def plot(brand, category, skin_type, gender):
    df = data.copy()
    if brand != 'All':
        df = df[df['Brand'] == brand]
    if category != 'All':
        df = df[df['Category'] == category]
    if skin_type != 'All':
        df = df[df['Skin_Type'] == skin_type]
    if gender != 'All':
        df = df[df['Gender_Target'] == gender]

    return df.hvplot.scatter(
        x='Price_USD',
        y='Rating',
        hover_cols=['Product_Name', 'Brand', 'Category'],
        title=f'Price vs Rating ({len(df)} products)',
        width=800,
        height=500
    )


# Layout
app = pn.Column(
    '# Beauty Products Dashboard',
    pn.Row(brand, category, skin_type, gender),
    plot
)

app.show()