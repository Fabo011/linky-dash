# Migrate data to the appropriate format
import pandas as pd

input_file = 'data.csv'
output_file = 'reduced_data.csv'

df = pd.read_csv(input_file)

columns_to_keep = ['linkname', 'linkdescription', 'category', 'link']
reduced_df = df[columns_to_keep]

reduced_df.to_csv(output_file, index=False)

print(f"Reduced data saved to {output_file}")
