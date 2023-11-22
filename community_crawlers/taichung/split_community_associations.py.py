import pandas as pd

# Load the CSV file
file_path = '/Users/lipinze/Desktop/Notion-Automation-Integrator/community_associations.csv'
community_associations_df = pd.read_csv(file_path)

# Extracting the district information from the 'name' column
community_associations_df['district'] = community_associations_df['name'].apply(lambda x: x.split('區')[0][-2:] + '區')

# List of districts to filter and save as separate CSV files
districts = [
    "中區", "東區", "西區", "南區", "北區", "西屯區", "南屯區", "北屯區", "豐原區", "大里區", "太平區", "東勢區",
    "大甲區", "清水區", "沙鹿區", "梧棲區", "后里區", "神岡區", "潭子區", "大雅區", "新社區", "石岡區", "外埔區",
    "大安區", "烏日區", "大肚區", "龍井區", "霧峰區", "和平區"
]

for district in districts:
    # Filter the dataframe for the current district
    district_df = community_associations_df[community_associations_df['district'] == district]

    # Save to a new CSV file if there are entries for the district
    if not district_df.empty:
        district_file_path = f'/Users/lipinze/Desktop/Notion-Automation-Integrator/{district}.csv'
        district_df.to_csv(district_file_path, index=False)
