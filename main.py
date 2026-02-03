import os
import json
import math
from openai import OpenAI
from dotenv import load_dotenv

# 1. Načítame API kľúč
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ---------------------------------------------------------
# KROK A: Funkcia (Nástroj) - ostáva rovnaká
# ---------------------------------------------------------
def vypocitaj_preponu(a, b):
    print(f"--- VOLÁM NÁSTROJ: vypocitaj_preponu pre a={a}, b={b} ---")
    c = math.sqrt(a**2 + b**2)
    return json.dumps({"strana_a": a, "strana_b": b, "vysledok_c": round(c, 2)})

# ---------------------------------------------------------
# KROK B: Definícia nástroja pre LLM - ostáva rovnaká
# ---------------------------------------------------------
tools = [
    {
        "type": "function",
        "function": {
            "name": "vypocitaj_preponu",
            "description": "Vypočíta dĺžku prepony pravouhlého trojuholníka z dvoch odvesien.",
            "parameters": {
                "type": "object",
                "properties": {
                    "a": { "type": "number", "description": "Dĺžka prvej odvesny" },
                    "b": { "type": "number", "description": "Dĺžka druhej odvesny" },
                },
                "required": ["a", "b"],
            },
        }
    }
]

# ---------------------------------------------------------
# KROK C: Hlavná logika - TU SÚ ZMENY
# ---------------------------------------------------------
def main():
    print("=== VÝPOČET PREPONY (PYTAGOROVA VETA) ===")
    
    # 1. Vypýtame si hodnoty od teba cez terminál
    strana_a = input("Zadaj dĺžku strany A: ")
    strana_b = input("Zadaj dĺžku strany B: ")

    # 2. Vytvoríme otázku pre LLM dynamicky
    # Používame takzvaný f-string (písmeno f pred úvodzovkami), 
    # ktorý nám dovolí vložiť premenné priamo do textu pomocou {zátvoriek}.
    user_query = f"Mám pravouhlý trojuholník so stranami a={strana_a} a b={strana_b}. Vypočítaj mi preponu."
    
    print(f"\nPosielam túto otázku na LLM: '{user_query}'")
    
    messages = [{"role": "user", "content": user_query}]
    
    # Prvé volanie LLM
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        tools=tools,
        tool_choice="auto", 
    )

    response_message = response.choices[0].message
    tool_calls = response_message.tool_calls

    if tool_calls:
        messages.append(response_message)

        for tool_call in tool_calls:
            function_name = tool_call.function.name
            function_args = json.loads(tool_call.function.arguments)
            
            if function_name == "vypocitaj_preponu":
                function_response = vypocitaj_preponu(
                    a=function_args.get("a"),
                    b=function_args.get("b")
                )
                
                messages.append(
                    {
                        "tool_call_id": tool_call.id,
                        "role": "tool",
                        "name": function_name,
                        "content": function_response,
                    }
                )
        
        print("Spracovávam výsledok...")
        second_response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
        )
        
        final_answer = second_response.choices[0].message.content
        print("\n=== ODPOVEĎ ===")
        print(final_answer)
    else:
        print("LLM sa rozhodol nepoužiť nástroj (skús zadať čísla jasnejšie).")

if __name__ == "__main__":
    main()