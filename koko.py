import streamlit as st
import json
import sympy as sp
from openai import OpenAI

try:
    from ddgs import DDGS
except ImportError:
    from duckduckgo_search import DDGS

client = OpenAI(
    base_url="https://oxionai.com/v1", 
    api_key=st.secrets["OXION_KEY"]
)

SYSTEM_PROMPT = """Ты — Коко, продвинутый ИИ-ассистент. 
Твоя задача — помогать пользователю, отвечая на вопросы, решая задачи и находя информацию.

Твои правила (алгоритм действий):
1. Если вопрос требует точных математических вычислений, используй инструмент `solve_math`.
2. Если вопрос касается новостей, курсов валют, погоды или фактов, которых нет в твоей базе знаний, используй инструмент `web_search`.
3. Если вопрос простой (приветствие, болтовня), отвечай сразу, без инструментов.
4. В финальном ответе будь вежливым, структурированным и ссылайся на найденную информацию.
"""

tools = [
    {
        "type": "function",
        "function": {
            "name": "solve_math",
            "description": "Решает математические выражения и уравнения.",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string", 
                        "description": "Математическое выражение (например, '2+2', 'x**2 - 4 = 0')"
                    }
                },
                "required": ["expression"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "web_search",
            "description": "Ищет актуальную информацию в интернете.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string", 
                        "description": "Точный поисковый запрос"
                    }
                },
                "required": ["query"]
            }
        }
    }
]

def solve_math(expression: str):
    try:
        expr_clean = expression.replace("^", "**")
        if '=' in expr_clean:
            left, right = expr_clean.split('=')
            eq = sp.Eq(sp.sympify(left), sp.sympify(right))
            solution = sp.solve(eq)
            return f"Корни уравнения: {solution}"
        else:
            result = sp.sympify(expr_clean)
            return f"Результат: {result.evalf()}"
    except Exception as e:
        return f"Ошибка математики: {str(e)}"

def web_search(query: str):
    try:
        results = DDGS().text(query, max_results=3)
        if not results:
            return "Ничего не найдено."
        
        formatted_results = "\n".join([f"- {r.get('title', 'Без названия')}: {r.get('body', 'Нет описания')}" for r in results])
        return formatted_results
    except Exception as e:
        return f"Ошибка поиска: {str(e)}"

available_functions = {
    "solve_math": solve_math,
    "web_search": web_search
}

def chat_with_koko():
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    
    print("🤖 Привет! Я Коко. Чем могу помочь? (напишите 'выход' для завершения)")
    
    while True:
        try:
            user_input = input("\nВы: ")
            if user_input.lower() in ['выход', 'exit', 'quit']:
                print("Коко: До встречи!")
                break
                
            messages.append({"role": "user", "content": user_input})
            
            max_iterations = 5
            iteration = 0
            
            while iteration < max_iterations:
                iteration += 1
                
                response = client.chat.completions.create(
                    model="deepseek-v4-flash-0731",
                    messages=messages,
                    tools=tools,
                    tool_choice="auto"
                )
                
                response_message = response.choices[0].message
                
                messages.append(response_message.model_dump(exclude_none=True))
                
                if not response_message.tool_calls:
                    print(f"\nКоко: {response_message.content}")
                    break 
                
                print(f"\n[⚙️ Коко использует инструменты: {len(response_message.tool_calls)}]")
                
                for tool_call in response_message.tool_calls:
                    function_name = tool_call.function.name
                    function_args = json.loads(tool_call.function.arguments)
                    
                    print(f"   -> {function_name}({function_args})")
                    
                    function_to_call = available_functions.get(function_name)
                    if function_to_call:
                        function_response = function_to_call(**function_args)
                    else:
                        function_response = "Ошибка: Инструмент не найден."
                    
                    print(f"   [Результат]: {function_response[:100]}...") 
                    
                    messages.append({
                        "tool_call_id": tool_call.id,
                        "role": "tool",
                        "name": function_name,
                        "content": str(function_response)
                    })
                    
        except KeyboardInterrupt:
            print("\nКоко: Завершаю работу.")
            break
        except Exception as e:
            print(f"\n❌ Ошибка в работе Коко: {e}")

if __name__ == "__main__":
    chat_with_koko()
