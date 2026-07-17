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
# Flag Latitude = 0 or Longitude = 0 (sentinel null values)
# Flag Longitude > 0 errors (California coordinates should be negative)
# Flag out-of-state or implausible coordinates