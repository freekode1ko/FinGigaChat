"""Бот"""
from aiogram import Bot

from configs import config

bot = Bot(token=config.api_token)  # FIXME
