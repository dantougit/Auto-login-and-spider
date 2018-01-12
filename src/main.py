#!/usr/bin/env python
# -*- coding:UTF-8 -*-
"""author : haozhuolin
   date : 20170929
"""
import sys
import time
import re
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
import random
from spider import Spider

reload(sys)
sys.setdefaultencoding("utf-8")

class Robot(object):
    def __init__(self):
        self.driver = webdriver.Chrome()
        self.host = "https://www.huxiu.com"
        self.article_url = "/article"
        self.temp = "../data/temp4"
        self.driver.get(self.host)
        self.driver.maximize_window()
        self.spider = Spider()

    def login(self):
        #登录
        self.driver.find_element_by_class_name("js-login").click()
        time.sleep(2)
        #输入账号
        self.driver.find_element_by_id("login_username").send_keys("###")
        time.sleep(1)
        #输入密码
        self.driver.find_element_by_id("login_password").send_keys("###")
        time.sleep(1)
        #点击近十天自动登录
        self.driver.find_element_by_id("autologin").click()
        time.sleep(1)
        #点击登录
        self.driver.find_element_by_xpath("//div[@class='login-form username-box ']//button[@class='js-btn-login btn-login']").click()

    def click_move(self, element):
        ActionChains(self.driver).move_to_element(element).perform()

    def screen_move(self, element):
        self.driver.execute_script("arguments[0].scrollIntoView();", element)

    def screen_slide(self, num, speed):
        for i in range(num):
            self.driver.execute_script("window.scrollBy(0, %s)" % speed)
            time.sleep(0.01)

    def switch_window(self):
        self.driver.switch_to.window(self.driver.window_handles[-1])

    def personification(self):

        #主页滑动3次
        for i in range(4):
            time.sleep(random.uniform(1, 2))
            self.screen_slide(30, 20)

        #选一个文章进去
        elem = robot.driver.find_elements_by_xpath("//a[@class='transition msubstr-row2']")[5]
        self.click_move(elem)
        time.sleep(1)
        self.driver.execute_script("arguments[0].click();", elem)
        self.switch_window()

        #滑动10次
        for i in range(10):
            self.screen_slide(int(random.uniform(20, 40)), int(random.uniform(10, 30)))
            time.sleep(random.uniform(0.5, 2))

        #点赞
        try:
            time.sleep(1)
            elem = self.driver.find_element_by_xpath("//div[@class='neirong-shouquan']")
            self.screen_move(elem)
            time.sleep(1)
            elem = self.driver.find_element_by_xpath(
                "//div[@class='praise-box transition js-like-article center-box ']")
            self.driver.execute_script("arguments[0].click();", elem)
        except Exception as e:
            print e
        time.sleep(3)
        self.driver.close()

        #返回主页进入人工智能板块
        self.switch_window()
        time.sleep(1)
        elem = self.driver.find_element_by_xpath("//li[@class='nav-news js-show-menu']//a[@href='/']")
        self.click_move(elem)
        time.sleep(1)
        self.driver.find_element_by_css_selector("a[href='/channel/104.html']").click()
        self.switch_window()
        time.sleep(1)

        #滑动两次
        for i in range(3):
            time.sleep(random.uniform(0.5, 2))
            self.screen_slide(30, 20)

        time.sleep(3)

        #返回主页
        self.driver.close()
        self.switch_window()

    def replay(self, article_id, data_pid, data_uid, data_comment_dp_id, content):
        self.driver.get("%s/%s/%s" % (self.host, self.article_url, article_id))
        time.sleep(3)
        if data_pid == "":
            elem = self.driver.find_element_by_xpath("//textarea[@id='saytext']")
            click_elem = self.driver.find_element_by_xpath("//button[@class='btn btn-article js-comment-yh-submit transition ']")
            #self.screen_move(self.driver.find_element_by_xpath("//p[@id='comment-pl-position']"))
        elif data_uid == "" and data_comment_dp_id == "":
            self.driver.find_element_by_xpath("//div[@class='pl-box-wrap' and @data-pid='%s']//div[@class='btn-dp transition js-add-dp-box']" % data_pid).click()
            time.sleep(1)
            elem = self.driver.find_element_by_xpath("//div[@class='pl-box-wrap' and @data-pid='%s']//textarea[@class='form-control js-comment-yh-form-control']" % data_pid)
            click_elem = self.driver.find_element_by_xpath("//div[@class='pl-box-wrap' and @data-pid='%s']//button[@class='btn btn-article js-comment-yh-dp-submit']" % data_pid)
        else:
            self.driver.find_element_by_xpath("//div[@class='one-pl-content' and @data-uid='%s' and @data-comment-dp-id='%s']//div[@class='js-hf-article-pl hf-article-pl pull-right comment-yh-dp-relpyTA']" % (data_uid, data_comment_dp_id)).click()
            time.sleep(1)
            elem = self.driver.find_element_by_xpath("//div[@class='one-pl-content' and @data-uid='%s' and @data-comment-dp-id='%s']//textarea[@class='form-control']" % (data_uid, data_comment_dp_id))
            click_elem = self.driver.find_element_by_xpath("//div[@class='one-pl-content' and @data-uid='%s' and @data-comment-dp-id='%s']//button[@class='btn btn-article js-comment-yh-hf-dp']" % (data_uid, data_comment_dp_id))

        elem.click()
        time.sleep(2)
        elem.send_keys(content)
        time.sleep(2)
        self.screen_slide(5, 20)
        time.sleep(2)
        click_elem.click()
        time.sleep(5)
        self.driver.get(self.host)

    def model(self):
        article_ids = set()
        reg_rep = {}
        with open(self.temp) as fi:
            for line in fi:
                arr = line.decode("utf-8").strip().split("\t")
                if len(arr) == 2:
                    self.replay(arr[0], "", "", "", arr[1])
                    time.sleep(30)
                else:
                    reg_rep[re.compile(arr[1])] = arr[2]
                    article_ids.add(arr[0])
        while len(reg_rep):
            for article_id in article_ids:
                for arr in self.spider.get_comment(article_id, 1) + self.spider.get_comment(article_id, 2):
                    cp = reg_rep.copy()
                    for reg, rep in cp.iteritems():
                        print arr[-1], reg.pattern
                        if reg.search(arr[3]):
                            del reg_rep[reg]
                            robot.replay(article_id, arr[0], arr[1], arr[2], rep)
                            time.sleep(30)
                    time.sleep(3)

if __name__ == "__main__":

    robot = Robot()
    robot.login()
    time.sleep(2)
    robot.personification()
    time.sleep(5)
    robot.model()