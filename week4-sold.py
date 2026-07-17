#-----------------------------------------------------------
# Data Cleaning and Preparation
#-----------------------------------------------------------

import pandas as pd

sold = pd.read_csv('data/combined_sold_residential_fred.csv')

# Convert date fields to datetime format 
sold['CloseDate'] = pd.to_datetime(sold['CloseDate'], errors='coerce')
sold['PurchaseContractDate'] = pd.to_datetime(sold['PurchaseContractDate'], errors='coerce')
sold['ListingContractDate'] = pd.to_datetime(sold['ListingContractDate'], errors='coerce')
sold['ContractStatusChangeDate'] = pd.to_datetime(sold['ContractStatusChangeDate'], errors='coerce')

# Remove invalid numeric values
sold = sold[sold['ClosePrice'] > 0]
sold = sold[sold['LivingArea'] > 0]
sold = sold[sold['DaysOnMarket'] >= 0]
sold = sold[sold['Bedrooms'] >= 0]
sold = sold[sold['Bathrooms'] >= 0]

## Data Consistency Checks

# Validate the logical order of date fields
sold['listing_after_close_flag'] = sold['ListingContractDate'] > sold['CloseDate']
sold['purchase_after_close_flag'] = sold['PurchaseContractDate'] > sold['CloseDate']
sold['negative_timeline_flag'] = sold['ListingContractDate'] > sold['PurchaseContractDate']

## Geographic Data Checks
# Flag records with missing coordinates (Latitude or Longitude is null)
# Flag Latitude = 0 or Longitude = 0 (sentinel null values)
# Flag Longitude > 0 errors (California coordinates should be negative)
# Flag out-of-state or implausible coordinates