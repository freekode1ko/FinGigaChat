from config import user_agents
import requests as req
import random


class Parser:
    user_agents = user_agents

    def get_html(self, url: str, session: req.sessions.Session):
        """
        Method return html from requester page
        :param session: request "user" session
        :param url: Where to grab html code
        :return: html code from page as string
        """
        proxies = {
            'http': 'http://10.10.1.10:3128',
            'https': 'http://10.10.1.10:1080',
        }
        euro_standart = False
        if '.ru' in url:
            euro_standart = True
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
        return euro_standart, html
