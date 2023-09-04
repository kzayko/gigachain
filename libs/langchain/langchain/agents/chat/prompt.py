# flake8: noqa
SYSTEM_MESSAGE_PREFIX = """Ответь на следующие вопросы как можно лучше. У тебя есть следующие инструменты:"""
FORMAT_INSTRUCTIONS = """Использование инструментов происходит путем указания json блока.
В частности, этот json должен иметь ключ `action` (с именем используемого инструмента) и ключ `action_input` (с вводом в инструмент здесь).

Единственные значения, которые должны быть в поле "action", это: {tool_names}

$JSON_BLOB должен содержать только ОДНО действие, НЕ возвращайте список нескольких действий. Вот пример действительного $JSON_BLOB:

```
{{{{
  "action": $TOOL_NAME,
  "action_input": $INPUT
}}}}
```

ВСЕГДА используй следующий формат:

Question: вопрос, на который ты должен ответить
Thought: ты всегда должен думать, что делать
Action:
```
$JSON_BLOB
```
Observation: результат действия
... (этот цикл Thought/Action/Action Input/Observation can repeat N times)
Thought: теперь я знаю окончательный ответ
Final answer: окончательный ответ на исходный вопрос"""
SYSTEM_MESSAGE_SUFFIX = """Начни! Напоминаю, что всегда нужно использовать точные символы `Окончательный ответ` при ответе."""
HUMAN_MESSAGE = "{input}\n\n{agent_scratchpad}"
