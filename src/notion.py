from notion_client import Client
from config import NOTION_API_KEY

notion = Client(auth=NOTION_API_KEY)

# Dictionary to map status names to Notion IDs
status_ids = {
    "Not started": "c212d4da-276c-4f43-a2cc-95bf8cabcd56",
    "In progress": "a166a5b4-a8ad-4ba7-8468-46f27ed29e56",
    "Completed": "3b3b37b2-8104-4bf1-a40d-13642c8ca16a",
}

def update_notion_document(content: dict) -> str:
    try:
        database_id = content.get("database_id")
        if not database_id:
            raise ValueError("Missing 'database_id' in content.")

        fields = content.get("fields", {})

        if content["type"] == "Tasks":
            status_name = fields.get("Status", "Not started")
            status_id = status_ids.get(status_name)

            page = notion.pages.create(
                parent={"database_id": database_id},
                properties={
                    "Name": [{"type": "text", "text": {"content": fields.get("Name", "")}}],
                    "Status": {
                        "id": status_id
                    },
                },
                children=[]
            )

        elif content["type"] == "Thoughts":
            page = notion.pages.create(
                parent={"database_id": database_id},
                properties={
                    "Name": [{"type": "text", "text": {"content": fields.get("Name", "")}}],
                    # "Created": {"date": {"start": fields.get("Created"), "end": None}},
                    # "Tags": {"multi_select": [{"name": tag} for tag in fields.get("Tags", [])]},
                    # Add other properties for Thoughts as needed, based on your database
                },
                children=[
                    {
                        "object": "block",
                        "type": "paragraph",
                        "paragraph": {
                            "rich_text": [{"type": "text", "text": {"content": fields.get("Content", "")}}]
                        }
                    }
                ]
            )

        else:
            raise ValueError("Invalid content type. Must be 'Tasks' or 'Thoughts'.")

        # Return the URL of the created page
        return f"https://www.notion.so/{page['id'].replace('-', '')}"

    except Exception as e:
        raise Exception(f"Error updating Notion document: {str(e)}")