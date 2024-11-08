import requests
import pandas as pd
import httpx
import json
from datetime import datetime
import csv
import os
from dotenv import load_dotenv

def get_token(secrete: str) -> str:
    """Get access token from iLumen API."""
    try:
        client = httpx.Client(timeout=30.0)  # Added timeout for reliability
        response_API = client.get(f'https://app.ilumen.biz/WebApi/RequestAccessToken/?clientsecret={secrete}')
        response_API.raise_for_status()  # Will raise an exception for 4XX/5XX status codes
        return response_API.text
    except httpx.HTTPError as e:
        print(f"HTTP error occurred while getting token: {e}")
        raise
    finally:
        client.close()

def generate_report():
    """Generate progress report from iLumen data."""
    print("Starting report generation...")
    
    # Load environment variables from .env file
    load_dotenv()
    
    # Set up directories - using GitHub Actions workspace
    reports_dir = 'csv_reports'
    os.makedirs(reports_dir, exist_ok=True)

    # Get secrets from .env file
    secrets = {
        'ORG_GFM': os.getenv('ORG_GFM_SECRET')
    }

    # Validate that required environment variables are present
    if not secrets['ORG_GFM']:
        raise ValueError("Missing required environment variable: ORG_GFM_SECRET")

    now = datetime.now()
    now_str = now.strftime("%Y%m%d_%H%M")
    
    # Define column configurations
    columns_to_keep = [
        "OrgTotalPeriodsQty", "OrgQuarterlyPeriodQty", "OrgMonthlyPeriodQty", 
        "Org13PeriodQty", "OrgName", "OrgCompanyID", "Currency", "Department", 
        "OrgDataStatus", "AgreementSigned", "OrgCountry", "BU", "PeerCurrentPeriodDisplay"
    ]
    
    new_order = [
        "Key", "Department", "OrgName", "OrgCompanyID", "Currency", "AgreementSigned",
        "OrgCountry", "BU", "OrgDataStatus", "Has Data", "OrgTotalPeriodsQty",
        "OrgQuarterlyPeriodQty", "OrgMonthlyPeriodQty", "Org13PeriodQty",
        "PeerCurrentPeriodDisplay"
    ]

    all_data = []

    for key, value in secrets.items():
        print(f"Processing organization: {key}")
        try:
            org_name = key.replace("_", " ")
            token = get_token(value)
            
            # Get demographic data
            api_url = f'https://app.ilumen.biz/WebApi/GetDemographicData?accesstoken={token}'
            response = requests.get(api_url, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            # Process the data
            df = pd.DataFrame(data)
            df = df.pivot(index='orgCompanyID', columns='demographic', values='demographicValue')

            # Ensure all required columns exist
            for column in columns_to_keep:
                if column not in df.columns:
                    df[column] = 'Not Found'
                    print(f"Column '{column}' not found in data, adding with default value")

            df = df[columns_to_keep]
            df = df.fillna('')
            df.reset_index(drop=True, inplace=True)

            # Reorder columns
            for column in new_order:
                if column not in df.columns:
                    df[column] = 'Not Found'

            df = df.reindex(columns=new_order)
            df['Key'] = org_name
            
            # Filter out RAL Survey Entity
            df = df[~df['OrgName'].str.contains('RAL Survey Entity', na=False, case=False)]

            # Convert and calculate Has Data
            df['OrgTotalPeriodsQty'] = pd.to_numeric(df['OrgTotalPeriodsQty'], errors='coerce').fillna(0).astype(int)
            df['Has Data'] = df['OrgTotalPeriodsQty'].apply(lambda x: 'Yes' if x > 0 else 'No')

            all_data.append(df)
            print(f"Successfully processed {key} with {len(df)} records")

        except Exception as e:
            print(f"Error processing {key}: {str(e)}")
            raise

    # Combine all data
    final_df = pd.concat(all_data, ignore_index=True)
    
    # Save reports
    output_headers = [
        'iLumen Site', 'Franchisee Name', "Store Name", "AIS Store ID", 
        "Currency", "AgreementSigned", "Country", "BU", "OrgDataStatus", 
        'Has Data', "OrgTotalPeriodsQty", "OrgQuarterlyPeriodQty", 
        "OrgMonthlyPeriodQty", "Org13PeriodQty", "PeerCurrentPeriodDisplay"
    ]
    
    # Save the progress report
    progress_report_path = os.path.join(reports_dir, f'progress_report_{now_str}.csv')
    with open(progress_report_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(output_headers)
        writer.writerows(final_df.values.tolist())
    print(f"Progress report saved to: {progress_report_path}")

    # Save the original format
    original_path = os.path.join(reports_dir, 'original.csv')
    final_df.to_csv(original_path, index=False, encoding='utf-8')
    print(f"Original format saved to: {original_path}")

if __name__ == "__main__":
    try:
        generate_report()
        print("Report generation completed successfully")
    except Exception as e:
        print(f"Error during report generation: {str(e)}")
        raise  # Re-raise the exception to ensure GitHub Actions marks the step as failed
