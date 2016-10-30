import re
import requests
import json
import time
from PIL import Image

headers = {
           'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36'
           }
session = requests.Session()

def get_xsrf():
    """
    获取_xrsf
    """
    response = session.get('https://www.zhihu.com', headers=headers)
    html = response.text
    pattern = re.compile(r'<input type="hidden" name="_xsrf" value="(.*?)"/>')
    _xsrf = re.findall(pattern, html)
    return _xsrf[0]

def get_captcha():
    """
    获取验证码
    """
    t = int(time.time() * 1000)
    # 知乎网页版登录界面有时出现的是点击倒立中文字的验证模式
    # 请求URL是在 type=login 后面加上 &lang=cn 参数
    # 这里强制请求输入字母类型的验证码，就不涉及到点击了
    captcha_url = 'http://www.zhihu.com/captcha.gif?r=%s&type=login' % t
    response = session.get(captcha_url, headers=headers)
    with open('captcha.jpg', 'wb') as f:
        f.write(response.content)
        f.close()
    image = Image.open('captcha.jpg')
    image.show()
    captcha = input('请输入验证码：')
    return captcha

def login(username, password):
    """
    登录知乎
    """
    form_data = {'_xsrf' : get_xsrf(),
                 'password' : password,
                 'remember_me' : 'true',
                 'email' : username
                 }
    email_login_url = 'https://www.zhihu.com/login/email'
    result = session.post(email_login_url, data=form_data, headers=headers)
    # 根据返回值判断登录是否成功（成功 r 为 0，不成功 r 为 1）
    if json.loads(result.text)['r'] == 0:
        test_login()
    else:
        form_data['captcha'] = get_captcha()
        response = session.post(email_login_url, data=form_data, headers=headers)
        while json.loads(response.text)['r'] == 1:
            print('验证码错误！')
            form_data['captcha'] = get_captcha()
            response = session.post(email_login_url, data=form_data, headers=headers)
        test_login()

def test_login():
    """
    测试是否登录成功，并显示欢迎词
    此函数非必须
    """
    url = "https://www.zhihu.com/"
    response = session.get(url, headers=headers, allow_redirects=False)
    html = response.text
    pattern = re.compile(r'<span\sclass="name">(.*)</span>')
    name = re.findall(pattern, html)[0]
    print('%s , Welcome back to Zhihu!' % name)
    print()
    print('首页内容标题：')
    pattern2 = re.compile(r'<a\sclass="question_link"\shref="/question/[0-9]{1,}#answer-[0-9]{1,}"\starget="_blank"\sdata-id="[0-9]{1,}">\n(.*)\n</a>')
    question = re.findall(pattern2, html)
    for title in question:
        print(title)

if __name__ == '__main__':
    username = input('请输入邮箱：')
    password = input('请输入密码：')
    login(username, password)
