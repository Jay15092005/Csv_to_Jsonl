import pandas as pd
import json
import streamlit as st

# Function to clean and normalize data (e.g., convert dates, numbers)
def clean_data(value):
    if isinstance(value, str):
        try:
            parsed_date = pd.to_datetime(value, errors='raise')
            return parsed_date.isoformat()
        except (ValueError, TypeError):
            return value.strip() if isinstance(value, str) else value
    elif isinstance(value, (int, float)):
        return value
    elif isinstance(value, (list, dict)):
        return json.dumps(value)
    return value

# Function to clean the dataframe
def clean_dataframe(df):
    df = df.dropna(how='all', axis=1)  # Drop empty columns
    df = df.dropna(how='all', axis=0)  # Drop empty rows
    df.columns = df.columns.str.strip().str.replace(' ', '_').str.lower()  # Clean column names
    df = df.drop_duplicates()  # Drop duplicates
    for col in df.columns:
        df[col] = df[col].apply(clean_data)
    return df

# Function to convert each row into the required JSON structure
def row_to_json(row):
    messages = [{"role": "system", "content": "Product information entry."}]
    for col, value in row.items():
        if pd.notna(value):
            cleaned_value = clean_data(value)
            messages.append({"role": "assistant", "content": f"{col}: {cleaned_value}"})
    return {"messages": messages}

# Main function to handle CSV file conversion and download
def convert_csv_to_jsonl(file):
    df = pd.read_csv(file)
    df = clean_dataframe(df)
    json_data = [row_to_json(row) for _, row in df.iterrows()]
    
    # Save the output as a JSONL file
    output_file_path = 'output_file.jsonl'
    with open(output_file_path, 'w') as jsonl_file:
        for entry in json_data:
            jsonl_file.write(json.dumps(entry) + '\n')
    
    return output_file_path

# Streamlit web interface
st.title('CSV to JSONL Converter')

st.write('Upload your CSV file to convert it into JSONL format.')

# File uploader
uploaded_file = st.file_uploader("Choose a CSV file", type="csv")

if uploaded_file is not None:
    # Process the uploaded file
    output_file = convert_csv_to_jsonl(uploaded_file)
    
    # Provide download link
    with open(output_file, "rb") as file:
        st.download_button(
            label="Download JSONL file",
            data=file,
            file_name=output_file,
            mime="application/jsonl"
        )
