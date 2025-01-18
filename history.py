import requests
from bs4 import BeautifulSoup
import json

# 定义目标 URL 列表
URLS = [f"https://www.boc.cn/sourcedb/whpj/index_{i}.html" for i in range(1, 10)] + [
    "https://www.boc.cn/sourcedb/whpj/index.html"
]

# 设置目标币种
TARGET_CURRENCIES = ["新加坡元", "美元", "欧元", "英镑", "日元", "韩国元"]


# 爬取汇率数据
def scrape_exchange_rates(url, target_currencies, data):
    """
    爬取目标 URL 的汇率信息并返回指定币种的数据。

    Args:
        url (str): 目标 URL。
        target_currencies (list): 需要提取的币种列表。

    Returns:
        dict: 包含目标币种及其汇率的字典。
    """
    try:
        response = requests.get(url)
        response.encoding = "utf-8"
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            # 查找目标表格
            tables = soup.find_all("table")
            if len(tables) < 2:
                print(f"未在 {url} 找到有效的表格。")
                return {}

            table = tables[1]
            rows = table.find_all("tr")
            for row in rows[1:]:  # 跳过表头
                cols = [col.text.strip() for col in row.find_all("td")]
                if cols and cols[0] in target_currencies:
                    currency = cols[0]
                    rate = cols[3]
                    update_day = cols[6][:10]
                    update_time = cols[7]
                    if currency not in data:
                        data[currency] = {}
                    if update_day not in data[currency]:
                        data[currency][update_day] = {}
                    data[currency][update_day][update_time] = rate
            return data
        else:
            print(f"请求失败，状态码：{response.status_code}")
            return {}
    except Exception as e:
        print(f"请求 {url} 时发生错误：{e}")
        return {}


# 从 JSON 文件中读取现有历史数据
def load_from_json(filename="history_rates.json"):
    # 尝试读取现有文件中的数据
    try:
        with open(filename, "r", encoding="utf-8") as f:
            existing_data = json.load(f)
    except FileNotFoundError:
        existing_data = {}
    return existing_data


# 保存数据为 JSON 文件
def save_to_json(data, filename="history_rates.json"):
    """
    将数据保存为 JSON 文件。

    Args:
        data (dict): 要保存的数据。
        filename (str): 文件名。
    """
    try:
        # 保存更新后的数据
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        print(f"数据已成功保存到 {filename}")
    except Exception as e:
        print(f"保存 JSON 文件时出错：{e}")


# 主程序
def main():
    """
    主程序逻辑，爬取汇率并根据条件发送通知。
    """
    history_data = load_from_json("history_rates.json")
    for url in URLS:
        history_data = scrape_exchange_rates(url, TARGET_CURRENCIES, history_data)

    if not history_data:
        print("未获取到任何汇率数据。")
        return

    # 保存数据为 JSON 文件
    save_to_json(history_data)


if __name__ == "__main__":
    main()
