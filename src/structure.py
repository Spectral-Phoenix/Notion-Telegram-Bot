import requests
from collections import deque
import time
import concurrent.futures
import json
import os
from datetime import datetime

# Replace with your Notion integration token
NOTION_TOKEN = "secret_GK4jGTAp26UwRfy1lT55RZwoEQPKsCnqFPnIfqPjJJp"

# Replace with the ID of the page containing the databases
PAGE_ID = "add3e3ebc3ff4ee38974df2b8a31e45f"

NOTION_API_BASE = "https://api.notion.com/v1"
NOTION_HEADERS = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}

def get_databases_from_block(block_id):
    """Retrieves all databases present within a Notion block (page or database)."""
    databases = []
    has_more = True
    start_cursor = None

    while has_more:
        url = f"{NOTION_API_BASE}/blocks/{block_id}/children"
        params = {"page_size": 100}
        if start_cursor:
            params["start_cursor"] = start_cursor

        response = requests.get(url, headers=NOTION_HEADERS, params=params).json()

        for child in response["results"]:
            if child["type"] == "child_database":
                databases.append(child)
            elif child["type"] == "child_page":
                pass  # We'll handle recursive searches differently

        has_more = response["has_more"]
        start_cursor = response["next_cursor"]

    return databases

def get_database_info(database_id):
    """Retrieves detailed information about a specific database."""
    url = f"{NOTION_API_BASE}/databases/{database_id}"
    response = requests.get(url, headers=NOTION_HEADERS).json()

    title = "Untitled"
    if 'title' in response:
        title_items = response['title']
        if title_items and isinstance(title_items, list):
            title = title_items[0].get('plain_text', 'Untitled')
        elif isinstance(title_items, dict):
            title = title_items.get('plain_text', 'Untitled')

    description = "No description"
    if 'description' in response:
        desc_items = response['description']
        if desc_items and isinstance(desc_items, list):
            description = desc_items[0].get('plain_text', 'No description')
        elif isinstance(desc_items, str):
            description = desc_items

    schema = response.get('properties', {})

    return {
        "title": title,
        "id": database_id,
        "description": description,
        "schema": schema
    }

def retrieve_all_pages(database_id):
    """Retrieves all pages from a Notion database, handling pagination."""
    all_pages = []
    has_more = True
    next_cursor = None

    while has_more:
        url = f"{NOTION_API_BASE}/databases/{database_id}/query"
        payload = {"page_size": 100}
        if next_cursor:
            payload["start_cursor"] = next_cursor

        response = requests.post(url, headers=NOTION_HEADERS, json=payload).json()

        if "results" in response:
            all_pages.extend(response["results"])
            has_more = response["has_more"]
            next_cursor = response["next_cursor"]
        else:
            print(f"Error retrieving pages: {response}")
            break

    return all_pages

def process_block(block_id, visited):
    """Process a single block, returning its databases and pages."""
    if block_id in visited:
        return [], []

    visited.add(block_id)
    databases = get_databases_from_block(block_id)

    block_databases = []
    pages_list = []

    for database in databases:
        db_info = get_database_info(database['id'])
        block_databases.append(db_info)

        pages = retrieve_all_pages(database['id'])
        for page in pages:
            page_title = next((prop_value['title'][0]['plain_text']
                               for prop_name, prop_value in page['properties'].items()
                               if prop_value['type'] == 'title' and prop_value['title']), "Untitled")
            pages_list.append({
                "title": page_title,
                "id": page['id']
            })

    # Check for pages within regular pages (not databases)
    if not databases:
        url = f"{NOTION_API_BASE}/blocks/{block_id}/children"
        response = requests.get(url, headers=NOTION_HEADERS).json()
        for page in response['results']:
            if page['type'] == 'child_page':
                pages_list.append({
                    "title": page['child_page']['title'],
                    "id": page['id']
                })

    return block_databases, pages_list

def build_database_tree(block_id):
    """Builds a tree structure of databases within a Notion block using parallel processing."""
    queue = deque([block_id])
    visited = set()
    tree = []
    all_pages = []

    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        while queue:
            current_batch = list(queue)
            queue.clear()

            future_to_block = {executor.submit(process_block, block_id, visited): block_id for block_id in current_batch}

            for future in concurrent.futures.as_completed(future_to_block):
                block_databases, block_pages = future.result()
                tree.extend(block_databases)
                all_pages.extend(block_pages)

                queue.extend([db['id'] for db in block_databases])
                queue.extend([page['id'] for page in block_pages])

    return tree, all_pages

def get_options_string(prop_details):
    """Returns a string of options with their IDs for select, multi-select, and status properties."""
    options = prop_details.get(prop_details['type'], {}).get('options', [])
    option_strings = [f"{option.get('name', '')} (ID: {option.get('id', '')})" for option in options]
    return f"[{', '.join(option_strings)}]" if option_strings else ""

def print_database_info(database, file=None, indent=0): 
    """Prints detailed information about a database to a file or console."""
    print("  " * indent + f"- {database['title']} (ID: {database['id']})", file=file)
    print("  " * (indent + 2) + f"Description: {database['description']}", file=file)
    print("  " * (indent + 2) + "Schema:", file=file)
    for prop_name, prop_details in database['schema'].items():
        prop_type = prop_details['type']
        options_string = ""
        if prop_type in ['select', 'multi_select', 'status']:
            options_string = get_options_string(prop_details)

        # Check for multi-select tags and add the statement
        if prop_type == 'multi_select' and prop_name.lower() == 'tags':
            options_string += " (You can add additional tags if required)"

        print("  " * (indent + 4) + f"{prop_name}: {prop_type} {options_string}", file=file)

if __name__ == "__main__":
    # Specify the folder path where you want to save the file
    output_folder = "src/prompts"

    start_time = time.time()

    database_tree, pages_list = build_database_tree(PAGE_ID)

    end_time = time.time()
    elapsed_time = end_time - start_time

    # Create the output folder if it doesn't exist
    os.makedirs(output_folder, exist_ok=True)

    # Construct the full file path
    file_path = os.path.join(output_folder, "structure.txt")

    # Store output in the specified file with timestamp
    with open(file_path, "w") as f:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"Generated on: {timestamp}", file=f)
        print(file=f)

        for db in database_tree:
            print_database_info(db, file=f)