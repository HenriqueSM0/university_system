from langchain_groq import ChatGroq
from dotenv import load_dotenv

load_dotenv()

class Ai_funcs:
    def __init__(self):
        self.__prompt_valid_horario = open('prompts/verify_loc_horario.md', "r", encoding="utf-8").read()
        self.__agent = ChatGroq(model_name="llama3-8b-8192") 

    def valid_local(self, hor: str, local: str):
        prompt_completo = self.__prompt_valid_horario + '\ntime:' + hor + '\nlocal:' + local
        return self.__agent.invoke(prompt_completo).content