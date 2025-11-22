import panel as pn
import hvplot.pandas
from makeupapi import BeautyProductAPI

pn.extension()

api = BeautyProductAPI()
api.load_data('data/sephora_website_dataset.csv')

# WIDGET DECLARATIONS - Filtering
brand = pn.widgets.MultiChoice(
    name='Brands (select multiple)',
    options=api.get_options("brand")[1:],  # Remove 'All' option
    value=[],
    solid=False
)

category = pn.widgets.Select(
    name='Category',
    options=api.get_options("category")
)

# NEW: Minimum rating filter to find good products
min_rating = pn.widgets.FloatSlider(
    name='Minimum Rating',
    start=0,
    end=5,
    step=0.5,
    value=0,
    format='0.0'
)

# NEW: Price range filter
price_range = pn.widgets.RangeSlider(
    name='Price Range ($)',
    start=0,
    end=500,
    step=10,
    value=(0, 500)
)

# NEW: Minimum reviews filter (products with more reviews are more reliable)
min_reviews = pn.widgets.IntSlider(
    name='Minimum Reviews',
    start=0,
    end=1000,
    step=50,
    value=0
)

online_only = pn.widgets.Select(
    name='Online Only',
    options=["All", "Yes", "No"]
)

exclusive = pn.widgets.Select(
    name='Exclusive',
    options=["All", "Yes", "No"]
)

# NEW: Sort by dropdown
sort_by = pn.widgets.Select(
    name='Sort By',
    options=['Rating (High to Low)', 'Rating (Low to High)', 'Price (Low to High)', 'Price (High to Low)', 'Most Loved',
             'Most Reviewed'],
    value='Rating (High to Low)'
)

# Plotting widgets
width = pn.widgets.IntSlider(name="Width", start=250, end=2000, step=250, value=1500)
height = pn.widgets.IntSlider(name="Height", start=200, end=2500, step=100, value=800)


# CALLBACK FUNCTIONS

def get_catalog(brand, category, online_only, exclusive, min_rating, price_range, min_reviews, sort_by):
    """Display filtered and sorted product data table"""
    df = api.filter_data(brand, category, online_only, exclusive, min_rating, price_range, min_reviews)

    # Apply sorting
    if not df.empty:
        if sort_by == 'Rating (High to Low)':
            df = df.sort_values('rating', ascending=False)
        elif sort_by == 'Rating (Low to High)':
            df = df.sort_values('rating', ascending=True)
        elif sort_by == 'Price (Low to High)':
            df = df.sort_values('price', ascending=True)
        elif sort_by == 'Price (High to Low)':
            df = df.sort_values('price', ascending=False)
        elif sort_by == 'Most Loved':
            if 'love' in df.columns:
                df = df.sort_values('love', ascending=False)
        elif sort_by == 'Most Reviewed':
            if 'number_of_reviews' in df.columns:
                df = df.sort_values('number_of_reviews', ascending=False)

    # Select relevant columns for display
    display_cols = ['name', 'brand', 'category', 'price', 'rating', 'number_of_reviews', 'love']
    available_cols = [col for col in display_cols if col in df.columns]

    if df.empty:
        return pn.pane.Markdown("### No products match your filters. Try adjusting your criteria.")

    return pn.widgets.Tabulator(
        df[available_cols],
        selectable=False,
        page_size=25,
        sizing_mode='stretch_width',
        titles={'name': 'Product Name', 'brand': 'Brand', 'category': 'Category',
                'price': 'Price ($)', 'rating': 'Rating', 'number_of_reviews': '# Reviews', 'love': 'Loves'}
    )


def get_summary_stats(brand, category, online_only, exclusive, min_rating, price_range, min_reviews, sort_by):
    """Display summary statistics with product quality insights"""
    df = api.filter_data(brand, category, online_only, exclusive, min_rating, price_range, min_reviews)
    summary = api.get_summary(df)

    avg_price = summary["Average Price"]
    avg_price_str = f"${avg_price:.2f}" if avg_price is not None else "N/A"

    avg_rating = summary["Average Rating"]
    avg_rating_str = f"{avg_rating:.2f} ⭐" if avg_rating is not None else "N/A"

    # NEW: Highlight highly rated products
    highly_rated = summary.get("Highly Rated Products (4.5+)", 0)

    return pn.pane.Markdown(
        f"""
        ## 📊 Summary Statistics

        - **Total Products:** {summary['Total Products']}  
        - **Average Rating:** {avg_rating_str}
        - **Highly Rated Products (4.5+):** {highly_rated} 🌟
        - **Average Price:** {avg_price_str}  
        - **Exclusive Products:** {summary['Exclusive Products']}  
        - **Online Only Products:** {summary['Online Only Products']}

        💡 **Tip:** Use the rating and review filters to find the most trusted products!
        """,
        styles={'background-color': '#fff3f8', 'padding': '20px', 'border-radius': '10px',
                'border': '2px solid #ffd1dc'}
    )


def get_recommended_products(brand, category, online_only, exclusive, min_rating, price_range, min_reviews, sort_by):
    """Show top recommended products based on rating and reviews"""
    df = api.filter_data(brand, category, online_only, exclusive, min_rating, price_range, min_reviews)

    if df.empty:
        return pn.pane.Markdown("*No products available to recommend.*")

    # Filter for highly rated products with decent number of reviews
    recommended = df[
        (df['rating'] >= 4.0) &
        (df['number_of_reviews'] >= 50)
        ].sort_values(['rating', 'number_of_reviews'], ascending=[False, False]).head(10)

    if recommended.empty:
        return pn.pane.Markdown("*No highly-rated products with sufficient reviews found. Try adjusting your filters.*")

    display_cols = ['name', 'brand', 'price', 'rating', 'number_of_reviews', 'love']
    available_cols = [col for col in display_cols if col in recommended.columns]

    return pn.Column(
        pn.pane.Markdown("### 🌟 Top Recommended Products (4.0+ rating, 50+ reviews)"),
        pn.widgets.Tabulator(
            recommended[available_cols],
            selectable=False,
            page_size=10,
            sizing_mode='stretch_width',
            titles={'name': 'Product Name', 'brand': 'Brand', 'price': 'Price ($)',
                    'rating': 'Rating', 'number_of_reviews': '# Reviews', 'love': 'Loves'}
        )
    )


def get_scatter(brand, category, online_only, exclusive, min_rating, price_range, min_reviews, sort_by):
    """Generate scatter plot of Price vs Rating with size by number of reviews"""
    df = api.filter_data(brand, category, online_only, exclusive, min_rating, price_range, min_reviews)

    if df.empty or 'price' not in df or 'rating' not in df:
        return pn.pane.Markdown("*No data available for scatter plot.*")

    # Size bubbles by number of reviews (more reviews = bigger bubble = more reliable)
    return df.hvplot.scatter(
        x='price', y='rating',
        size='number_of_reviews',
        hover_cols=['name', 'brand', 'category', 'number_of_reviews'],
        title=f'Price vs Rating ({len(df)} products) - Bubble size = # of reviews',
        width=900, height=600,
        color='#ffd1dc',
        alpha=0.6
    )


def get_top_brands(brand, category, online_only, exclusive, min_rating, price_range, min_reviews, sort_by):
    """Bar plot of top 10 brands by average rating"""
    df = api.get_top_brands_by_rating(brand, category, online_only, exclusive, min_rating, price_range, min_reviews,
                                      top_n=10)

    if df.empty:
        return pn.pane.Markdown("*No data available for top brands.*")

    return df.hvplot.barh(
        x='brand', y='rating',
        title='Top 10 Brands by Average Rating',
        xlabel='Brand',
        ylabel='Average Rating',
        width=900, height=600,
        color='#ffd1dc'
    )


def get_price_by_category(brand, category, online_only, exclusive, min_rating, price_range, min_reviews, sort_by):
    """Bar chart of average price by category"""
    df = api.get_avg_price_by_category(brand, category, online_only, exclusive, min_rating, price_range, min_reviews)

    if df.empty:
        return pn.pane.Markdown("*No data available for price by category.*")

    return df.hvplot.bar(
        x='category', y='price',
        title='Average Price by Category',
        xlabel='Category',
        ylabel='Average Price ($)',
        width=900, height=600,
        rot=45,
        color='#ffd1dc'
    )


def get_rating_distribution(brand, category, online_only, exclusive, min_rating, price_range, min_reviews, sort_by):
    """Histogram of rating distribution"""
    df = api.filter_data(brand, category, online_only, exclusive, min_rating, price_range, min_reviews)

    if df.empty or 'rating' not in df:
        return pn.pane.Markdown("*No data available for rating distribution.*")

    return df.hvplot.hist(
        'rating',
        bins=20,
        title='Rating Distribution - Find concentration of highly-rated products',
        xlabel='Rating',
        ylabel='Number of Products',
        width=900, height=600,
        color='#ffd1dc'
    )


# CALLBACK BINDINGS
catalog = pn.bind(get_catalog, brand, category, online_only, exclusive, min_rating, price_range, min_reviews, sort_by)
summary = pn.bind(get_summary_stats, brand, category, online_only, exclusive, min_rating, price_range, min_reviews,
                  sort_by)
recommended = pn.bind(get_recommended_products, brand, category, online_only, exclusive, min_rating, price_range,
                      min_reviews, sort_by)
scatter = pn.bind(get_scatter, brand, category, online_only, exclusive, min_rating, price_range, min_reviews, sort_by)
top_brands = pn.bind(get_top_brands, brand, category, online_only, exclusive, min_rating, price_range, min_reviews,
                     sort_by)
price_category = pn.bind(get_price_by_category, brand, category, online_only, exclusive, min_rating, price_range,
                         min_reviews, sort_by)
rating_dist = pn.bind(get_rating_distribution, brand, category, online_only, exclusive, min_rating, price_range,
                      min_reviews, sort_by)

# DASHBOARD WIDGET CONTAINERS
card_width = 350

filter_card = pn.Card(
    pn.Column(
        pn.pane.Markdown("### 🔍 Product Filters"),
        brand,
        category,
        online_only,
        exclusive
    ),
    title="Basic Filters",
    width=card_width,
    collapsed=False
)

quality_filter_card = pn.Card(
    pn.Column(
        pn.pane.Markdown("### ⭐ Quality Filters"),
        pn.pane.Markdown("*Filter for highly-rated, well-reviewed products*"),
        min_rating,
        min_reviews,
        price_range
    ),
    title="Quality & Price Filters",
    width=card_width,
    collapsed=False
)

sort_card = pn.Card(
    pn.Column(
        sort_by
    ),
    title="Sorting",
    width=card_width,
    collapsed=True
)

plot_settings_card = pn.Card(
    pn.Column(width, height),
    title="Plot Settings",
    width=card_width,
    collapsed=True
)

# LAYOUT
layout = pn.template.FastListTemplate(
    title="🛍️ Sephora Product Finder - Discover the Best Beauty Products",
    sidebar=[filter_card, quality_filter_card, sort_card, plot_settings_card],
    theme_toggle=False,
    main=[
        summary,
        pn.Tabs(
            ("🌟 Recommended", recommended),
            ("📋 All Products", catalog),
            ("💰 Price vs Rating", scatter),
            ("🏆 Top Brands", top_brands),
            ("📊 Price by Category", price_category),
            ("⭐ Rating Distribution", rating_dist),
            active=0
        )
    ],
    header_background='#ffd1dc'
).servable()

if __name__ == "__main__":
    layout.show()