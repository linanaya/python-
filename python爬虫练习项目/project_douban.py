import requests,re,xlwt,pymysql
from bs4 import BeautifulSoup

# 执行主函数
def main():
    # 爬取网页的前缀
    url = "https://movie.douban.com/top250?start="
    data = get_data(url)  # 总数据列表

    savepath = "豆瓣电影250排行榜信息.xls"  # 保存路径
    # saveXls(data,savepath)  # 保存到xls表格

    saveMysql(data)  # 保存到MySQL数据库


# 构建规则变量
findLink = re.compile(r'<a href="(.*?)">')
findImg = re.compile(r'<img.*src="(.*?)"',re.S)
findTitle = re.compile(r'<span class="title">(.*?)</span>')
findInfo = re.compile(r'<p class="">(.*?)</p>',re.S)
findGrade = re.compile(r'<span class="rating_num" property="v:average">(.*)</span>')
findNum = re.compile(r'<span>(\d*)人评价</span>')
findInq = re.compile(r'<span class="inq">(.*?)</span>')



# 爬取网页并解析
def get_data(url):
    data_total = []  # 所有电影的信息
    for i in range(10):
        build_url = url + str(i*25)  # 构建将要爬取的网页
        head = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36"
        }  # 构建请求头，伪装成浏览器

        # 逐一解析
        response = requests.get(build_url,headers=head)
        html = response.text
        soup = BeautifulSoup(html,"html.parser")
        
        # 解析每个电影标签，并把需要的数据拿出来
        for item in soup.find_all("div",class_="item"):
            data_part = []  # 保存一部电影的信息
            item = str(item)

            # 利用规则，匹配数据
            link = re.findall(findLink,item)[0]  # 电影详情链接
            data_part.append(link)

            img = re.findall(findImg,item)[0]  # 电影海报图片
            data_part.append(img)

            title = re.findall(findTitle,item)  # 电影的名称
            if len(title) == 2:
                ctitle = title[0]
                wtitle = title[1].replace("/","")
                wtitle = wtitle.replace("'","\\'")  # 将字符串中含有"'"--单引号的加上转义\，防止数据库存储的时候遇到'li nan's things'这种问题
                wtitle = wtitle.strip()
                data_part.append(ctitle)
                data_part.append(wtitle)
            else:
                data_part.append(title[0])
                data_part.append(" ")

            info = re.findall(findInfo,item)[0]  # 电影的概括
            info = re.sub('<br(\s+)?/>(\s+)?'," ",info)
            info = info.replace("'","\\'")
            data_part.append(info.strip())

            grade = re.findall(findGrade,item)[0]  # 电影的评分
            data_part.append(grade)

            num = re.findall(findNum,item)[0]  # 电影评价的人数
            data_part.append(num)

            inq = re.findall(findInq,item)  # 电影的简介
            if len(inq) != 0:
                inq = inq[0].replace("。","")
                inq = inq.replace("'","\\'")
                data_part.append(inq)
            else:
                data_part.append(" ")
            
            # 将一部电影的信息添加到总数据
            data_total.append(data_part)
    
    return data_total


# xls保存功能
def saveXls(data,savepath):
    # 创建对象
    workbook = xlwt.Workbook(encoding="utf-8")
    worksheet = workbook.add_sheet("豆瓣电影排行")  # 工作表

    field = ["电影详情链接","电影图片","电影国内名称","电影国外名称","概况","评分","评价人数","简介"]  # 表格的第一行字段
    for i in range(8):
        worksheet.write(0,i,field[i])
    
    # 导入数据
    for i in range(250):
        print("导入第{}次".format(i+1))
        film = data[i]
        for j in range(8):
            worksheet.write(i+1,j,film[j])
    
    # 保存数据
    workbook.save(savepath)


# mysql保存功能
def saveMysql(data):
    db = pymysql.connect(host='localhost',user='root',password='123456789',port=3306,db='douban')  # 连接数据库
    cursor = db.cursor()  # 调用数据库对象的cursor方法，返回MySQL的操作游标

    # 导入数据
    for i in range(250):
        film = data[i]
        paramers = {
            'filmLink':"'"+film[0]+"'",
            'filmImg':"'"+film[1]+"'",
            'filmCtitle':"'"+film[2]+"'",
            'filmFtitle':"'"+film[3]+"'",
            'filmInfo':"'"+film[4]+"'",
            'filmGrade':"'"+film[5]+"'",
            'filmNum':"'"+film[6]+"'",
            'filmInq':"'"+film[7]+"'"
        }  # 构建sql语句的参数,!!! 给每个值加上单引号，sql语法--values参数要带引号

        keys = ",".join(paramers.keys())
        values = ",".join(paramers.values())

        sql = "insert into film_data({keys}) values({values})".format(keys=keys,values=values)

        try:
            cursor.execute(sql)
            db.commit()
            print(str(i+1)+" 导入成功")
        except:
            print(str(i+1)+" 导入失败")
            db.rollback()
    db.close()  # 切记要等数据全部存到数据库再关闭数据库


main()
print("导入完成！")