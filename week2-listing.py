#-----------------------------------------------------------
# Week 1 - Monthly Dataset Aggregation
#-----------------------------------------------------------

import os
import datetime
import pandas as pd 

today = datetime.date.today()

last_day_prev_month = today.replace(day=1) - datetime.timedelta(days=1)
months = pd.date_range(start='2024-01', end=last_day_prev_month, freq='MS').strftime('%Y%m')

# checks for filled data files, removes last 2 columns, then saves as name without "_filled"
for prefix in ['CRMLSSold', 'CRMLSListing']:
    for m in months:
        filled_filename = f'data/{prefix}{m}_filled.csv'
        normal_filename = f'data/{prefix}{m}.csv'
        if os.path.exists(filled_filename):
            df = pd.read_csv(filled_filename)
            df = df.iloc[:, :-2]
            df.to_csv(normal_filename, index=False)
            print(f"Fixed {filled_filename} -> {normal_filename}")

listing_months = []
for m in months:
    filename = f'data/CRMLSListing{m}.csv'
    try:
        data = pd.read_csv(filename)
        listing_months.append(data)
    except FileNotFoundError:
        print(f"Skipped missing file: {filename}")


listing_rows_before = sum(len(m) for m in listing_months)
listing = pd.concat(listing_months, ignore_index=True)
listing_rows_after = len(listing)
print(f"Listing rows before concat: {listing_rows_before}, after concat: {listing_rows_after}")


listing_rows_before_filter = len(listing)
listing_residential = listing[listing['PropertyType'] == 'Residential']
listing_rows_after_filter = len(listing_residential)
print(f"Listing rows before filter: {listing_rows_before_filter}, after filter: {listing_rows_after_filter}")

listing_residential.to_csv('data/combined_listing_residential.csv', index=False)

#-----------------------------------------------------------
# Week 2 - Dataset Structuring and Validation
#-----------------------------------------------------------

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

listing = pd.read_csv("data/combined_listing_residential.csv")

# number of rows and columns
print("Shape:", listing.shape)
# column names
print("Columns:", listing.columns.tolist())
# preview first rows
print(listing.head())
# column data types
print(listing.dtypes)

# drop duplicate columns with ".1"
listing = listing.loc[:, ~listing.columns.str.endswith('.1')]

metadata_cols = [
    'ListingKey', 'ListingKeyNumeric', 'ListingId', 'ListAgentFirstName',
    'ListAgentLastName', 'ListAgentFullName', 'ListAgentEmail', 'BuyerAgentFirstName',
    'BuyerAgentLastName', 'BuyerAgentMlsId', 'CoListAgentFirstName', 'CoListAgentLastName',
    'ListOfficeName', 'BuyerOfficeName', 'CoListOfficeName', 'BuyerOfficeAOR',
    'BuyerAgencyCompensation', 'BuyerAgencyCompensationType'
]

# filter to residential properties only
print("Unique property types:", listing['PropertyType'].unique())
listing = listing[listing.PropertyType == 'Residential']
print("Filtered shape:", listing.shape)

## missing value analysis

# identify high missing columns
missing_count = listing.isnull().sum()
missing_pct = (listing.isnull().mean() * 100).round(2)

missing_report = pd.DataFrame({
    'MissingCount': missing_count,
    'MissingPct': missing_pct
}).sort_values('MissingPct', ascending=False)

print("\nMissing Value Report:")
print(missing_report)

# check columns with >90% missing
missing_report['Flag90'] = missing_report['MissingPct'] > 90
print("\nMissing Value Report:")
print(missing_report)
high_missing_cols = missing_report[missing_report['MissingPct'] > 90].index.tolist()
drop_cols = metadata_cols + high_missing_cols
listing = listing.drop(columns=[c for c in drop_cols if c in listing.columns]) # dropped the unnecessary columns

## numeric distribution review

numeric_fields = [
    'ClosePrice', 'ListPrice', 'OriginalListPrice', 'LivingArea',
    'LotSizeAcres', 'BedroomsTotal', 'BathroomsTotalInteger',
    'DaysOnMarket', 'YearBuilt'
]

# percentile summaries
percentiles = listing[numeric_fields].describe(percentiles=[0.01, 0.05, 0.25, 0.5, 0.75, 0.95, 0.99])
print(percentiles)

percentile_cutoffs = {
    'ClosePrice': 0.99, 'ListPrice': 0.99, 'OriginalListPrice': 0.99,
    'LivingArea': 0.995, 'LotSizeAcres': 0.98, 'BedroomsTotal': 1.00,
    'BathroomsTotalInteger': 1.00, 'DaysOnMarket': 0.99, 'YearBuilt': 1.00
}

# print histograms with outliers
for col in percentile_cutoffs.keys():
    fig, axes = plt.subplots(1, 2, figsize=(14, 4))
    sns.histplot(listing[col], kde=True, ax=axes[0])
    axes[0].set_title(f"{col} Distribution (With Outliers)")
    sns.boxplot(x=listing[col], ax=axes[1])
    axes[1].set_title(f"{col} Boxplot (With Outliers)")
    plt.tight_layout()
    plt.show()

# identify extreme outliers
outlier_indices = {}

for col, cutoff in percentile_cutoffs.items():
    threshold = listing[col].quantile(cutoff)
    outliers = listing[listing[col] > threshold]
    outlier_indices[col] = outliers.index.tolist()

    print(f"\n{col} — cutoff at {cutoff} percentile = {threshold:.2f}")
    print(f"Extreme outliers found: {len(outliers)}")

# helper function to print histograms without outliers
def remove_outliers(series, cutoff):
    threshold = series.quantile(cutoff)
    return series[series <= threshold]

# histograms without outliers
for col, cutoff in percentile_cutoffs.items():
    trimmed = remove_outliers(listing[col], cutoff)
    fig, axes = plt.subplots(1, 2, figsize=(14, 4))
    sns.histplot(trimmed, kde=True, ax=axes[0])
    axes[0].set_title(f"{col} Distribution (Outliers Removed at {cutoff} percentile)")
    sns.boxplot(x=trimmed, ax=axes[1])
    axes[1].set_title(f"{col} Boxplot (Outliers Removed at {cutoff} percentile)")
    plt.tight_layout()
    plt.show()

listing.to_csv('data/combined_listing_residential_eda.csv', index=False)