import pandas as pd


class BeautyProductAPI:
    def __init__(self):
        self.df = None

    def load_data(self, path):
        """Load the Sephora dataset."""
        self.df = pd.read_csv(path)

        # Normalize column names for consistency
        self.df.columns = [c.strip() for c in self.df.columns]

        # Ensure required columns exist
        required_cols = ["brand", "category"]
        for col in required_cols:
            if col not in self.df.columns:
                raise ValueError(f"Missing required column: {col}")

        return self.df

    def get_options(self, column):
        """Get unique options for filters."""
        if column not in self.df.columns:
            return []
        options = sorted([x for x in self.df[column].dropna().unique() if pd.notna(x)])
        return ['All'] + options

    def filter_data(self, brand=None, category='All', online_only='All', exclusive='All',
                    min_rating=0, price_range=(0, 500), min_reviews=0):
        """Filter the dataset according to dashboard widget values."""
        df = self.df.copy()

        # Handle multiple brand selection
        if brand and len(brand) > 0:
            df = df[df["brand"].isin(brand)]

        if category and category != "All":
            df = df[df["category"] == category]

        if online_only and online_only != "All":
            filter_val = 1 if online_only == "Yes" else 0
            if "online_only" in df.columns:
                df = df[df["online_only"] == filter_val]

        if exclusive and exclusive != "All":
            filter_val = 1 if exclusive == "Yes" else 0
            if "exclusive" in df.columns:
                df = df[df["exclusive"] == filter_val]

        # NEW: Filter by minimum rating
        if "rating" in df.columns and min_rating > 0:
            df = df[df["rating"] >= min_rating]

        # NEW: Filter by price range
        if "price" in df.columns and price_range:
            df = df[(df["price"] >= price_range[0]) & (df["price"] <= price_range[1])]

        # NEW: Filter by minimum reviews
        if "number_of_reviews" in df.columns and min_reviews > 0:
            df = df[df["number_of_reviews"] >= min_reviews]

        return df

    def get_summary(self, df):
        """Return summary metrics used in visualizations."""
        highly_rated = 0
        if "rating" in df.columns and not df.empty:
            highly_rated = len(df[df["rating"] >= 4.5])

        summary = {
            "Total Products": len(df),
            "Average Price": df["price"].mean() if "price" in df and not df.empty else None,
            "Average Rating": df["rating"].mean() if "rating" in df and not df.empty else None,
            "Highly Rated Products (4.5+)": highly_rated,
            "Exclusive Products": int(df["exclusive"].sum()) if "exclusive" in df and not df.empty else 0,
            "Online Only Products": int(df["online_only"].sum()) if "online_only" in df and not df.empty else 0
        }
        return summary

    def get_top_brands_by_rating(self, brand=None, category='All', online_only='All', exclusive='All',
                                 min_rating=0, price_range=(0, 500), min_reviews=0, top_n=10):
        """Get top N brands by average rating."""
        df = self.filter_data(brand, category, online_only, exclusive, min_rating, price_range, min_reviews)

        if df.empty or 'rating' not in df:
            return pd.DataFrame()

        # Filter out brands with very few products (less than 3) for more reliable averages
        brand_counts = df.groupby('brand').size()
        valid_brands = brand_counts[brand_counts >= 3].index
        df = df[df['brand'].isin(valid_brands)]

        top_brands = df.groupby('brand')['rating'].mean().sort_values(ascending=False).head(top_n)
        return top_brands.reset_index()

    def get_avg_price_by_category(self, brand=None, category='All', online_only='All', exclusive='All',
                                  min_rating=0, price_range=(0, 500), min_reviews=0):
        """Get average price by category."""
        df = self.filter_data(brand, category, online_only, exclusive, min_rating, price_range, min_reviews)

        if df.empty or 'price' not in df:
            return pd.DataFrame()

        avg_price = df.groupby('category')['price'].mean().sort_values(ascending=False)
        return avg_price.reset_index()