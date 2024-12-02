"""Function calling tools"""

from utils.function_calling.tool_functions.call_report.run import get_call_reports_by_name
from utils.function_calling.tool_functions.cib_info.run import get_analytical_reports_by_name
from utils.function_calling.tool_functions.commodity.run import get_commodity_quote
from utils.function_calling.tool_functions.help.run import get_help_function
from utils.function_calling.tool_functions.preparing_meeting.run import get_preparing_for_meeting
from utils.function_calling.tool_functions.product.run import get_product_list

# TODO: надо бы добавить впринципе в документацию о том, как тут структура тулзов/агентов устроена у нас

tools_functions = [get_commodity_quote,
                   get_help_function,
                   get_product_list,
                   get_preparing_for_meeting]
