import pandas as pd

def describe_product(row):
    return f"""
    ### {row['name']}
    **Brand:** {row['brand']}  
    **Category:** {row['category']}  
    **Price:** ${row['price_usd']}  
    **Online Only:** {row['online_only']}  
    **Exclusive:** {row['exclusive']}  

    **Description:**  
    {row['description']}

    **Ingredients:**  
    {row['ingredients']}
    """

def generate_markdown(df):
    md = "# Product Overview\n\n"
    for _, row in df.iterrows():
        md += describe_product(row)
        md += "\n---\n"
    return md
