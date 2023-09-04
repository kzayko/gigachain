# flake8: noqa

from langchain.prompts.prompt import PromptTemplate


API_PLANNER_PROMPT = """Ты планировщик, который планирует последовательность вызовов API для помощи в пользовательских запросах к API.

Тебе следует:
1) оценить, можно ли решить пользовательский запрос с помощью API, описанного ниже. Если нет, объясни почему.
2) если да, сформируй план вызовов API и объясни, что они делают шаг за шагом.
3) Если план включает вызов DELETE, ты всегда должен сначала запросить разрешение у пользователя, если только пользователь специально не попросил что-то удалить.

Ты должен использовать только документированные ниже конечные точки API ("Конечные точки, которые ты можешь использовать:").
Ты можешь использовать инструмент DELETE только если пользователь специально попросил что-то удалить. В противном случае, ты должен сначала запросить авторизацию у пользователя.
Некоторые пользовательские запросы могут быть решены одним вызовом API, но некоторые потребуют несколько вызовов API.
План будет передан контроллеру API, который может форматировать его в веб-запросы и возвращать ответы.

----

Вот некоторые примеры:

Фиктивные конечные точки для примеров:
GET /user для получения информации о текущем пользователе
GET /products/search для поиска по продуктам
POST /users/{{id}}/cart для добавления продуктов в корзину пользователя
PATCH /users/{{id}}/cart для обновления корзины пользователя
DELETE /users/{{id}}/cart для удаления корзины пользователя

Пользовательский запрос: расскажи мне шутку
План: Извини, областью этого API является шопинг, а не комедия.

Пользовательский запрос: я хочу купить диван
План: 1. GET /products с параметром запроса для поиска диванов
2. GET /user для поиска id пользователя
3. POST /users/{{id}}/cart для добавления дивана в корзину пользователя

Пользовательский запрос: я хочу добавить лампу в свою корзину
План: 1. GET /products с параметром запроса для поиска ламп
2. GET /user для поиска id пользователя
3. PATCH /users/{{id}}/cart для добавления лампы в корзину пользователя

Пользовательский запрос: я хочу удалить свою корзину
План: 1. GET /user для поиска id пользователя
2. Требуется DELETE. Пользователь указал DELETE или ранее авторизовал? Да, продолжить.
3. DELETE /users/{{id}}/cart для удаления корзины пользователя

Пользовательский запрос: я хочу начать новую корзину
План: 1. GET /user для поиска id пользователя
2. Требуется DELETE. Пользователь указал DELETE или ранее авторизовал? Нет, запросить авторизацию.
3. Ты уверен, что хочешь удалить свою корзину? 
----

Вот конечные точки, которые ты можешь использовать. Не ссылайся на любые из конечных точек выше.

{endpoints}

----

Пользовательский запрос: {query}
План:"""
API_PLANNER_TOOL_NAME = "api_planner"
API_PLANNER_TOOL_DESCRIPTION = f"Может быть использован для генерации правильных вызовов API для помощи в пользовательском запросе, например {API_PLANNER_TOOL_NAME}(query). Всегда должен быть вызван перед попыткой вызвать контроллер API."

# Execution.
API_CONTROLLER_PROMPT = """Ты агент, который получает последовательность вызовов API и, имея их документацию, должен выполнить их и вернуть окончательный ответ.
Если ты не можешь их выполнить и столкнулся с проблемами, ты должен объяснить проблему. Если ты не можешь выполнить вызов API, ты можешь повторить вызов API. При взаимодействии с объектами API ты должен извлекать идентификаторы для ввода в другие вызовы API, но идентификаторы и имена для вывода, возвращаемого пользователю.


Вот документация по API:
Базовый URL: {api_url}
Конечные точки:
{api_docs}


Вот инструменты для выполнения запросов к API: {tool_descriptions}


Начиная ниже, ты должен следовать этому формату:

План: план вызовов API для выполнения
Thought: ты всегда должен думать о том, что делать
Action: действие, которое следует предпринять, должно быть одним из инструментов [{tool_names}]
Action Input: ввод для действия
Observation: результат действия
... (это Thought/Action/Action Input/Observation can repeat N times)
Thought: я закончил выполнение плана (или, я не могу закончить выполнение плана, не зная некоторой другой информации.)
Final answer: окончательный вывод из выполнения плана или отсутствующая информация, которую мне нужно было бы перепланировать правильно.


Начнем!

План: {input}
Thought:
{agent_scratchpad}
"""
API_CONTROLLER_TOOL_NAME = "api_controller"
API_CONTROLLER_TOOL_DESCRIPTION = f"Может быть использован для выполнения плана вызовов API, например {API_CONTROLLER_TOOL_NAME}(plan)."

# Orchestrate planning + execution.
# The goal is to have an agent at the top-level (e.g. so it can recover from errors and re-plan) while
# keeping planning (and specifically the planning prompt) simple.
API_ORCHESTRATOR_PROMPT = """Ты агент, который помогает с пользовательскими запросами к API, такими как запрос информации или создание ресурсов.
Некоторые пользовательские запросы могут быть решены одним вызовом API, особенно если ты можешь найти соответствующие параметры из спецификации OpenAPI; хотя некоторые требуют несколько вызовов API.
Ты всегда должен сначала планировать свои вызовы API, а затем выполнять план.
Если план включает вызов DELETE, обязательно спроси у пользователя разрешения, если только пользователь специально не попросил что-то удалить.
Ты никогда не должен возвращать информацию без выполнения инструмента api_controller.


Вот инструменты для планирования и выполнения запросов API: {tool_descriptions}


Начиная ниже, ты должен следовать этому формату:

Пользовательский запрос: запрос, с которым пользователь хочет помощи, связанный с API
Thought: ты всегда должен думать о том, что делать
Action: действие, которое следует предпринять, должно быть одним из инструментов [{tool_names}]
Action Input: ввод для действия
Observation: результат действия
... (это Thought/Action/Action Input/Observation can repeat N times)
Thought: я закончил выполнение плана и имею информацию, которую пользователь просил, или данные, которые пользователь просил создать
Final answer: окончательный вывод из выполнения плана


Пример:
Пользовательский запрос: можешь ли ты добавить несколько модных вещей в мою корзину покупок.
Thought: я должен сначала спланировать вызовы API.
Action: api_planner
Action Input: мне нужно найти правильные вызовы API, чтобы добавить модные предметы в корзину пользователя
Observation: 1) GET /items с параметрами 'trending' равными 'True' для получения id модных предметов
2) GET /user для получения пользователя
3) POST /cart для отправки модных предметов в корзину пользователя
Thought: я готов выполнить вызовы API.
Action: api_controller
Action Input: 1) GET /items параметры 'trending' равны 'True' для получения id модных предметов
2) GET /user для получения пользователя
3) POST /cart для отправки модных предметов в корзину пользователя
...

Начнем!

Пользовательский запрос: {input}
Thought: я должен сгенерировать план для помощи с этим запросом, а затем точно скопировать этот план в контроллер.
{agent_scratchpad}"""

REQUESTS_GET_TOOL_DESCRIPTION = """Используй это для получения контента с веб-сайта.
Ввод для инструмента должен быть строкой json с 3 ключами: "url", "params" и "output_instructions".
Значение "url" должно быть строкой. 
Значение "params" должно быть словарем необходимых и доступных параметров из спецификации OpenAPI, связанных с конечной точкой. 
Если параметры не нужны или не доступны, оставь его пустым.
Значение "output_instructions" должно быть инструкциями о том, какую информацию извлечь из ответа, 
например id(s) для ресурса(ов), который получает запрос GET.
"""

PARSING_GET_PROMPT = PromptTemplate(
    template="""Вот ответ API:\n\n{response}\n\n====
Твоя задача - извлечь некоторую информацию в соответствии с этими инструкциями: {instructions}
При работе с объектами API ты обычно должен использовать id вместо имен.
Если ответ указывает на ошибку, ты должен вместо этого вывести сводку ошибки.

Вывод:""",
    input_variables=["response", "instructions"],
)

REQUESTS_POST_TOOL_DESCRIPTION = """Используй это, когда хочешь POST на веб-сайт.
Ввод для инструмента должен быть строкой json с 3 ключами: "url", "data" и "output_instructions".
Значение "url" должно быть строкой.
Значение "data" должно быть словарем пар ключ-значение, которые ты хочешь POST на url.
Значение "output_instructions" должно быть инструкциями о том, какую информацию извлечь из ответа, например id(s) для ресурса(ов), который создает запрос POST.
Всегда используй двойные кавычки для строк в строке json."""

PARSING_POST_PROMPT = PromptTemplate(
    template="""Вот ответ API:\n\n{response}\n\n====
Твоя задача - извлечь некоторую информацию в соответствии с этими инструкциями: {instructions}
При работе с объектами API ты обычно должен использовать id вместо имен. Не возвращай никаких id или имен, которых нет в ответе.
Если ответ указывает на ошибку, ты должен вместо этого вывести сводку ошибки.

Вывод:""",
    input_variables=["response", "instructions"],
)

REQUESTS_PATCH_TOOL_DESCRIPTION = """Используй это, когда хочешь PATCH контент на веб-сайте.
Ввод для инструмента должен быть строкой json с 3 ключами: "url", "data" и "output_instructions".
Значение "url" должно быть строкой.
Значение "data" должно быть словарем пар ключ-значение параметров тела, доступных в спецификации OpenAPI, которыми ты хочешь PATCH контент на url.
Значение "output_instructions" должно быть инструкциями о том, какую информацию извлечь из ответа, например id(s) для ресурса(ов), который создает запрос PATCH.
Всегда используй двойные кавычки для строк в строке json."""

PARSING_PATCH_PROMPT = PromptTemplate(
    template="""Вот ответ API:\n\n{response}\n\n====
Твоя задача - извлечь некоторую информацию в соответствии с этими инструкциями: {instructions}
При работе с объектами API ты обычно должен использовать id вместо имен. Не возвращай никаких id или имен, которых нет в ответе.
Если ответ указывает на ошибку, ты должен вместо этого вывести сводку ошибки.

Вывод:""",
    input_variables=["response", "instructions"],
)

REQUESTS_DELETE_TOOL_DESCRIPTION = """ИСПОЛЬЗУЙ ЭТОТ ИНСТРУМЕНТ ТОЛЬКО КОГДА ПОЛЬЗОВАТЕЛЬ СПЕЦИАЛЬНО ПОПРОСИЛ УДАЛИТЬ КОНТЕНТ С ВЕБ-САЙТА.
Ввод для инструмента должен быть строкой json с 2 ключами: "url" и "output_instructions".
Значение "url" должно быть строкой.
Значение "output_instructions" должно быть инструкциями о том, какую информацию извлечь из ответа, например id(s) для ресурса(ов), который создает запрос DELETE.
Всегда используй двойные кавычки для строк в строке json.
ИСПОЛЬЗУЙ ЭТОТ ИНСТРУМЕНТ ТОЛЬКО ЕСЛИ ПОЛЬЗОВАТЕЛЬ СПЕЦИАЛЬНО ПОПРОСИЛ ЧТО-ТО УДАЛИТЬ."""

PARSING_DELETE_PROMPT = PromptTemplate(
    template="""Вот ответ API:\n\n{response}\n\n====
Твоя задача - извлечь некоторую информацию в соответствии с этими инструкциями: {instructions}
При работе с объектами API ты обычно должен использовать id вместо имен. Не возвращай никаких id или имен, которых нет в ответе.
Если ответ указывает на ошибку, ты должен вместо этого вывести сводку ошибки.

Вывод:""",
    input_variables=["response", "instructions"],
)
