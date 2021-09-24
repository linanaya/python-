import requests,xlwt,re
from bs4 import BeautifulSoup

# 主函数
def main():
    url = "http://maoyan.com/board/4?offset="
    data = getDate(url)  # 接收电影信息总数据
    print(len(data))
    savepath = "猫眼电影排行信息.xls"
    saveXls(data,savepath)



# 构建规则
findLink = re.compile(r'<a class="image-link".*href="(.*?)"')
findImg = re.compile(r'<img .* class="board-img" data-src="(.*?)"/>',re.S)
findTitle = re.compile(r'<p class="name"><a .*>(.*?)</a></p>')
findStar = re.compile(r'<p class="star">(.*?)</p>',re.S)
findTime = re.compile(r'<p class="releasetime">上映时间：(.*?)</p>')


# 爬取网页
def getHtml(url):
    html = ""
    head = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36"
    }  # 构建请求头，伪装成浏览器
    try:
        response = requests.get(url,headers=head)
        html = response.text
    except Exception as e:
        print(e)
    
    return html


# 解析网页，返回数据
def getDate(url):
    data_total = []  # 所有电影的信息
    for i in range(10):
        build_url = url + str(i*10)
        html = getHtml(build_url)
        soup = BeautifulSoup(html,"html.parser")  # 初始化网页，用于解析

        # 逐一解析
        for item in soup.find_all("dd"):
            data_part = []  # 保存一部电影的信息
            item = str(item)

            link = "https://maoyan.com"+re.findall(findLink,item)[0]
            data_part.append(link)
            img = re.findall(findImg,item)[0]
            data_part.append(img)
            title = re.findall(findTitle,item)[0]
            data_part.append(title)
            star = re.findall(findStar,item)[0]
            data_part.append(star.strip())  # 去掉前后空格
            time = re.findall(findTime,item)[0]
            data_part.append(time)

            # 将电影保存到总数据列表里面
            data_total.append(data_part)

    return data_total


# xls保存
def saveXls(data,savepath):
    # 创建对象
    table = xlwt.Workbook(encoding="utf-8")
    sheet = table.add_sheet("猫眼电影排行")  # 工作表

    # 固定字段名
    field = ['电影详情链接','电影图片','电影名称','演员','上映时间']
    for i in range(5):
        sheet.write(0,i,field[i])
    
    # 添加数据
    for i in range(len(data)):
        print("导入第{}次".format(i+1))
        film = data[i]
        for j in range(5):
            sheet.write(i+1,j,film[j])
    
    # 保存表格
    table.save(savepath)

# 执行
main()
print("导入完成！")