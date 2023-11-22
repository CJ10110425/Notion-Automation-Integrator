import requests
from bs4 import BeautifulSoup
import csv


def scrape_all_data(table_url):
    """
    從表格頁面提取所有鏈接，並從每個鏈接頁面提取詳細信息。
    """
    # 從表格中提取所有鏈接
    response = requests.get(table_url)
    response.encoding = 'utf-8'
    soup = BeautifulSoup(response.text, 'html.parser')
    table = soup.find('table')
    rows = table.find_all('tr')

    links = []
    for row in rows:
        link = row.find('a')
        if link and 'href' in link.attrs:
            full_link = "https://community.society.taichung.gov.tw/compoint/" + \
                link['href']
            links.append(full_link)

    # 對每個鏈接提取詳細信息
    all_data = []
    for link in links:
        data = scrape_data(link)
        all_data.append(data)
    return all_data


def scrape_data(url):
    """
    從給定的 URL 提取社團相關的詳細信息。
    """
    response = requests.get(url)
    response.encoding = 'utf-8'
    soup = BeautifulSoup(response.text, 'html.parser')

    # 提取信息，如果找不到則返回 None
    name_element = soup.find("dd", class_="tabulation_tt", string="社團名稱")
    name = name_element.find_next_sibling(
        "dt").text.strip() if name_element else None

    population_element = soup.find(
        "dd", class_="tabulation_tt", string="社區人口數")
    population = population_element.find_next_sibling(
        "dt").text.strip() if population_element else None

    address_element = soup.find("dd", class_="tabulation_tt", string="聯絡地址")
    address = address_element.find_next_sibling(
        "dt").text.strip() if address_element else None

    email_element = soup.find("dd", class_="tabulation_tt", string="電子信箱")
    email = email_element.find_next_sibling(
        "dt").text.strip() if email_element else None

    contact_info = soup.find("ul", id="comm2")
    if contact_info:
        contact_person_element = contact_info.find("dd", string="聯絡窗口")
        contact_person = contact_person_element.find_next_sibling(
            "dt").text.strip() if contact_person_element else None

        title_element = contact_info.find(
            "dd", string=lambda text: "職" in text)
        title = title_element.find_next_sibling(
            "dt").text.strip() if title_element else None

        phone_element = contact_info.find(
            "dd", string=lambda text: "電" in text)
        phone = phone_element.find_next_sibling(
            "dt").text.strip() if phone_element else None
    else:
        contact_person = title = phone = None

    return {
        "name": name,
        "population": population,
        "address": address,
        "email": email,
        "contact_person": contact_person,
        "title": title,
        "phone": phone
    }


def write_to_csv(data_list):
    """
    將數據列表寫入 CSV 文件。
    :param data_list: 包含字典的列表，每個字典代表一行數據。
    """
    filename = 'community_associations.csv'
    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        if data_list:
            fieldnames = data_list[0].keys()
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            for data in data_list:
                writer.writerow(data)
        else:
            print("提供的數據列表為空。")

    print(f'數據已寫入 {filename}')


def main():
    """
    主控制函數，生成多個 URL，提取數據，然後寫入 CSV 文件。
    """
    base_url = 'https://community.society.taichung.gov.tw/compoint/List.aspx?Parser=99,6,22,'
    urls = []
    table_data = []
    count = 0
    for i in range(0, 62):
        if i == 0:  # 第一頁的 URL 有些不同
            url = base_url + ',,,,,,,,,,,,400-401-403-402-404-407-408-406-420-412-411-423-437-436-433-435-421-429-427-428-426-422-438-439-414-432-434-413-424,1'
        else:
            url = base_url + ',,,,,,,' + \
                str(i) + ',,,,,400-401-403-402-404-407-408-406-420-412-411-423-437-436-433-435-421-429-427-428-426-422-438-439-414-432-434-413-424,1'
        urls.append(url)
    for url in urls:
        datas = scrape_all_data(url)
        table_data.append(datas)
    for data in table_data:
        count = count + len(data)
    print(count)
    merged_data_list = [item for sublist in table_data for item in sublist]
    write_to_csv(merged_data_list)


if __name__ == '__main__':
    main()
