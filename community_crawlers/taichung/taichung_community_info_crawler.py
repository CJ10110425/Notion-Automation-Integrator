import requests
from bs4 import BeautifulSoup


def scrape_table_data(url):
    """
    從給定的URL抓取表格數據並返回解析後的數據。
    """
    # 使用requests獲取網頁內容
    response = requests.get(url)
    response.encoding = 'utf-8'  # 確保正確的編碼

    # 使用BeautifulSoup解析HTML
    soup = BeautifulSoup(response.text, 'html.parser')

    # 查找並解析表格
    table = soup.find('table')  # 根據您的網頁結構調整這行
    rows = table.find_all('tr')

    # 用於存儲所有行的數據
    all_data = []

    # 提取表格每一行的數據
    for row in rows:
        cols = row.find_all('td')
        cols_text = [ele.text.strip() for ele in cols]
        # 尋找每個單元格中的連結
        cols_link = [ele.find('a')['href'] if ele.find('a')
                     else '' for ele in cols]
        data = [text for text in cols_text if text]  # 文本數據
        # 確保連結不是空的，並將其拼接為完整URL
        links = ["https://community.society.taichung.gov.tw/compoint/" +
                 link for link in cols_link if link]

        all_data.append((data, links))

    return all_data


def main():
    url = 'https://community.society.taichung.gov.tw/compoint/List.aspx?Parser=99,6,22,,,,,,,,,,,,,400-401-403-402-404-407-408-406-420-412-411-423-437-436-433-435-421-429-427-428-426-422-438-439-414-432-434-413-424,1'
    table_data = scrape_table_data(url)
    for data, links in table_data:
        print(data, links)

if __name__ == '__main__':
    main()