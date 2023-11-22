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

def add_info_to_notion_database(notion_token, database_id, data):
    """
    Adds a new row (page) to a specified Notion database.

    Parameters:
    notion_token (str): The authorization token for the Notion API.
    database_id (str): The ID of the Notion database where the row will be added.
    data (dict): The data for the new row.

    Returns:
    dict: The response from the Notion API.
    """
    headers = {
        "Authorization": f"Bearer {notion_token}",
        "Notion-Version": "2022-06-28",
        "Content-Type": "application/json"
    }

    create_page_url = f"https://api.notion.com/v1/pages"

    page_data = {
        "parent": {"database_id": database_id},
        "properties": {
            "對接窗口": {"rich_text": [{"text": {"content": data['對接窗口']}}]},
            "電話": {"phone_number": data['電話']},
            "Email": {"email": data['Email']},
            "部落名稱": {"title": [{"text": {"content": data['部落名稱'],"link": {"url": data['部落連結']}}}]},
            "聯絡進度": {"select": {"name": data['聯絡進度']}},
            "意願程度": {"select": {"name": data['意願程度']}},
            "聯絡方式": {"select": {"name": data['聯絡方式']}}
        }
    }

    response = requests.post(create_page_url, headers=headers, json=page_data)
    return response.json()

# Write a function to add many info into database
def add_many_info_to_notion_database(notion_token, database_id, data_list):
    """
    Adds a new row (page) to a specified Notion database.

    Parameters:
    notion_token (str): The authorization token for the Notion API.
    database_id (str): The ID of the Notion database where the row will be added.
    data_list (list): The list of data for the new rows.

    Returns:
    dict: The response from the Notion API.
    """
    for data in data_list:
        add_info_to_notion_database(notion_token, database_id, data)

def create_notion_database(notion_token, parent_page_id, database_title):
    """
    Creates a new Notion database under a specified parent page.

    Parameters:
    notion_token (str): The authorization token for the Notion API.
    parent_page_id (str): The ID of the parent page where the database will be created.
    database_title (str): The title of the new database.
    """
    # 設定 API endpoint
    url = "https://api.notion.com/v1/databases"

    # 設定請求頭
    headers = {
        "Authorization": f"Bearer {notion_token}",
        "Content-Type": "application/json",
        "Notion-Version": "2021-08-16"  # 使用最新的 Notion API 版本
    }

    # 定義資料庫的結構
    data = {
        "parent": {"type": "page_id", "page_id": parent_page_id},
        "title": [
            {
                "type": "text",
                "text": {"content": database_title}
            }
        ],
        "properties": {
            "電話": {"phone_number": {}},
            "社區名稱": {"title": {}},
            "對接窗口": {"rich_text": {}},
            "職稱": {"rich_text": {}},
            "Email": {"email": {}},
            "人口數量":{"number":{}},
            "地址": {"rich_text": {}},
            "聯絡進度": {"select": {
                "options": [
                    {"name": "已聯絡", "color": "blue"},
                    {"name": "待聯絡", "color": "green"}
                ]
            }},
            "意願程度": {"select": {
                "options": [
                    {"name": "不方便", "color": "red"},
                    {"name": "當面了解", "color": "yellow"},
                    {"name": "願意合作", "color": "green"},
                    {"name": "None", "color": "gray"}
                ]
            }},
            "聯絡方式": {"select": {
                "options": [
                    {"name": "電訪+Email", "color": "blue"},
                    {"name": "電訪", "color": "yellow"},
                    {"name": "Email", "color": "green"},
                    {"name": "None", "color": "gray"}
                ]
            }}
        }
    }

    # 發送請求
    response = requests.post(url, headers=headers, json=data)
    database_id = response.json().get('id', None)

    # 返回響應
    return database_id

def main():
    NOTION_TOKEN = os.getenv("INTERNAL_INTEGRATION_SECRET")
    DATABASE_ID = os.getenv("DATABASE_ID")
    PAGE_ID = os.getenv("PAGE_ID")
    # results_json = read_notion_database(NOTION_TOKEN, DATABASE_ID)
    # Process your data using the functions
    # 'your_json_data' is the JSON data obtained from Notion API
    # pages = results_json['results']
    # extracted_data = extract_data_from_pages(pages)

    # Print the results
    # for data in extracted_data:
    #     print(data)
    #     pass

    # Test the add_row_to_notion_database function
    data = {
        '對接窗口': '張三',
        '電話': '0912345678',
        'Email': 'kejcwrkjfh@gmail.com',
        '部落名稱': '山村部落',
        '部落連結': 'https://community.society.taichung.gov.tw/compoint/Details.aspx?Parser=99%2C6%2C22%2C%2C%2C%2C16582',
        '聯絡進度': "待聯絡",
        '意願程度': 'None',
        '聯絡方式': 'None'
    }
    print(add_info_to_notion_database(NOTION_TOKEN, DATABASE_ID, data))
    # 使用函式
    # database_title = '霧峰區'

    # response = create_notion_database(NOTION_TOKEN,PAGE_ID,database_title)
    # print(response)


if __name__ == "__main__":
    dotenv.load_dotenv()
    main()



