#-----------------------------------------------------------
# Data Cleaning and Preparation
#-----------------------------------------------------------

import pandas as pd

listing = pd.read_csv('data/combined_listing_residential_fred.csv')

# Convert date fields to datetime format 
listing['CloseDate'] = pd.to_datetime(listing['CloseDate'], errors='coerce')
listing['PurchaseContractDate'] = pd.to_datetime(listing['PurchaseContractDate'], errors='coerce')
listing['ListingContractDate'] = pd.to_datetime(listing['ListingContractDate'], errors='coerce')
listing['ContractStatusChangeDate'] = pd.to_datetime(listing['ContractStatusChangeDate'], errors='coerce')

# Remove invalid numeric values
listing = listing[listing['ClosePrice'] > 0]
listing = listing[listing['LivingArea'] > 0]
listing = listing[listing['DaysOnMarket'] >= 0]
listing = listing[listing['Bedrooms'] >= 0]
listing = listing[listing['Bathrooms'] >= 0]

## Data Consistency Checks

# Validate the logical order of date fields
listing['listing_after_close_flag'] = listing['ListingContractDate'] > listing['CloseDate']
listing['purchase_after_close_flag'] = listing['PurchaseContractDate'] > listing['CloseDate']
listing['negative_timeline_flag'] = listing['ListingContractDate'] > listing['PurchaseContractDate']

## Geographic Data Checks

# Flag records with missing coordinates (Latitude or Longitude is null)
listing['missing_coords_flag'] = listing['Latitude'].isnull() | listing['Longitude'].isnull()

# Flag Latitude = 0 or Longitude = 0 (sentinel null values)
listing['zero_coords_flag'] = (listing['Latitude'] == 0) | (listing['Longitude'] == 0)

# Flag Longitude > 0 errors (California coordinates should be negative)
listing['pos_coords_flag'] = listing['Longitude'] > 0

# Flag out-of-state or implausible coordinates
listing['implausible_coords_flag'] = (
    (listing['Latitude'] < 32.5) | (listing['Latitude'] > 42) |
    (listing['Longitude'] < -124.5) | (listing['Longitude'] > - 114)
)

print("Missing coordinates:", listing['missing_coords_flag'].sum())
print("Zero/sentinel coordinates:", listing['zero_coords_flag'].sum())
print("Positive longitude errors:", listing['pos_coords_flag'].sum())
print("Implausible/out-of-state coordinates:", listing['implausible_coords_flag'].sum())

listing.to_csv('data/combined_listing_residential_prepped.csv', index=False)