import requests
from bs4 import BeautifulSoup


def scrape_all_data(table_url):
    """
    从表格页面提取所有链接，并从每个链接页面提取详细信息。
    """
    # 首先，从表格中提取所有链接
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

    # 然后，对每个链接提取详细信息
    all_data = []
    for link in links:
        data = scrape_data(link)
        all_data.append(data)
    return all_data


def scrape_data(url):
    response = requests.get(url)
    response.encoding = 'utf-8'
    soup = BeautifulSoup(response.text, 'html.parser')

    # 提取信息，如果找不到则返回 None
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


def categorize_address(data):
    districts = ['中區', '東區', '西區', '南區', '北區', '西屯區', '南屯區', '北屯區', '豐原區', '大里區', '太平區', '東勢區', '大甲區', '清水區',
                 '沙鹿區', '梧棲區', '后里區', '神岡區', '潭子區', '大雅區', '新社區', '石岡區', '外埔區', '大安區', '烏日區', '大肚區', '龍井區', '霧峰區', '和平區']
    categorized_data = {district: [] for district in districts}

    for entry in data:
        address = entry.get('address', '')
        for district in districts:
            if district in address:
                categorized_data[district].append(entry)
                break

    return categorized_data


def main():
    base_url = 'https://community.society.taichung.gov.tw/compoint/List.aspx?Parser=99,6,22,'
    urls = []
    table_data = []
    count = 0
    for i in range(0, 2):
        if i == 0:  # 第一页的URL有些不同
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
        print(data)
    print(count)


if __name__ == '__main__':
    main()
