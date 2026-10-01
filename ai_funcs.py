from langchain_groq import ChatGroq
from dotenv import load_dotenv
load_dotenv()

class Ai_funcs:
    def __init__(self):
        try:
            self.__prompt_valid_horario = open('prompts/verify_loc_horario.md', "r", encoding="utf-8").read()
        except Exception:
            self.__prompt_valid_horario = ""
        if ChatGroq:
            try:
                self.__agent = ChatGroq(model_name="llama3-8b-8192")
            except Exception:
                self.__agent = None
        else:
            self.__agent = None

    def valid_local(self, hor: str, local: str):
        if self.__agent:
            try:
                prompt_completo = self.__prompt_valid_horario + '\ntime:' + hor + '\nlocal:' + local
                return self.__agent.invoke(prompt_completo).content
            except Exception:
                return "1"
        return "1"