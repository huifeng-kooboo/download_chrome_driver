import json
import subprocess
import shutil
import os
import time
import zipfile

import requests
from webdriver_manager.core.os_manager import OperationSystemManager
from webdriver_manager.chrome import ChromeDriverManager, ChromeType

__all__ = {
    'download_suit_chrome_driver'
}

# 记录固定数据
chrome_json_file = 'chrome_version.json'
chrome_zip = 'chrome_driver.zip'


def format_float(num):
    return '{:.2f}'.format(num)


def download_file(name, url):
    '''
    :param name:下载保存的名称
    :param url: 下载链接
    :return:
    '''
    headers = {'Proxy-Connection': 'keep-alive'}
    r = requests.get(url, stream=True, headers=headers)
    length = float(r.headers['content-length'])
    f = open(name, 'wb')
    count = 0
    count_tmp = 0
    time1 = time.time()
    for chunk in r.iter_content(chunk_size=512):
        if chunk:
            f.write(chunk)
            count += len(chunk)
            if time.time() - time1 > 2:
                p = count / length * 100
                speed = (count - count_tmp) / 1024 / 1024 / 2
                count_tmp = count
                print(name + ': ' + format_float(p) + '%' + ' Speed: ' + format_float(speed) + 'M/S')
                time1 = time.time()
    f.close()


def install_chrome_driver():
    """
    安装chrome浏览器
    """
    try:
        p = ChromeDriverManager(chrome_type=ChromeType.CHROMIUM).install()
        os.environ['CHROME_DRIVER_PATH'] = p
    except Exception as e:
        print("error")


def get_chromedriver_version(chromedriver_path="chromedriver.exe"):
    """
    获取chrome_driver版本
    Args:
        chromedriver_path:

    Returns:

    """
    try:
        # 运行Chromedriver，并通过命令行参数获取版本信息
        result = subprocess.run([chromedriver_path, '--version'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        if result.returncode == 0:
            # 如果成功执行，解析版本信息
            version = result.stdout.strip()
            version_list = str(version).split(" ")
            if len(version_list) == 3:
                version = version_list[1]
            return True, version
        else:
            # 如果执行失败，输出错误信息
            error_message = result.stderr.strip()
            return False, f"Error: {error_message}"
    except Exception as e:
        return False, f"An error occurred: {str(e)}"


def get_chrome_version():
    """
    获取chrome版本
    Returns:
    """
    try:
        os_version = OperationSystemManager().get_browser_version_from_os("google-chrome")
        print(f"os_version:{os_version}")
        return os_version
    except Exception as e:
        return None


def get_chrome_version_info(version_info: str):
    if os.path.exists(chrome_json_file):
        with open(chrome_json_file) as f:
            data = f.read()
            json_data = json.loads(data)
            if json_data.get(version_info, None) is not None:
                return True, json_data.get(version_info)
            else:
                dict_version_info = {}
                google_driver_json_url = 'https://googlechromelabs.github.io/chrome-for-testing/known-good-versions-with-downloads.json'
                res = requests.get(google_driver_json_url)
                res_dict = json.loads(res.text)
                version_list = res_dict['versions']
                for version in version_list:
                    downloads_ = version['downloads']
                    if downloads_.get('chromedriver', None) is not None:
                        download_list = downloads_['chromedriver']
                        for data in download_list:
                            if data['platform'] == 'win64':
                                version_place = str(version['version'])
                                version_ = version_place[0:version_place.rfind('.')]
                                dict_version_info[version_] = data['url']
                with open(chrome_json_file, 'w+') as f:
                    json.dump(dict_version_info, f, indent=4)
                if dict_version_info.get(version_info, None) is not None:
                    version_url = dict_version_info[version_info]
                    return True, version_url
                return False, 'error to get'

    else:
        dict_version_info = {}
        google_driver_json_url = 'https://googlechromelabs.github.io/chrome-for-testing/known-good-versions-with-downloads.json'
        res = requests.get(google_driver_json_url)
        res_dict = json.loads(res.text)
        version_list = res_dict['versions']
        for version in version_list:
            downloads_ = version['downloads']
            if downloads_.get('chromedriver', None) is not None:
                download_list = downloads_['chromedriver']
                for data in download_list:
                    if data['platform'] == 'win64':
                        version_place = version['version']
                        version_ = version_place[0:version_place.rfind('.')]
                        dict_version_info[version_] = data['url']
        with open(chrome_json_file, 'w+') as f:
            json.dump(dict_version_info, f, indent=4)
        if dict_version_info.get(version_info, None) is not None:
            version_url = dict_version_info[version_info]
            return True, version_url
        return False, 'error to get'


def download_suit_chrome_driver(chrome_driver_path: str = "chromedriver.exe"):
    """
    下载合适的chrome_driver.exe
    Returns:
    """
    is_ok, chrome_driver_version = get_chromedriver_version(chrome_driver_path)
    browser_version = get_chrome_version()
    if is_ok:
        if str(chrome_driver_version).count(browser_version) > 0:
            print(f"当前已是合适的chrome_driver：{chrome_driver_version}")
            return True
        else:
            chrome_driver_big_version = browser_version.split(".")[0]
            if int(chrome_driver_big_version) < 115:
                print("下载Chrome-Driver")
                install_chrome_driver()
            else:
                is_get_chrome, version_info = get_chrome_version_info(browser_version)
                if is_get_chrome:
                    download_url = version_info
                    print('ok-remove-0')
                    if os.path.exists(chrome_zip):
                        os.remove(chrome_zip)
                    print('ok-remove-2')
                    download_file(chrome_zip, download_url)
                    print('ok-remove-3')
                    with zipfile.ZipFile(chrome_zip, 'r') as zip_ref:
                        zip_ref.extractall('./')
                    shutil.move('./chromedriver-win64/chromedriver.exe', './chromedriver.exe')
                    if os.path.exists(chrome_zip):
                        os.remove(chrome_zip)
    else:
        chrome_driver_big_version = browser_version.split(".")[0]
        if int(chrome_driver_big_version) < 115:
            print("下载Chrome-Driver")
            install_chrome_driver()
        else:
            is_get_chrome, version_info = get_chrome_version_info(browser_version)
            if is_get_chrome:
                download_url = version_info
                print('ok-remove-0')
                if os.path.exists(chrome_zip):
                    os.remove(chrome_zip)
                print('ok-remove-2')
                download_file(chrome_zip, download_url)
                print('ok-remove-3')
                with zipfile.ZipFile(chrome_zip, 'r') as zip_ref:
                    zip_ref.extractall('./')
                shutil.move('./chromedriver-win64/chromedriver.exe', './chromedriver.exe')
                if os.path.exists(chrome_zip):
                    os.remove(chrome_zip)


if __name__ == '__main__':
    download_suit_chrome_driver("chromedriver.exe")
