import json
import subprocess
import re
import sys

DRIVE_FOLDER_ID = '1YUT00lIw6UMlGiNgkqcYPuipQE6c6u5B'

def get_drive_briefs():
    cmd = ["gog", "drive", "search", f"'{DRIVE_FOLDER_ID}' in parents", "--max", "500", "--json"]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        return []
    try:
        data = json.loads(result.stdout)
        return data.get('files', [])
    except:
        return []

def clean_name(s):
    if not s: return ""
    # Remove common suffixes and brief labels
    s = s.replace('_Pre-Call_Brief.pdf', '').replace('.pdf', '')
    s = s.replace('_', ' ').replace('-', ' ').strip().lower()
    # Handle specific common variations
    s = s.replace(' biosolutions', ' bio').replace(' genetics', '').replace(' robotics', '').replace(' labs', '')
    s = re.sub(r' (inc|corp|llc|ag|bio|agtech)$', '', s)
    return s.strip()

def sync():
    json_path = "data/pipeline.json"
    try:
        with open(json_path, 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        print("Data file not found.")
        return
    
    briefs = get_drive_briefs()
    brief_map = {clean_name(b['name']): b['webViewLink'] for b in briefs}
    updated_count = 0
    
    for deal in data['deals']:
        company_clean = clean_name(deal['company'])
        if company_clean in brief_map:
            new_url = brief_map[company_clean]
            if deal.get('brief_url') != new_url:
                deal['brief_url'] = new_url
                deal['updated_at'] = "2026-03-11"
                updated_count += 1
                print(f"Synced brief for {deal['company']}")

    if updated_count > 0:
        with open(json_path, 'w') as f:
            json.dump(data, f, indent=2)
        print(f"Total: {updated_count} updates saved.")
    else:
        print("Everything up to date.")

if __name__ == "__main__":
    sync()
