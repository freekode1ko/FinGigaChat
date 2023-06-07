from config import user_agents
import requests as req
import random


class Parser:
    user_agents = user_agents

    def get_html(self, url: str):
        """
        Method return html from requester page
        :param url: Where to grab html code
        :return: html code from page as string
        """
        euro_standart = False
        if '.ru' in url:
            euro_standart = True
        header = {'User-Agent': random.choice(self.user_agents)}
        req_page = req.get(url, verify=False, headers=header)
        html = req_page.text
        return euro_standart, html
