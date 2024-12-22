import requests
from bs4 import BeautifulSoup
import time
from datetime import datetime

# 定义目标URL
urls = [
    "https://www.boc.cn/sourcedb/whpj/index.html",
    "https://www.boc.cn/sourcedb/whpj/index_1.html",
]


# 创建一个函数来爬取数据
def scrape_exchange_rates(url, target_currencies):
    response = requests.get(url)
    response.encoding = "utf-8"  # 确保中文字符正确解码
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")
        # 定位表格
        table = soup.find_all("table")[1]
        if not table:
            print(f"No table found on {url}")
            return []

        rows = table.find_all("tr")
        data = {}
        for row in rows[1:]:  # 跳过表头
            cols = row.find_all("td")
            cols = [col.text.strip() for col in cols]
            # 筛选目标币种
            if cols and cols[0] in target_currencies:
                if cols[0] not in data:
                    data[cols[0]] = cols[3]
        return data
    else:
        print(f"Failed to fetch {url}, status code: {response.status_code}")
        return []


# 发送汇率信息到微信
def send_to_wechat(title):
    params = {
        "appkey": "482d185a324970fed1037e054416b735-wPQ7KTLd",
        "title": title,
    }
    response = requests.get("https://cx.super4.cn/push_msg", params=params)

    if response.status_code == 200:
        print("消息发送成功")
    else:
        print(f"消息发送失败，状态码：{response.status_code}, 响应：{response.text}")


# 主程序
def main():
    target_currencies = ["欧元", "新加坡元"]
    for url in urls:
        data = scrape_exchange_rates(url, target_currencies)

    # 打印结果
    if data:
        print("汇率信息：")
        for key, value in data.items():
            print(key, value)
    else:
        print("未获取到数据。")

    if float(data["欧元"]) < 760:
        send_to_wechat(f"汇率降价，欧元：{data['欧元']}")
    time.sleep(0.5)
    if float(data["新加坡元"]) < 540:
        send_to_wechat(f"汇率降价，新加坡元：{data['新加坡元']}")
    time.sleep(0.5)
    # 测试Github Actions
    send_to_wechat(
        f"{datetime.now()}，新加坡元：{data['新加坡元']}，欧元：{data['欧元']}"
    )
    if datetime.now().hour == 18:
        send_to_wechat(
            f"{datetime.now().year}年{datetime.now().month}月{datetime.now().day}日，新加坡元：{data['新加坡元']}，欧元：{data['欧元']}"
        )


if __name__ == "__main__":
    main()
