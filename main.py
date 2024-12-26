import json
import time
import requests
import execjs
import csv
from datetime import datetime


def save_json_to_txt(file_path, data):
    """
    将 JSON 数据追加写入文本文件，每行一个 JSON 对象。

    :param file_path: 保存的文件路径
    :param data: 要保存的 JSON 数据（字典格式）
    """
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json_line = json.dumps(data, ensure_ascii=False)
            f.write(json_line + '\n')
    except IOError as e:
        print(f"文件写入错误: {e}")


if __name__ == '__main__':
    stat_year = 2024  # 只看2024年的

    offset = '0'
    with open('config.json', 'r') as f:
        config = json.load(f)
    cookies = config['cookies']
    pdduid = config['pdduid']

    order_list = []
    while True:
        anti_content = execjs.compile(open('hello.js', 'r', encoding='utf-8').read()).call('dt')
        # print(anti_content)

        params = {
            'pdduid': pdduid,
        }
        headers = {
            'accept': 'application/json, text/plain, */*',
            'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'cache-control': 'no-cache',
            'content-type': 'application/json;charset=UTF-8',
            'origin': 'https://mobile.pinduoduo.com',
            'pragma': 'no-cache',
            'priority': 'u=1, i',
            'referer': 'https://mobile.pinduoduo.com/orders.html?type=0&comment_tab=1&combine_orders=1&main_orders=1&refer_page_name=login&refer_page_id=10169_1730154038757_91fnav6ik9&refer_page_sn=10169&page_id=10032_1729549301932_hai9b5qifq&order_index=30&is_back=1',
            'sec-ch-ua': '"Chromium";v="130", "Google Chrome";v="130", "Not?A_Brand";v="99"',
            'sec-ch-ua-mobile': '?1',
            'sec-ch-ua-platform': '"Android"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Mobile Safari/537.36',
        }
        json_data = {
            'type': 'all',
            'page': 1,
            'origin_host_name': 'mobile.pinduoduo.com',
            'scene': 'order_list_h5',
            'page_from': 0,
            'anti_content': anti_content,
            'size': 10,
            'offset': offset,
        }

        response = requests.post(
            'https://mobile.pinduoduo.com/proxy/api/api/aristotle/order_list_v4',
            params=params,
            cookies=cookies,
            headers=headers,
            json=json_data,
        )

        resp_json = response.json()
        # print(resp_json)
        print(str(json.dumps(resp_json)))
        orders = resp_json.get("orders", [])
        if len(orders) == 0:
            print("----------END---------")
            break
        for order in orders:
            save_json_to_txt('pdd_order.txt', order)
            order_list.append(order)

        last_order = orders[-1]
        offset = last_order.get("offset", "")
        order_time = order.get('order_time', 0)  # 下单时间 10位时间戳
        order_datetime = datetime.fromtimestamp(order_time)
        if order_datetime.year != stat_year:
            break

        time.sleep(5.2)  # 随机延迟避免反爬

    # 订单解析
    order_parse_data = []
    for order in order_list:
        order_type = order.get('type', 1)  # 订单类型

        if order_type == 1:
            order_time = order.get('order_time', 0)  # 下单时间 10位时间戳
            order_amount = order.get('order_amount', 0)  # 订单金额（实付）单位：分
            order_goods = order.get('order_goods', [])
            if len(order_goods) == 1:
                order_good = order_goods[0]
                goods_name = order_good.get('goods_name', '')  # 商品名称
                spec = order_good.get('spec', '')  # 规格
                goods_price = order_good.get('goods_price', 0)  # 商品价格 单位：分
                goods_number = order_good.get('goods_number', 0)  # 商品数量
                thumb_url = order_good.get('thumb_url', '')  # 商品图片
                order_datetime = datetime.fromtimestamp(order_time)
                print(goods_name, spec, order_amount, goods_price, goods_number, thumb_url, order_time, order_datetime)
                if order_datetime.year != stat_year:
                    break
                order_parse_data.append([goods_name, spec, order_amount, goods_price, goods_number, thumb_url, order_time, order_datetime, 1])
            else:
                print(order)
        elif order_type == 2:  # 包含多个商品
            orders = order.get('orders', [])
            order_time = order.get('group_order', {}).get('success_time', 0)  # 下单时间 10位时间戳
            order_datetime = datetime.fromtimestamp(order_time)
            if order_datetime.year != stat_year:
                break
            order_amount = order.get('display_amount', 0)  # 订单金额（实付）单位：分
            spec_list = []
            goods_name_list = []
            goods_number_list = []
            goods_price_list = []
            thumb_url_list = []

            if len(orders) == 0:
                print(order)
            for order_detail in orders:
                order_goods = order_detail.get('order_goods', [])
                if len(order_goods) == 1:
                    order_good = order_goods[0]
                    goods_name = order_good.get('goods_name', '')  # 商品名称
                    goods_name_list.append(goods_name)
                    spec = order_good.get('spec', '')  # 规格
                    spec_list.append(spec)
                    goods_price = order_good.get('goods_price', 0)  # 商品价格 单位：分
                    goods_price_list.append(goods_price)
                    goods_number = order_good.get('goods_number', 0)  # 商品数量
                    goods_number_list.append(goods_number)
                    thumb_url = order_good.get('thumb_url', '')  # 商品图片
                    thumb_url_list.append(thumb_url)
                    print(goods_name, spec, order_amount, goods_price, thumb_url, goods_number, order_time, order_datetime)
                else:
                    print(order)
            order_parse_data.append([
                '\n'.join(goods_name_list),
                '\n'.join(spec_list),
                order_amount,
                '\n'.join(map(str, goods_price_list)),
                '\n'.join(map(str, goods_number_list)),
                '\n'.join(thumb_url_list),
                order_time,
                order_datetime,
                len(goods_name_list)  # 商品种类
            ])

    # 保存csv
    with open('output.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(order_parse_data)

    # 统计
    order_amount_sum = sum(order_parse_data[i][2] for i in range(len(order_parse_data)))
    order_goods_number_sum = sum(order_parse_data[i][-1] for i in range(len(order_parse_data)))
    print("2024年拼多多年度账单：")
    print("订单总金额：", order_amount_sum/100)
    print("订单总数：", len(order_parse_data))
    print("订单商品种类数：", order_goods_number_sum)
