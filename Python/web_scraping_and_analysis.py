import requests
from bs4 import BeautifulSoup
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

def get_exchange_rate_data(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        table = soup.find('table', {'class': 'tbl_list'})
        if not table:
            print("테이블을 찾을 수 없다.")
            return None

        rows = table.find('tbody').find_all('tr')
        
        data = []
        for row in rows:
            cols = row.find_all('td')
            if len(cols) > 0:
                currency = cols[0].text.strip()
                exchange_rate = float(cols[1].text.strip().replace(',', ''))
                change = float(cols[2].text.strip().replace(',', ''))
                data.append([currency, exchange_rate, change])
                
        df = pd.DataFrame(data, columns=['통화', '매매기준율', '전일대비'])
        return df

    except requests.exceptions.RequestException as e:
        print(f"웹 요청 중 오류 발생: {e}")
        return None

def analyze_and_visualize_data(df):
    if df is None:
        return

    print("수집된 데이터:")
    print(df.head())
    print("데이터 요약:")
    print(df.describe())
    
    plt.style.use('seaborn-v0_8-whitegrid')
    
    plt.figure(figsize=(12, 7))
    sns.barplot(x='통화', y='매매기준율', data=df.sort_values(by='매매기준율', ascending=False), palette='viridis')
    plt.title('주요국 통화별 매매기준율')
    plt.xlabel('통화')
    plt.ylabel('매매기준율 (원)')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.show()

    plt.figure(figsize=(10, 6))
    sns.histplot(df['매매기준율'], bins=10, kde=True, color='skyblue')
    plt.title('매매기준율 분포')
    plt.xlabel('매매기준율')
    plt.ylabel('빈도수')
    plt.tight_layout()
    plt.show()

if __name__ == '__main__':
    naver_finance_url = 'https://finance.naver.com/marketindex/exchangeList.naver'
    
    print("웹 페이지에서 환율 데이터 스크래핑 시작...")
    exchange_rate_df = get_exchange_rate_data(naver_finance_url)
    
    if exchange_rate_df is not None:
        analyze_and_visualize_data(exchange_rate_df)
        print("데이터 분석 및 시각화 완료.")