#!/usr/bin/python
# -*- coding:utf-8 -*-

import urllib2
import re
import MySQLdb
import os
import shutil


def insert_all_price():
    url = 'https://www.hexonet.net/js/prices.json?_=1461911040270'
    request = urllib2.Request(url)
    response = urllib2.urlopen(request)
    content = response.read().decode('utf-8')
    pattern = re.compile('\[\"(\.[a-z]+ )","(.*?)","(.*?)","(.*?)","(.*?)", \
                          "(.*?)","(.*?)","(.*?)","(.*?)","(.*?)","(.*?)", \
                          "(.*?)","(.*?)","(.*?)","(.*?)"\]', re.S)
    items = re.findall(pattern, content)
    cur.execute("truncate table All_Price")
    for item in items:
        if item[13] == "USD":
            sql = ("insert into All_Price values \
                  (\"%s\",\"%s\",\"%s\",\"%s\",\"%s\")"
                   % (item[0], item[1], item[2],
                      item[3], item[13]))
            cur.execute(sql)
        else:
            sql = ("insert into All_Price values \
                   (\"%s\",\"%s\",\"%s\",\"%s\",\"%s\")"
                   % (item[0], item[7], item[8], item[9], item[13]))
            cur.execute(sql)


def insert_all_promotion_price():
    page = 1
    url = 'https://www.hexonet.net/js/promotions.json?_=1461716466659' \
          + str(page)
    request = urllib2.Request(url)
    response = urllib2.urlopen(request)
    content = response.read().decode('utf-8')
    pattern = re.compile('.*?(\.[a-z]+ ).*?\'(promoPrice|notApplicable)\' \
                          >(.*?)</span>.*?\'(promoPrice|notApplicable)\' \
                          >(.*?)</span>.*?\'(promoPrice|notApplicable)\' \
                          >(.*?)</span>.*?\'(promoPrice|notApplicable)\' \
                          >(.*?)</span>.*?\'(promoPrice|notApplicable)\' \
                          >(.*?)</span>.*?\'(promoPrice|notApplicable)\' \
                          >(.*?)</span>.*?\'(promoPrice|notApplicable)\' \
                          >(.*?)</span>.*?\'(promoPrice|notApplicable)\' \
                          >(.*?)</span>.*?\'(promoPrice|notApplicable)\' \
                          >(.*?)</span>.*?\'(promoPrice|notApplicable)\' \
                          >(.*?)</span>.*?\'(promoPrice|notApplicable)\' \
                          >(.*?)</span>.*?\'(promoPrice|notApplicable)\' \
                          >(.*?)</span>.*?(USD|CNY|EUR).*?]', re.S)
    items = re.findall(pattern, content)
    cur.execute("truncate table All_promotion_Price")
    for item in items:
        if item[25] == 'USD':
            sql = ("insert into All_promotion_Price values \
                    (\"%s\",\"%s\",\"%s\",\"%s\",\"%s\")"
                   % (item[0], item[2], item[10], item[18], item[25]))
            cur.execute(sql)
        else:
            sql = ("insert into All_promotion_Price values \
                   (\"%s\",\"%s\",\"%s\",\"%s\",\"%s\")"
                   % (item[0], item[6], item[14], item[22], item[25]))
            cur.execute(sql)


# 查询是数据库列表中
def Promotion_Price(table, domain_name):
    cur = conn.cursor()
    sql = ("select * from %s where domain_name = \" \
            %s\" " % (table, domain_name))
    num = cur.execute(sql)
    rs = cur.fetchall()
    if num == 1:
        return rs
    elif num == 0:
        return num
    else:
        return False


def Change_Database(domain_name, Databases_table):
    Delete_Sql = ("delete from Last_Domain_Price where domain_name = \" \
                   %s \"" % domain_name)
    content = cur.fetchall()
    pattern = re.findall('.*?u\'(.*?)\'', '%s' % (content))
    Insert_Sql = ("insert into Last_Domain_Price values \
                  (\"%s\",\"%s\",\"%s\",\"%s\",\"%s\")"
                  % (pattern[0], pattern[1], pattern[2],
                     pattern[3], pattern[4]))
    cur.execute(Delete_Sql)
    cur.execute(Insert_Sql)


def write_file(content):
    w = file("domain_price", "a+")
    price = ("%s\n" % (content))
    w.writelines(price)
    w.close()


conn = MySQLdb.connect(
        host='10.0.5.106',
        port=3306,
        user='test',
        passwd='test',
        db='python',
        charset='utf8'
)


cur = conn.cursor()
print "exec insert_all_price"
# insert_all_price()

print "exec insert_all_promotion_price"
# insert_all_promotion_price()

print "find domain price"
f = open("domain_list", "r")
while True:
    line = f.readline()
    if line:
        line = line.strip()
        old_price = Promotion_Price("Last_Domain_Price", line)
        old_pattern = re.findall('.*?u\'(.*?)\'', '%s' % (old_price))
        if Promotion_Price("All_promotion_Price", line) is False:
            if Promotion_Price("All_Price", line) is False:
                # 所有列表都没有
                write_file("domain %s is not found" % line)
            # 原价与总价不同
            elif Promotion_Price("All_Price", line) \
                    != Promotion_Price("Last_Domain_Price", line):
                # 新增域名并且该域名在原价中
                if Promotion_Price("Last_Domain_Price", line) == 0:
                    Change_Database(line, "All_Price")
                    continue
                new_price = Promotion_Price("All_Price", line)
                new_pattern = re.findall('.*?u\'(.*?)\'', '%s' % (new_price))
                write_file("%s 原价: New Registrations = %s, \
                            Renewals = %s, Transfers = %s"
                           % (line, old_pattern[1],
                               old_pattern[2], old_pattern[3]))
                write_file("%s 现价: New Registrations = %s，\
                            Renewals = %s, Transfers = %s"
                           % (line, new_pattern[1],
                               new_pattern[2], new_pattern[3]))
                Change_Database(line, "All_Price")
        else:
            # 原价与特价不同
            if Promotion_Price("Last_Domain_Price", line) != \
               Promotion_Price("All_promotion_Price", line):
                if Promotion_Price("Last_Domain_Price", line) == 0:
                    Change_Database(line, "All_promotion_Price")
                    continue
                else:
                    new_price = Promotion_Price("All_promotion_Price", line)
                    new_pattern = re.findall('.*?u\'(.*?)\'',
                                             '%s' % (new_price))
                    write_file("%s 原价: New Registrations = %s \
                               ，Renewals = %s, Transfers = %s"
                               % (line, old_pattern[1],
                                  old_pattern[2], old_pattern[3]))
                    write_file("%s 现价: New Registrations = %s，\
                               Renewals = %s, Transfers = %s"
                               % (line, new_pattern[1],
                                  new_pattern[2], new_pattern[3]))
                    Change_Database(line, "All_promotion_Price")
    else:
        break
f.close()
cur.close
conn.close()

if os.path.exists("domain_price"):
    os.system('cat domain_price \
              |mail -s "您关注域名价格发生改变" xxx@xxx.com')
    shutil.move('domain_price', 'domain_price.last')
