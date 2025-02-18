import pandas as pd
import numpy as np
import random
from pathlib import Path

# Define tenure type factors
tenure_type_factor = {
    "Freehold": 3620, "Freehold Reversion": 102, "Leasehold": 74, "Maintenance Obligation": 42,
    "Education Acts Agt": 31, "Informal Agreement": 26, "Mixed Title": 25, "Management Agreement": 24,
    "User Rights": 6, "Licence": 5, "Tenancy": 2, "Right Of Way": 1
}

# Define holding type factors
holding_type_factor = {
    "Land only": 2130, "Land and Building(s)": 213, "Building": 151, "Structure": 48,
    "Land": 10, "Building(s) only": 7
}

# Function to calculate EPC rating
def calculate_epc(property_type, building_size):
    if pd.isnull(building_size):
        return None
    epc_ratings = {"Offices": ["A", "B", "C", "D"], "Industrial/Workshop": ["A", "B", "C", "D"],
                   "Land-Industrial": ["N/A"], "Land only": ["N/A"]}
    return random.choice(epc_ratings.get(property_type, ["E", "F", "G"]))

# Function to assign council tax based on EPC rating
def assign_council_tax(epc_rating):
    tax_bands = {"A": 1000, "B": 1200, "C": 1400, "D": 1600, "E": 1800, "F": 2000, "G": 2200}
    return tax_bands.get(epc_rating)

# Function to generate key features for a property based on its type
def generate_key_features(property_type):
    features_dict = {
        "Offices": ["Modern Kitchen", "Private Parking", "Meeting Rooms"],
        "Industrial/Workshop": ["Storage Space", "Loading Dock", "Security System"],
        "Land-Industrial": ["Open Land", "Development Potential"],
        "Land only": ["Green Space", "Investment Opportunity"]
    }
    return ", ".join(random.sample(features_dict.get(property_type, []), min(2, len(features_dict.get(property_type, [])))))


# Function to generate property history based on effective date
def generate_property_history(effective_date):
    years = sorted({2021, 2016} | {random.randint(2010, 2025) for _ in range(random.randint(3, 6))})
    return ", ".join(map(str, years))

# Function to assign base price based on building size
def assign_price(building_size):
    return round(building_size * random.uniform(10, 50), 2) if pd.notnull(building_size) else None

# Function to calculate new price considering effective date, property type, and price adjustment
def calculate_new_price(effective_date, tenure_type, holding_type, base_price):
    if pd.isnull(effective_date) or pd.isnull(base_price):
        return None
    try:
        # Apply 2% price adjustment per year based on effective date
        year_factor = (2025 - int(effective_date)) * 0.02
        tenure_factor_value = tenure_type_factor.get(tenure_type, 1)
        holding_factor_value = holding_type_factor.get(holding_type, 1)
        
        # Calculate the new price with all factors
        return round(base_price * (1 + year_factor) * tenure_factor_value * holding_factor_value, 2)
    except ValueError:
        return None

# Load and merge datasets
# datasets = ["dataset/dataset_2021.csv", "dataset/dataset_2016.csv", "dataset/dataset_2023.csv"]
datasets = [str(Path("dataset") / f"dataset_{year}.csv") for year in [2021, 2016, 2023]]
merged_df = pd.concat([pd.read_csv(file) for file in datasets]).drop_duplicates(subset=["Property ID"]).reset_index(drop=True)

# Apply transformations and add new columns to the merged dataset
merged_df["EPC Rating"] = merged_df.apply(lambda x: calculate_epc(x["Property Type"], x["Building Size - GIA (M2)"]), axis=1)
merged_df["Council Tax"] = merged_df["EPC Rating"].apply(assign_council_tax)
merged_df["Key Features"] = merged_df["Property Type"].apply(generate_key_features)
merged_df["Property Rent/Sale History"] = merged_df["Effective Date"].apply(generate_property_history)
merged_df["Base Price"] = merged_df["Building Size - GIA (M2)"].apply(assign_price)
merged_df["New Price"] = merged_df.apply(lambda x: calculate_new_price(x["Effective Date"], x["Tenure Type"], x["Holding Type"], x["Base Price"]), axis=1)

# Save merged dataset
merged_df.to_csv("merged_dataset.csv", index=False)
print("Merged dataset saved as merged_dataset.csv")
