#!/usr/bin/env python
# -*- coding:UTF-8 -*-
"""author : haozhuolin
   date : 20170929
"""
import sys
import time
import re
import urllib
import urllib2
import json
import hashlib
from lxml import etree


reload(sys)
sys.setdefaultencoding("utf-8")

class Spider(object):

    def __init__(self):
        self.base_url = "https://www.huxiu.com"
        self.article_url = "/v2_action/article_list"
        self.comment_url = "/comment/getCommentList"
        self.content_url = "/article"
        self.article_id_pattern = re.compile("[0-9]+")
        self.comment_file = "../data/comment"
        self.content_file = "../data/content"
        self.articles = set()
        self.comments = set()
        self.load_articles()

    def load_articles(self):
        with open(self.content_file, "r") as fi:
            for line in fi:
                self.articles.add(line.strip().split("\t")[0])
        with open(self.comment_file, "r") as fi:
            for line in fi:
                self.comments.add("\t".join(line.strip().split("\t")[0:3]))

    def request(self, url, data=None, headers=None):
        data = data if data else {}
        headers = headers if headers else {}
        for i in range(5):
            try:
                conn = urllib2.urlopen(urllib2.Request(url, data = urllib.urlencode(data), headers = headers))
                content = conn.read()
                conn.close()
                return content
            except Exception as e:
                time.sleep(0.2)
                print e
        return None

    def get_article(self):
        res = set()
        #主页article
        content = self.request(self.base_url)
        if content:
            html = etree.HTML(content)
            for tag in html.xpath("//*[starts-with(@href,'/article')]"):
                res.add(self.article_id_pattern.findall(tag.get("href"))[0])

        for i in range(1, 10):
            data = {"huxiu_hash_code": hashlib.sha1(str(time.time())).hexdigest(),
                    "page": "%s" % i,
                    "last_dateline": 0}

            content = self.request(url=self.base_url + self.article_url, data=data)
            if content:
                content = json.loads(content)
                if content['msg'] == "获取成功":
                    html = etree.HTML(content['data'])
                    for tag in html.xpath("//div[@class='mod-b mod-art']//div[@class='mob-ctt']/h2/a"):
                        res.add(self.article_id_pattern.findall(tag.get("href"))[0])
                else:
                    break
            else:
                break
            time.sleep(0.2)
        return res


    def get_comment(self, object_id, type):
        res = []
        data = {"object_type": 1,
                "object_id": object_id,
                "type": type}
        content = self.request(url=self.base_url + self.comment_url, data=data)
        if content:
            content = json.loads(content)
            if content['success']:
                html = etree.HTML(content['data']['data'])
                for tag in html.xpath("//div[@class='pl-wrap pl-yh-wrap']//div[@class='pl-box-wrap']"):
                    data_pid = tag.get("data-pid")
                    html1 = etree.HTML(etree.tostring(tag))
                    comment = "。".join(html1.xpath(\
                        "//div[@class='pl-content pl-yh-content']/div[@class='pull-left ']/text()"))
                    res.append([data_pid, '', '', comment.replace("\t", "").replace("\n", "")])
                    for tag1 in html1.xpath("//div[@class='dp-box']//div[@class='one-pl-content']"):
                        data_uid = tag1.get("data-uid")
                        data_comment_dp_id = tag1.get("data-comment-dp-id")
                        html2 = etree.HTML(etree.tostring(tag1))
                        sub_comment = "。".join(html2.xpath(\
                            "//div[@class='content comment-dp-box-cont']//div[@class='author-content']/text()"\
                            )).strip()
                        res.append([data_pid, data_uid, data_comment_dp_id, sub_comment.replace("\t", "").replace("\n", "")])
        return res

    def get_content(self, object_id):
        content = self.request(url="%s%s/%s.html" % (self.base_url, self.content_url, object_id))
        if content:
            html = etree.HTML(content)
            return "。".join([text.strip() for text in html.xpath("//div[@class='article-content-wrap']//text()") if text.strip()])

    def main(self):

        while(True):
            content_fw = open(self.content_file, "a+")
            comment_fw = open(self.comment_file, "a+")
            for article_id in self.get_article():
                print article_id + "\t" + str(time.time())
                if article_id not in self.articles:
                    content = self.get_content(article_id)
                    content_fw.write("%s\t%s\n" % (article_id, content.replace("\t", "").replace("\n", "")))
                    content_fw.flush()
                    self.articles.add(article_id)
                for comment in self.get_comment(article_id, 1) + self.get_comment(article_id, 2):
                    key = "%s\t%s\t%s" % (article_id, comment[0], comment[1])
                    print comment[-1]
                    if key not in self.comments:
                        comment_fw.write("%s\t%s\n" % (article_id, "\t".join(comment)))
                        comment_fw.flush()
                        self.comments.add(key)
                time.sleep(0.2)
            time.sleep(10)

            comment_fw.close()
            content_fw.close()

if __name__ == "__main__":
    spider = Spider()
    spider.main()