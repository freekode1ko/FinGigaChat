"""Параметры для оценки качества ретривера"""
import sys

from pathlib import Path

EVALUATION_DATASET_PATH = "dataset/qr_data_short.xlsx"

PROJECT_DIR = Path(__file__).parent

LOG_FILE = "evaluation"
LOG_LEVEL = 20

N_ATTEMPTS = 3

ANSWER_FORMAT = "tg"
