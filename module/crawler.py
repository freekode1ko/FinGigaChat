import requests as req
import random
from config import user_agents


class Parser:
    user_agents = user_agents

    def get_html(self, url: str) -> tuple(bool, str):
        """
        Method return html from requester page
        :param url: Where to grab html code
        :return: html code from page as string
        """
        euro_standart = True
        # TODO: Make logic for separating euro sites from US based pages
        header = {'User-Agent': random.choice(self.user_agents)}
        req_page = req.get(url, verify=False, headers=header)
        html = req_page.text
        return euro_standart, html
