import httpx, os
from bs4 import BeautifulSoup
from datetime import datetime

# 百变小樱
class bbxy:
    def __init__(self):
        self.client = None
        self.headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64) AppleWebKit/537.36 (KHTML, like Gecko) "
                                      "Chrome/78.0.3904.108 Safari/537.36"}
        self.timeout = httpx.Timeout(15)
        # 检查是否需要登录
        if not self.check_status():
            self.login()

    def login(self):
        # 创建client对象
        self.client = httpx.Client()
        url = "https://bbxy.shop/auth/login"
        # 设置JSON数据
        json = {"email": os.environ["SCA"], "passwd": os.environ["SCP"], "remember_me": 'off', "code": ''}
        # 发送POST请求
        response = self.client.post(url, headers=self.headers, json=json, timeout=self.timeout)

    def query_all(self):
        html = self.client.get("https://bbxy.shop/user")
        soup = BeautifulSoup(html, 'html.parser')
        # [剩余流量, 今日已用, 历史已用]
        queryResult = [i.text.strip() for i in soup.find_all('div', class_="product-result")]
        # 过期时间
        overTime = soup.find('h5').text.replace("到期时间：", "")
        formatOverTime = datetime.strptime(overTime, "%Y-%m-%d %H:%M:%S")
        distanceTime = (formatOverTime - datetime.now()).days
        return f"历史已用: {queryResult[2]}\n今日已用: {queryResult[1]}\n剩余流量: {queryResult[0]}\n距离到期时间还有{distanceTime}天"

    # 普通查询
    def query(self):
        b = self.query_all()
        return "--百变小樱--\n" + b

    # 签到，返回成功或失败的信息
    def sign(self):
        # 签到 url
        url = "https://bbxy.shop/user/checkin"
        # 签到操作, 将返回的结果转换为 json 格式
        response = self.client.post(url, headers=self.headers, timeout=self.timeout).json()
        # 签到完之后顺便查询一下流量
        q = self.query_all()
        # 构造消息
        msg = "--百变小樱--\n"
        if response['ret']:
            msg += f"签到成功,{response['msg']}\n" + self.query_all()
        else:
            msg += f"签到失败, {response['msg']}"
        return msg

    # 检测登录状态
    def check_status(self):
        # 如果client为空，说明还没有登录
        if self.client is None:
            return False
        # 如果client不为空，检查访问主页的状态码是否为200
        response = self.client.get("https://bbxy.shop/user")
        return response.status_code == 200


if __name__ == '__main__':
    print("任务开始...")
    B = bbxy()
    print(B.sign())