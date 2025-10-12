import pandas as pd
import sankey as sk

df = pd.read_csv("data/most_used_beauty_cosmetics_products_extended.csv")

df.groupby("")

df = df[["Brand", "Category", "Rating", "Number_of_Reviews"]]
print(df.head())

sk.show_sankey(df, "Brand", "Category", "Rating", "Number_of_Reviews")