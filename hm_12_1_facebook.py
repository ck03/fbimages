from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
import time
import json
import requests
import os


class FbSpider:
    def __init__(self, name, url):
        chrome_options = Options()
        # 沒有這一行會自動開啟瀏覽器
        chrome_options.add_argument("--headless")
        self.driver = webdriver.Chrome(chrome_options=chrome_options,
                                       executable_path=r'D:\Study\Python2\chromedriver\chromedriver.exe')
        self.start_url = url
        self.headers = {"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36"}
        self.result_list = []
        self.result_dict = {}
        self.name = name

    def get_content_list(self):
        print(self.driver.current_url)
        time.sleep(3)
        while True:
            wait = WebDriverWait(self.driver, 2)

            if len(self.driver.find_elements_by_xpath("//div[@id='content_container']/div/div[@class='_2pie']/div[@class='_2piq']/div[@class='_2pie']/div/div[2]/div[@class='_2eec']/div")) == 0:
                print("1")
                # # # VIP，内容加载完成后爬取
                wait.until(
                    lambda driver: self.driver.find_elements_by_xpath("//div[@id='content_container']/div/div[@class='_2pie']/div[@class='_4-u2 _4784 _2y_h _4-u8']/div/div[2]/div[@class='_2eec']/div"))
                div_list = self.driver.find_elements_by_xpath("//div[@id='content_container']/div/div[@class='_2pie']/div[@class='_4-u2 _4784 _2y_h _4-u8']/div/div[2]/div[@class='_2eec']/div")
                downloading = self.driver.find_elements_by_xpath("//div[@id='content_container']/div/div[@class='_2pie']/div[@class='_4-u2 _4784 _2y_h _4-u8']/div/div[2]/div[@class='_3fv0']/div/span")
                print("lod1=", len(downloading))
            else:
                print("2")
                # # # VIP，内容加载完成后爬取
                wait.until(
                    lambda driver: self.driver.find_elements_by_xpath("//div[@id='content_container']/div/div[@class='_2pie']/div[@class='_2piq']/div[@class='_2pie']/div/div[2]/div[@class='_2eec']/div"))
                div_list = self.driver.find_elements_by_xpath("//div[@id='content_container']/div/div[@class='_2pie']/div[@class='_2piq']/div[@class='_2pie']/div/div[2]/div[@class='_2eec']/div")
                #  用find_element(s)方法判断元素是否存在 ,判斷元素是否存在elements 要加 s
                downloading = self.driver.find_elements_by_xpath("//div[@id='content_container']/div/div[@class='_2pie']/div[@class='_2piq']/div[@class='_2pie']/div/div[2]/div[@class='_3fv0']/div/span")
                print("lod2=", len(downloading))

            if len(downloading) != 0:
                # 拖動到可见的元素去, 因為它是滾動頁面往下,所以此動作是在模擬頁面往下移到目前最後一個元素,代表頁面在滾動
                self.driver.execute_script('arguments[0].scrollIntoView();', div_list[-1])
                time.sleep(5)
            else:
                print("已經全部加載完畢....")
                for div in div_list:
                    item = {}
                    item["imghrefB"] = div.find_element_by_xpath("./a").get_attribute("href")
                    item["imgS"] = div.find_element_by_xpath("./a/img").get_attribute("src")
                    item["id"] = div.find_element_by_xpath(".").get_attribute("id")
                    # item["hot"] = div.find_element_by_xpath("./div[@class='_3x2f']/div[@class='_3t_i']/div/div/div[@class='_ohf rfloat']/div/a[1]").text  # if len(div.find_elements_by_xpath("./div[@class='_3x2f']/div[@class='_3t_i']/div/div/div[@class='_ohf rfloat']/div/a[1]")) > 0 else None
                    # item["msg"] = div.find_element_by_xpath("./div[@class='_3x2f']/div[@class='_3t_i']/div/div/div[@class='_ohf rfloat']/div/a[2]").text  # if len(div.find_elements_by_xpath("./div[@class='_3x2f']/div[@class='_3t_i']/div/div/div[@class='_ohf rfloat']/div/a[2]")) > 0 else None

                    # print(item)
                    self.result_list.append(item)
                break

            print(len(div_list))

    # 獲取更大尺寸圖片的連結
    def get_real_img(self, url, sid, folder_path):
        self.driver.get(url)
        # print(self.driver.page_source)
        url = self.driver.find_element_by_xpath("//head/meta[7]").get_attribute("content")

        res = requests.get(url)
        # 下載圖片到本地去
        with open(folder_path + "{}_{}.jpg".format(self.name, sid), "wb") as f:
            f.write(res.content)
        # 回傳url因為是後來才取得到的大尺寸圖片的url所以要insert到item去
        return url

    def run(self):  # 主要實現邏輯
        print("fbimg爬蟲開始.....")
        # 1.取得url
        self.driver.get(self.start_url)
        # 2.獲取響應,取得資料
        self.get_content_list()

        folder_path = "fb_{}/".format(self.name)
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

        icount = len(self.result_list)
        print("開始下載圖片....")
        # 3.歷遍,下一頁,滾動
        for img in self.result_list:
            imgurl = img["imghrefB"] + "&theater"
            sid = img["id"]
            imgB = self.get_real_img(imgurl, sid, folder_path)
            img["imgB"] = imgB
            icount -= 1
            if icount % 30 == 0:
                if icount != 0:
                    print("還剩{}張".format(icount))
                else:
                    print("下載完畢...")
        # print(self.result_list)

        # 4.保存
        self.result_dict["result"] = self.result_list
        with open("{}_img.json".format(self.name), "w", encoding="utf-8") as f:
            f.write(json.dumps(self.result_dict, ensure_ascii=False, indent=2))

        self.driver.close()
        self.driver.quit()
        print("fbimg爬蟲結束.....")


if __name__ == "__main__":
    """
        name: 名稱比如:人名
        url:  下載的網址
    """
    fbspider = FbSpider("name", "url")
    fbspider.run()