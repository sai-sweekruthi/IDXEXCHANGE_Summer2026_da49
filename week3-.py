#-----------------------------------------------------------
# Mortgage Rate Enrichment
#-----------------------------------------------------------

# Step 1 – Fetch the mortgage rate data from FRED
import pandas as pd

sold = pd.read_csv('data/combined_sold_residential_eda.csv')
listing = pd.read_csv('data/combined_listing_residential_eda.csv')

url = "https://fred.stlouisfed.org/graph/fredgraph.csv?id=MORTGAGE30US"
mortgage = pd.read_csv(url, parse_dates=['observation_date'])
mortgage.columns = ['date', 'rate_30yr_fixed']

# Step 2 – Resample weekly rates to monthly averages
mortgage['year_month'] = mortgage['date'].dt.to_period('M')
mortgage_monthly = (
    mortgage.groupby('year_month')['rate_30yr_fixed']
    .mean()
    .reset_index()
)

## Step 3 – Create a matching year_month key on the MLS datasets

# Sold dataset — key off CloseDate
sold['year_month'] = pd.to_datetime(sold['CloseDate']).dt.to_period('M')

# listing dataset — key off ListingContractDate
listing['year_month'] = pd.to_datetime(
    listing['ListingContractDate']
).dt.to_period('M')

# Step 4 – Merge
sold_with_rates = sold.merge(mortgage_monthly, on='year_month', how='left')
listing_with_rates = listing.merge(mortgage_monthly, on='year_month', how='left')

# Step 5 – Validate the merge
# Check for any unmatched rows (rate should not be null)
print(sold_with_rates['rate_30yr_fixed'].isnull().sum())
print(listing_with_rates['rate_30yr_fixed'].isnull().sum())

# Preview
print(
    sold_with_rates[
        ['CloseDate', 'year_month', 'ClosePrice', 'rate_30yr_fixed']
    ].head()
)

sold.to_csv('data/combined_sold_residential_fred.csv', index=False)
listing.to_csv('data/combined_listing_residential_fred.csv', index=False)