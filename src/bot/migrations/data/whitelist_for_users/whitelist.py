from configs import config


DATA_FILE_NAME = config.PROJECT_DIR / 'migrations' / 'data' / 'whitelist_for_users' / 'whitelist_data.txt'


def download_data_from_file(fname: str) -> list[dict[str, str]]:
    emails = []
    with open(fname, 'r') as rf:
        for line in rf:
            emails.append({'user_email': line.strip()})
    return emails


data = download_data_from_file(DATA_FILE_NAME)
