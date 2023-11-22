import os
import dotenv
import requests
import pandas as pd
import time

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
            "社區名稱": {"title": [{"text": {"content": data['社區名稱']}}]},
            "職稱": {"rich_text": [{"text": {"content": data['職稱']}}]},
            "人口數量": {"number": data['人口數量']},
            "地址": {"rich_text": [{"text": {"content": data['地址']}}]},
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
    districts_with_ids = [
        {"name": "中區", "id": "db21b6d1-7cec-4ed7-be92-9bc3377e9ed9"},
        {"name": "東區", "id": "9b8329c7-e496-4ecb-998c-2a313bb3dbb1"},
        {"name": "西區", "id": "cb277c71-a6fa-41e4-b6f5-b71cffc012ec"},
        {"name": "南區", "id": "03cda376-5020-4178-bd2a-ea035c0f98d4"},
        {"name": "北區", "id": "9dddfd64-b79f-4c43-b72b-d6d3afab01db"},
        {"name": "西屯區", "id": "c1b715ee-a604-4a7b-bc93-771dbcc97bae"},
        {"name": "南屯區", "id": "30056130-67cb-4bd8-a38d-23759d5362a9"},
        {"name": "北屯區", "id": "1934473a-fd4e-4720-a1d6-f4bf4d0b2681"},
        {"name": "豐原區", "id": "9da5cc8c-7f7c-446b-b78f-8e30fc052aa0"},
        {"name": "大里區", "id": "456c2bc8-1b9b-4c0d-8df4-765a9f7b182d"},
        {"name": "太平區", "id": "e37416ba-ab10-4a7d-a29b-e0374145a2f3"},
        {"name": "東勢區", "id": "8aebfab7-fa7a-4d8d-a424-a62169b4f250"},
        {"name": "大甲區", "id": "6e719c7d-5b68-4be2-aa0a-d8d6ca79759f"},
        {"name": "清水區", "id": "5611a974-0b85-454d-b4ba-34917cdc55f3"},
        {"name": "沙鹿區", "id": "cb60bb78-11e5-4e3d-b551-4b1b7f3ebed9"},
        {"name": "梧棲區", "id": "f5d3b75c-7577-471f-86ef-167f126d0903"},
        {"name": "后里區", "id": "e3f75277-a6f2-4286-9f38-b6e6841c098a"},
        {"name": "神岡區", "id": "60751b1d-5fd1-470b-91fe-36315a81b980"},
        {"name": "潭子區", "id": "0f8be5d3-3efb-492a-9b49-71819841af27"},
        {"name": "大雅區", "id": "1f7f2da8-bd8b-49e0-a41a-30868f10a063"},
        {"name": "新社區", "id": "8831e250-038c-4208-abe6-017cca78af69"},
        {"name": "石岡區", "id": "8197d413-e21a-444f-897a-92f82dfb6209"},
        {"name": "外埔區", "id": "4c652c26-14a4-40ce-b21a-b669429db49d"},
        {"name": "大安區", "id": "30f111be-103d-4e40-b19e-23b4e590a741"},
        {"name": "烏日區", "id": "7a99a34b-318e-47c0-93b5-484534ebd87e"},
        {"name": "大肚區", "id": "13cef29c-5ab8-4aa7-96ff-7b015b0e5f19"},
        {"name": "龍井區", "id": "61e6d1df-a748-4538-be74-812dc06e0b47"},
        {"name": "霧峰區", "id": "ebf2de69-eae0-4ca1-bd6c-fbe2670071ad"},
        {"name": "和平區", "id": "609f25de-9207-469b-849e-2075f19054e8"}
    ]
    NOTION_TOKEN = os.getenv("INTERNAL_INTEGRATION_SECRET")
    # DATABASE_ID = os.getenv("DATABASE_ID")
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
    # data = {
    #         '對接窗口': "ef",
    #         '電話': "0966747312",
    #         'Email': ";wlnkef@gmail.com",
    #         '社區名稱': "wefwf",
    #         '職稱': 'erge3w',
    #         '人口數量': 21431,
    #         '地址': 'fwefwefwe',
    #         '聯絡進度': '待聯絡',  # CSV 檔案中未提供這個資訊
    #         '意願程度': 'None',  # CSV 檔案中未提供這個資訊
    #         '聯絡方式': 'None'   # CSV 檔案中未提供這個資訊
    #     }
    # print(add_info_to_notion_database(NOTION_TOKEN, "db21b6d17cec4ed7be929bc3377e9ed9", data))
    # 使用函式
    # database_title = '霧峰區'

    # response = create_notion_database(NOTION_TOKEN,PAGE_ID,database_title)
    # print(response)
    # districts = ["石岡區"]
    # for district in districts:
    #     database_id = create_notion_database(NOTION_TOKEN, PAGE_ID, f"臺中市{district}")
    #     print(f"Database created for {district} District with ID: {database_id}")
    
    # CSV 檔案路徑與區域的對應
    file_paths = {
        '中區': 'community_crawlers/taichung/community/中區.csv',
        '北區': 'community_crawlers/taichung/community/北區.csv',
        '北屯區':'community_crawlers/taichung/community/北屯區.csv',
        '南區': 'community_crawlers/taichung/community/南區.csv',
        '大里區': 'community_crawlers/taichung/community/大里區.csv',
        '太平區': 'community_crawlers/taichung/community/太平區.csv',
        '大雅區': 'community_crawlers/taichung/community/大雅區.csv',
        '大甲區': 'community_crawlers/taichung/community/大甲區.csv',
        '大肚區': 'community_crawlers/taichung/community/大肚區.csv',
        '和平區': 'community_crawlers/taichung/community/和平區.csv',
        '東區': 'community_crawlers/taichung/community/東區.csv',
        '東勢區': 'community_crawlers/taichung/community/東勢區.csv',
        '梧棲區': 'community_crawlers/taichung/community/梧棲區.csv',
        '清水區': 'community_crawlers/taichung/community/清水區.csv',
        '潭子區': 'community_crawlers/taichung/community/潭子區.csv',
        '烏日區': 'community_crawlers/taichung/community/烏日區.csv',
        '石岡區': 'community_crawlers/taichung/community/石岡區.csv',
        '神岡區': 'community_crawlers/taichung/community/神岡區.csv',
        '西區': 'community_crawlers/taichung/community/西區.csv',
        '西屯區': 'community_crawlers/taichung/community/西屯區.csv',
        '南屯區': 'community_crawlers/taichung/community/南屯區.csv',
        '豐原區': 'community_crawlers/taichung/community/豐原區.csv',
        '沙鹿區': 'community_crawlers/taichung/community/沙鹿區.csv',
        '后里區': 'community_crawlers/taichung/community/后里區.csv',
        '新社區': 'community_crawlers/taichung/community/新社區.csv',
        '外埔區': 'community_crawlers/taichung/community/外埔區.csv',
        '大安區': 'community_crawlers/taichung/community/大安區.csv',
        '龍井區': 'community_crawlers/taichung/community/龍井區.csv',
        '霧峰區': 'community_crawlers/taichung/community/霧峰區.csv'
    }

    # 將各個區域名稱與對應的 ID 對應起來
    district_id_map = {district['name']: district['id'] for district in districts_with_ids}
    # 讀取 CSV 檔案並轉換為 data_example 格式，然後添加到 data_list
    data_list = []
    for district, file_path in file_paths.items():
        district_data = pd.read_csv(file_path)
        for _, row in district_data.iterrows():
            population_str = str(row['population'])
            # 检查字符串是否为 'nan'
            if population_str.lower() == 'nan':
                cleaned_population = 0
            else:
                cleaned_population = int(population_str.replace(',', '').replace(' 人', ''))
            data_example = {
                '對接窗口': row['contact_person'],
                '電話': row['phone'],
                'Email': row['email'] if pd.notna(row['email']) else 'None',
                '社區名稱': row['name'],
                '職稱': row['title'],
                '人口數量':cleaned_population,
                '地址': row['address'],
                '聯絡進度': '待聯絡',  # CSV 檔案中未提供這個資訊
                '意願程度': 'None',  # CSV 檔案中未提供這個資訊
                '聯絡方式': 'None'   # CSV 檔案中未提供這個資訊
            }
            data_list.append({'database_id': district_id_map[district], 'data': data_example})
    for item in data_list:
        database_id = item['database_id']
        data = item['data']
        print(add_info_to_notion_database(NOTION_TOKEN, database_id, data))
        time.sleep(0.1)

if __name__ == "__main__":
    dotenv.load_dotenv()
    main()



