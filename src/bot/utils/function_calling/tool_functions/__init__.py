"""Function calling tools"""

from utils.function_calling.tool_functions.call_report.run import get_call_reports_by_name
from utils.function_calling.tool_functions.cib_info.run import get_cib_reports_by_name
from utils.function_calling.tool_functions.commodity.run import get_commodity_quote
from utils.function_calling.tool_functions.help.run import get_help_function
from utils.function_calling.tool_functions.preparing_meeting.run import get_preparing_for_meeting
from utils.function_calling.tool_functions.product.run import get_product_list, get_product_recomendation
from utils.function_calling.tool_functions.rag.run import rag_news, rag_cib, rag_web
from utils.function_calling.tool_functions.summarization.run import get_news_by_name

# TODO: надо бы добавить впринципе в документацию о том, как тут структура тулзов/агентов устроена у нас

tools_functions = [get_commodity_quote,
                   get_help_function,
                   get_product_list,
                   get_preparing_for_meeting]

tool_functions_prepare_for_meeting = [
    get_call_reports_by_name,
    get_cib_reports_by_name,
    rag_news,
    rag_cib,
    rag_web,
    get_product_recomendation,
    get_news_by_name,
]
