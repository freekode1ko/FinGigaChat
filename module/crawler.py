import requests.exceptions

from config import user_agents
import requests as req
import pandas as pd
import random


class Dictlist(dict):
    def __setitem__(self, key, value) -> dict:
        """
        Overwrite default method setitem in class dict to append in list new urls
        :param key: Where need to add
        :param value: What need to add
        :return: dict with appended value in list for selected key
        """
        try:
            self[key]
        except KeyError:
            super(Dictlist, self).__setitem__(key, [])
        self[key].append(value)


proxy = Dictlist()


class Parser:
    user_agents = user_agents

    @staticmethod
    def get_proxy_addresses() -> None:
        """
        Method to get free proxy list from web
        and load it to package variable
        :return: None
        """
        global proxy
        try:
            ip_table = pd.DataFrame()
            html = req.get('https://free-proxy-list.net/', verify=False)

            for table in pd.read_html(html.text):
                if 'IP Address' in table.keys():
                    ip_table = table
            proxy['https'] = ['https://10.10.1.10:1080']
            proxy['http'] = ['http://10.10.1.10:3128']
            for ip in ip_table.values.tolist():
                if ip[1] in [443, 4849, 5443, 5989, 5990, 6443, 6771, 1080, 7677]:
                    proxy['https'] = 'https://{}:{}'.format(ip[0], ip[1])
                elif ip in [80, 280, 777, 3128, 1001, 1183, 2688, 8080, 8088, 8008]:
                    proxy['http'] = 'http://{}:{}'.format(ip[0], ip[1])
        except req.exceptions.MissingSchema:
            proxy['https'] = ['https://10.10.1.10:1080']
            proxy['http'] = ['http://10.10.1.10:3128']

    def get_html(self, url: str, session: req.sessions.Session):
        """
        Method return html from requester page
        :param session: request "user" session
        :param url: Where to grab html code
        :return: html code from page as string
        """
        euro_standard = False
        http = random.choice(proxy['http'])
        https = random.choice(proxy['https'])
        if type(http) == list:
            http = http[0]
        if type(https) == list:
            https = https[0]
        proxies = {'http': http, 'https': https}

        if '.ru' in url:
            euro_standard = True

        try:
            header = {'User-Agent': random.choice(self.user_agents),
                      'Connection': 'keep-alive',
                      'Accept-Encoding': 'gzip,deflate'}
            req_page = session.get(url, verify=False, headers=header)

        except req.exceptions.ConnectionError:
            session = req.Session()
            header = {'User-Agent': random.choice(self.user_agents),
                      'Connection': 'keep-alive',
                      'Accept-Encoding': 'gzip,deflate'}
            req_page = session.get(url, verify=False, headers=header, proxies=proxies)
        html = req_page.text

        return euro_standard, html
