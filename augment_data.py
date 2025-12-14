import pandas as pd
import numpy as np
from datetime import timedelta

# Set seed for reproducibility (optional)
np.random.seed(42)

input_file = 'zomato_orders.csv'
try:
    df = pd.read_csv(input_file).dropna(how='all')
    print(f"Loaded {len(df)} rows.")
except Exception as e:
    print(f"Error loading file: {e}")
    exit(1)

# Clean up column names just in case
df.columns = [c.strip() for c in df.columns]

# Ensure date is datetime
df['date'] = pd.to_datetime(df['date'])

target_total = 100
current_count = len(df)
needed = target_total - current_count

if needed > 0:
    print(f"Generating {needed} new datapoints...")
    
    new_rows = []
    
    cities = df['city'].unique()
    weather_types = df['weather'].unique()
    last_date = df['date'].max()
    
    # Pre-calculate stats for better noise generation
    # We want to preserve the correlation: Rain -> higher orders/value
    
    for _ in range(needed):
        city = np.random.choice(cities)
        weather = np.random.choice(weather_types)
        
        # Select a reference row to base our values on
        # Filter by city and weather if possible
        subset = df[(df['city'] == city) & (df['weather'] == weather)]
        if subset.empty:
            subset = df[df['city'] == city] 
        if subset.empty:
            subset = df
            
        reference = subset.sample(1).iloc[0]
        
        # Add noise: +/- 15% 
        noise_factor_orders = np.random.uniform(-0.15, 0.15)
        noise_factor_value = np.random.uniform(-0.15, 0.15)
        
        new_orders = int(reference['orders'] * (1 + noise_factor_orders))
        new_value = int(reference['avg_order_value'] * (1 + noise_factor_value))
        
        # Random date within the next 60 days
        days_ahead = np.random.randint(1, 60)
        new_date = last_date + timedelta(days=days_ahead)
        
        new_rows.append({
            'date': new_date,
            'city': city,
            'weather': weather,
            'orders': new_orders,
            'avg_order_value': new_value
        })
        
    new_df = pd.DataFrame(new_rows)
    combined = pd.concat([df, new_df], ignore_index=True)
    
    # Sort by date
    combined = combined.sort_values(by='date')
    
    # Save back
    combined.to_csv(input_file, index=False)
    print("Success! CSV updated.")
    
else:
    print("Already have enough data.")
