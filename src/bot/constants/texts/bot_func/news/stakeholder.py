from pydantic_settings import BaseSettings


class StakeholderTexts(BaseSettings):
    """Класс для хранения текстовок взаимодействия со стейкхолдерами."""

    # Текстовки для отображения меню новостей по стейкхолдерам
    BEN_MENU_NEWS: str = 'Выберите активы <b>{ben_name}</b>, по которым Вы хотите получить новости'
    LPR_MENU_NEWS: str = '<b>{ben_name}</b> является ЛПР следующих компаний, выберите по которым Вы хотите получить новости'
    FEW_COMMON_MENU_NEWS: str = 'Выберите из списка компании, аффилированные с <b>{ben_name}</b>, по которым Вы хотите получить новости'

    # Ссылка на биографию стейкхолдера
    BIO_LINK: str = ' <a href="{link}">forbes.ru</a>'

    # Текстовки для отображения новостей
    FEW_BEN_SHOW_NEWS: str = 'Вот новости по активам <b>{ben_name}</b>'
    FEW_LPR_SHOW_NEWS: str = 'Вот новости по клиентам, для которого <b>{ben_name}</b> является ЛПР'
    FEW_COMMON_SHOW_NEWS: str = 'Вот новости по компаниям, аффилированным с <b>{ben_name}</b>'
    ONE_BEN_SHOW_NEWS: str = 'Вот новости по активу <b>{ben_name}</b>\n\n'
    ONE_LPR_SHOW_NEWS: str = 'Вот новости по <b>{client}</b>, для которого <b>{ben_name}</b> является ЛПР\n\n'
