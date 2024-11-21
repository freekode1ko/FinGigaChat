"""Function calling tools"""

from utils.function_calling.tool_functions.call_report.run import get_call_report
from utils.function_calling.tool_functions.cib_info.run import get_cib_info
from utils.function_calling.tool_functions.rag.run import get_rag_answer
from utils.function_calling.tool_functions.recomendation.run import get_recomendation
from utils.function_calling.tool_functions.summarization.run import get_summarization

from utils.function_calling.tool_functions.commodity.run import get_commodity_quote
from utils.function_calling.tool_functions.help.run import get_help_function
from utils.function_calling.tool_functions.product.run import get_product_list
from utils.function_calling.tool_functions.preparing_meeting.run import get_preparing_for_meeting

# TODO: надо бы добавить впринципе в документацию о том, как тут структура тулзов/агентов устроена у нас

tools_functions = [get_commodity_quote,
                   get_help_function,
                   get_product_list,
                   get_preparing_for_meeting]
tool_functions_prepare_for_meeting = [get_summarization,
                                      get_cib_info,
                                      get_rag_answer,
                                      get_recomendation,
                                      get_call_report]
