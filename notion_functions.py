import os
import dotenv
import requests


def read_notion_database(notion_token, database_id):
    """
    Reads the content of a specified Notion database.

    Parameters:
    notion_token (str): The authorization token for the Notion API.
    database_id (str): The ID of the Notion database to be read.

    Returns:
    dict: The content of the database as retrieved from the Notion API.
    """
    headers = {
        "Authorization": f"Bearer {notion_token}",
        "Notion-Version": "2022-06-28",  # Replace with the current version of Notion
        "Content-Type": "application/json"
    }

    read_database_url = f"https://api.notion.com/v1/databases/{database_id}/query"

    response = requests.post(read_database_url, headers=headers)
    return response.json()


def get_field_value(page, field_name):
    field_type = page['properties'][field_name]['type']
    
    if field_type == 'rich_text':
        return page['properties'][field_name]['rich_text'][0]['plain_text']
    elif field_type == 'phone_number':
        return page['properties'][field_name]['phone_number']
    elif field_type == 'email':
        return page['properties'][field_name]['email']
    elif field_type == 'select':
        if page['properties'][field_name]['select']:
            return page['properties'][field_name]['select']['name']
        else:
            return None
    elif field_type == 'title':
        # 提取標題和相關連結
        title_text = page['properties'][field_name]['title'][0]['plain_text']
        title_link = page['properties'][field_name]['title'][0]['text']['link']
        if title_link:
            return title_text, title_link['url'] # 返回標題和連結
        else:
            return title_text, None # 如果沒有連結，則返回 None
    else:
        return None

def extract_data_from_pages(pages):
    extracted_data = []

    for page in pages:
        contact_name = get_field_value(page, '對接窗口')
        phone_number = get_field_value(page, '電話')
        email = get_field_value(page, 'Email')
        tribe_name, tribe_link = get_field_value(page, '部落名稱') # 獲取部落名稱和連結
        contact_progress = get_field_value(page, '聯絡進度')
        willingness = get_field_value(page, '意願程度')
        contact_method = get_field_value(page, '聯絡方式')

        page_data = {
            '聯絡人姓名': contact_name,
            '電話號碼': phone_number,
            '電子郵件': email,
            '部落名稱': tribe_name,
            '部落連結': tribe_link, # 添加部落連結
            '聯絡進度': contact_progress,
            '意願程度': willingness,
            '聯絡方式': contact_method,
        }

        extracted_data.append(page_data)

    return extracted_data


def main():
    NOTION_TOKEN = os.getenv("INTERNAL_INTEGRATION_SECRET")
    DATABASE_ID = os.getenv("DATABASE_ID")
    results_json = read_notion_database(NOTION_TOKEN, DATABASE_ID)
    # Process your data using the functions
    # 'your_json_data' is the JSON data obtained from Notion API
    pages = results_json['results']
    extracted_data = extract_data_from_pages(pages)

    # Print the results
    for data in extracted_data:
        print(data)
        pass


if __name__ == "__main__":
    dotenv.load_dotenv()
    main()
