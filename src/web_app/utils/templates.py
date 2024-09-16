from fastapi.templating import Jinja2Templates

from constants import constants

templates = Jinja2Templates(directory=constants.PROJECT_DIR / 'frontend' / 'templates')
