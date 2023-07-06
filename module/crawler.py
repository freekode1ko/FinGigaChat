from config import user_agents
import requests as req
import pandas as pd
import random


class Dictlist(dict):
    def __setitem__(self, key, value):
        try:
            self[key]
        except KeyError:
            super(Dictlist, self).__setitem__(key, [])
        self[key].append(value)


proxy = Dictlist()


class Parser:
    user_agents = user_agents

    @staticmethod
    def get_proxy_addresses():
        global proxy
        ip_table = pd.DataFrame()
        html = req.get('https://free-proxy-list.net/', verify=False)

        for table in pd.read_html(html.text):
            if 'IP Address' in table.keys():
                ip_table = table
        proxy['https'] = ['162.223.94.164:443', '100.19.135.109:4849', '5.161.41.17:5443']
        proxy['http'] = ['162.223.94.164:80', '100.19.135.109:80', '5.161.41.17:80']
        for ip in ip_table.values.tolist():
            if ip[1] in [443, 4849, 5443, 5989, 5990, 6443, 6771, 7443, 7677]:
                proxy['https'] = '{}:{}'.format(ip[0], ip[1])
            elif ip in [80, 280, 777, 832, 1001, 1183, 2688, 8080, 8088, 8008]:
                proxy['http'] = '{}:{}'.format(ip[0], ip[1])

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
