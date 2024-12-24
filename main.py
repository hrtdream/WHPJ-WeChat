import requests
from bs4 import BeautifulSoup
import time
from datetime import datetime
import os

# 定义目标 URL 列表
URLS = [
    "https://www.boc.cn/sourcedb/whpj/index_1.html",
    "https://www.boc.cn/sourcedb/whpj/index.html",
]

# 设置目标币种
TARGET_CURRENCIES = ["欧元", "新加坡元"]


# 爬取汇率数据
def scrape_exchange_rates(url, target_currencies):
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
            data = {}
            for row in rows[1:]:  # 跳过表头
                cols = [col.text.strip() for col in row.find_all("td")]
                if cols and cols[0] in target_currencies:
                    data[cols[0]] = cols[3]  # 现汇汇率位于第 4 列
            return data
        else:
            print(f"请求失败，状态码：{response.status_code}")
            return {}
    except Exception as e:
        print(f"请求 {url} 时发生错误：{e}")
        return {}


# 发送消息到微信
def send_to_wechat(title):
    """
    发送消息到微信。

    Args:
        title (str): 消息内容。
    """
    try:
        appkey = os.environ["APPKEY"]
    except KeyError:
        print("未找到环境变量 APPKEY，请检查配置。")
        return

    params = {
        "appkey": appkey,
        "title": title,
    }
    try:
        response = requests.get("https://cx.super4.cn/push_msg", params=params)
        if response.status_code == 200:
            print("消息发送成功")
        else:
            print(
                f"消息发送失败，状态码：{response.status_code}, 响应：{response.text}"
            )
    except Exception as e:
        print(f"发送消息时发生错误：{e}")


# 主程序
def main():
    """
    主程序逻辑，爬取汇率并根据条件发送通知。
    """
    combined_data = {}
    for url in URLS:
        data = scrape_exchange_rates(url, TARGET_CURRENCIES)
        combined_data.update(data)

    if not combined_data:
        print("未获取到任何汇率数据。")
        return

    print("获取到的汇率信息：")
    for currency, rate in combined_data.items():
        print(f"{currency}: {rate}")

    # 条件判断并发送消息
    try:
        euro_rate = float(combined_data.get("欧元", "1000"))
        sgd_rate = float(combined_data.get("新加坡元", "1000"))

        if euro_rate < 760:
            send_to_wechat(f"汇率提醒：欧元降至 {euro_rate}")
        time.sleep(0.5)  # 设置延迟防止发送消息过于频繁
        if sgd_rate < 539:
            send_to_wechat(f"汇率提醒：新加坡元降至 {sgd_rate}")
        time.sleep(0.5)  # 设置延迟防止发送消息过于频繁
        if datetime.now().hour >= 10:
            send_to_wechat(
                f"{datetime.now().year}年{datetime.now().month}月{datetime.now().day}日，新加坡元：{sgd_rate}，欧元：{euro_rate}"
            )
    except ValueError as e:
        print(f"解析汇率时出错：{e}")


if __name__ == "__main__":
    main()
