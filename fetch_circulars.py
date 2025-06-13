import requests
from bs4 import BeautifulSoup
import json
import os

def fetch_and_update_circulars():
    """
    Fetches the latest circulars from the EPFO website and adds only the new ones
    to the circulars.json file.
    """
    url = "https://www.epfindia.gov.in/site_en/circulars.php?id=sm7_officeUse"
    json_file = 'circulars.json'

    # Load existing circulars
    if os.path.exists(json_file):
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                existing_circulars = json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            existing_circulars = []
    else:
        existing_circulars = []

    existing_sr_numbers = {c['sr'] for c in existing_circulars}

    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for bad status codes
    except requests.exceptions.RequestException as e:
        print(f"Error fetching the URL: {e}")
        return

    soup = BeautifulSoup(response.content, 'html.parser')

    new_circulars = []
    table = soup.find('table', {'class': 'table'})

    if not table:
        print("Could not find the circulars table on the page.")
        return

    rows = table.find_all('tr')[1:]  # Skip the header row

    for row in rows:
        cols = row.find_all('td')
        if len(cols) == 4:
            sr_no = cols[0].text.strip()

            # Only add if the circular is not already in our list
            if sr_no not in existing_sr_numbers:
                subject_and_date = cols[1].get_text(separator='\n').strip().split('\n')
                subject = subject_and_date[0] if subject_and_date else ''
                date = subject_and_date[1] if len(subject_and_date) > 1 else ''

                hindi_link = cols[2].find('a')
                english_link = cols[3].find('a')

                hindi_href = "https://www.epfindia.gov.in" + hindi_link['href'].replace('..','') if hindi_link else 'NA'
                english_href = "https://www.epfindia.gov.in" + english_link['href'].replace('..','') if english_link else 'NA'

                new_circulars.append({
                    "sr": sr_no,
                    "subject": subject,
                    "hindi": hindi_href,
                    "english": english_href,
                    "year": "",
                    "date": date
                })

    if new_circulars:
        # Prepend new circulars to maintain descending order by date
        updated_circulars = new_circulars + existing_circulars

        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(updated_circulars, f, ensure_ascii=False, indent=4)
        print(f"Successfully added {len(new_circulars)} new circulars to {json_file}")
    else:
        print("No new circulars found.")

if __name__ == "__main__":
    fetch_and_update_circulars()
