import datetime
import pandas as pd 

today = datetime.date.today()

last_day_prev_month = today.replace(day=1) - datetime.timedelta(days=1)
months = pd.date_range(start='2024-01', end=last_day_prev_month, freq='MS').strftime('%Y%m')

# haven't addressed filled files yet

sold_months = []
for m in months:
    filename = f'data/CRMLSSold{m}.csv'
    try:
        data = pd.read_csv(filename)
        sold_months.append(data)
    except FileNotFoundError:
        print(f"Skipped missing file: {filename}")


listing_months = []
for m in months:
    filename = f'data/CRMLSListing{m}.csv'
    try:
        data = pd.read_csv(filename)
        listing_months.append(data)
    except FileNotFoundError:
        print(f"Skipped missing file: {filename}")


sold_rows_before = sum(len(m) for m in sold_months)
sold = pd.concat(sold_months, ignore_index=True)
sold_rows_after = len(sold)
print(f"Sold rows before concat: {sold_rows_before}, after concat: {sold_rows_after}")

listing_rows_before = sum(len(m) for m in listing_months)
listing = pd.concat(listing_months, ignore_index=True)
listing_rows_after = len(listing)
print(f"Listing rows before concat: {listing_rows_before}, after concat: {listing_rows_after}")

sold_rows_before_filter = len(sold)
sold_residential = sold[sold['PropertyType'] == 'Residential']
sold_rows_after_filter = len(sold_residential)
print(f"Sold rows before filter: {sold_rows_before_filter}, after filter: {sold_rows_after_filter}")

listing_rows_before_filter = len(listing)
listing_residential = listing[listing['PropertyType'] == 'Residential']
listing_rows_after_filter = len(listing_residential)
print(f"Listing rows before filter: {listing_rows_before_filter}, after filter: {listing_rows_after_filter}")

sold_residential.to_csv('data/combined_sold_residential.csv', index=False)
listing_residential.to_csv('data/combined_listing_residential.csv', index=False)