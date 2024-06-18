import glob
import pandas as pd
import re
import logging
import utils

# Set up logging
logging.basicConfig(filename='ocr_process.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Create an empty list to store dictionaries
data = []

path = '.'
tickets = glob.glob(os.path.join(path, 'files/ejercicio_2/*.pdf'), recursive=True)

# Read every image
for pdf_file in tickets:
    logging.info(f"Performing OCR on images in: {pdf_file}")
    ocr_text = utils.read_ocr_text_from_pdf(pdf_file)
    # Append the results to the list as a dictionary
    data.append({'PDF File': pdf_file, 'OCR Text': ocr_text})

# Convert the list of dictionaries to a DataFrame
result_rows = []
for item in data:
    pdf_file = item['PDF File']
    ocr_text_lines = item['OCR Text'].split('\n')
    for line in ocr_text_lines:
        result_rows.append({'PDF File': pdf_file, 'OCR Text': line})

# Create a DataFrame from the result_rows list
df_result = pd.DataFrame(result_rows)

# Find indices where predecessor line ends with "Oviedo" and the following line begins with "TOTAL"
indices_list_1 = df_result[df_result['OCR Text'].str.endswith('Oviedo')].index
indices_list_2 = df_result[df_result['OCR Text'].str.startswith('TOTAL ')].index

# Create a range of indices between the given lists
selected_indices = [i for j in range(len(indices_list_1)) for i in range(indices_list_1[j] + 1, indices_list_2[j])]

# Extract the corresponding rows from the DataFrame
result_rows = df_result.iloc[selected_indices]

# Extract information from OCR Text and PDF File paths
result_rows['ticket_id'] = result_rows['PDF File'].str.extract(r'Ticket-(\d+_\d+_\d+)\.pdf')
result_rows['product_name'] = result_rows['OCR Text'].str.extract(r'(?i)([A-Z\s._]+)')
result_rows['price'] = result_rows['OCR Text'].str.extract(r'(\d+,\d+)')

# Select only the necessary columns
final_table = result_rows[['ticket_id', 'product_name', 'price']].dropna()

# Extract additional information from OCR Text
# Address
address_pattern = r'[a-zA-Z]+,\s\d+\s-\s[a-zA-Z\s]+'
address_mask = df_result['OCR Text'].str.contains(address_pattern, na=False)
address = df_result.loc[address_mask, ['PDF File', 'OCR Text']]
address['ticket_id'] = df_result['PDF File'].str.extract(r'Ticket-(\d+_\d+_\d+)\.pdf')
address = address[['ticket_id', 'OCR Text']]

# Time
time_pattern = r'HORA: (\d{2}:\d{2}:\d{2})'
df_result['ticket_hour'] = df_result['OCR Text'].str.extract(time_pattern)
hour = df_result.dropna(subset=['ticket_hour'])
hour['ticket_id'] = hour['PDF File'].str.extract(r'Ticket-(\d+_\d+_\d+)\.pdf')
hour = hour[['ticket_id', 'ticket_hour']]

# TOTAL
total = df_result.iloc[indices_list_2]
total['total'] = total['OCR Text'].str.extract(r'(\d+,\d+)')
total['ticket_id'] = total['PDF File'].str.extract(r'Ticket-(\d+_\d+_\d+)')
total = total[['ticket_id', 'total']]

# Discounts
discount_pattern = r'(\D+:\s)([0-9,.]+)\sEUR'
df_result['discount'] = df_result['OCR Text'].str.extract(discount_pattern)[1]
df_result['ticket_id'] = df_result['PDF File'].str.extract(r'Ticket-(\d+_\d+_\d+)')
discount = df_result.dropna(subset=['discount'])
discount = discount[['ticket_id', 'discount']]

# Vale Mensual
vale_mensual_pattern = r'Vale\s*Mensual[\s\-_]*:\s*([0-9,.]+)\s*EUR'
df_result['vale_mensual'] = df_result['OCR Text'].str.extract(vale_mensual_pattern)[0]
df_result['ticket_id'] = df_result['PDF File'].str.extract(r'Ticket-(\d+_\d+_\d+)')
result_df = df_result[['ticket_id', 'vale_mensual']]
vale = result_df.dropna(subset=['vale_mensual'])

# Merge DataFrames
merged_df = pd.merge(vale, discount, on='ticket_id', how='outer')
merged_df = pd.merge(merged_df, hour, on='ticket_id', how='outer')
merged_df = pd.merge(merged_df, address, on='ticket_id', how='outer')
merged_df = pd.merge(merged_df, total, on='ticket_id', how='outer')

# Save DataFrames to CSV with UTF-8 encoding
final_table.to_csv('files/results/product_information_new_ticket.csv', index=False, encoding='utf-8')
merged_df.to_csv('files/results/ticket_details.csv', index=False, encoding='utf-8')

# Display confirmation
logging.info("CSV files saved successfully.")
print("\nCSV files saved successfully.")
print(df_result)
