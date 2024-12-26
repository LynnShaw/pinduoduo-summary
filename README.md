# pinduoduo-summary
拼多多年度账单


1. PC登录拼多多网页版 https://mobile.pinduoduo.com/
2. 打开订单页，在控制台找到 https://mobile.pinduoduo.com/proxy/api/api/aristotle/order_list_v4?pdduid=xxx 的请求
将cookie 和 pdduid放入config.json 中，格式
```
{
    "cookies": {
        "pdd_user_id": "1234",
        "pdd_user_uin": "xxx",
        "rec_list_personal": "xxx",
        "pdd_vds": "xxx",
        "JSESSIONID": "xxx"
    },
    "pdduid": "8469838080"
}
    },
    "pdduid": "1234567"
}
```
3. 运行代码。原始json会存入pdd_order.txt文件，数据提取后的csv会存入output.csv。同时输出
```
2024年拼多多年度账单：
订单总金额： 20036
订单总数： 10
订单商品种类数： 14
```

默认只运行2024年的订单，要看其他年份修改代码中的stat_year
