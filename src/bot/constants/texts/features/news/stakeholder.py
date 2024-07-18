from pydantic_settings import BaseSettings


class StakeholderTexts(BaseSettings):
    """Класс для хранения текстовок взаимодействия со стейкхолдерами."""

    # Текстовки для отображения меню новостей по стейкхолдерам
    BEN_MENU_NEWS: str = 'Выберите активы <b>{sh_name}</b>, по которым Вы хотите получить новости'
    LPR_MENU_NEWS: str = '<b>{sh_name}</b> является ЛПР следующих компаний, выберите по которым Вы хотите получить новости'
    COMMON_MENU_NEWS: str = 'Выберите из списка компании, аффилированные с <b>{sh_name}</b>, по которым Вы хотите получить новости'

    # Ссылка на биографию стейкхолдера
    BIO_LINK: str = ' <a href="{link}">forbes.ru</a>'

    # Текстовки для отображения новостей
    FEW_BEN_SHOW_NEWS: str = 'Вот новости по активам <b>{sh_name}</b>'
    FEW_LPR_SHOW_NEWS: str = 'Вот новости по клиентам, для которого <b>{sh_name}</b> является ЛПР'
    COMMON_SHOW_NEWS: str = 'Вот новости по компаниям, аффилированным с <b>{sh_name}</b>'
    ONE_BEN_SHOW_NEWS: str = 'Вот новости по активу <b>{sh_name}</b>\n\n'
    ONE_LPR_SHOW_NEWS: str = 'Вот новости по <b>{client}</b>, для которого <b>{sh_name}</b> является ЛПР\n\n'

    # Сообщение для отображения меню по клиенту
    CLIENT_MENU_START: str = 'Дополнительные данные о клиенте <b>{client}</b>'
