import re
from langchain_groq import ChatGroq
from dotenv import load_dotenv
load_dotenv()

class Ai_funcs:
    def __init__(self):
        try:
            self.__prompt_valid_horario = open('prompts/verify_loc_horario.md', "r", encoding="utf-8").read()
        except Exception:
            self.__prompt_valid_horario = ""

        self.__role_text = ""
        self.__entities = {}
        self.__behavior_text = ""
        self.__prompt_chatbot = ""
        self.__parse_chatbot_prompt()

        if ChatGroq:
            try:
                self.__agent = ChatGroq(model_name="openai/gpt-oss-120b")
            except Exception:
                self.__agent = None
        else:
            self.__agent = None

    def __parse_chatbot_prompt(self):
        try:
            full_text = open('prompts/chatbot.md', "r", encoding="utf-8").read()
            self.__prompt_chatbot = full_text

            behavior_pos = full_text.find('# USER BEHAVIOR:')
            if behavior_pos != -1:
                entities_part = full_text[:behavior_pos]
                self.__behavior_text = full_text[behavior_pos:]
            else:
                entities_part = full_text
                self.__behavior_text = ""

            role_end = entities_part.find('# ENTITIES:')
            if role_end != -1:
                self.__role_text = entities_part[:role_end].strip()
            else:
                self.__role_text = "# ROLE\n\nYou are a Agent of a System of an Univerity, and you need to evaluate, assist, and fulfill user requests:"

            pattern = r'(?m)^(\d+\)\s*([A-Za-z0-9_]+)\s*:)'
            matches = list(re.finditer(pattern, entities_part))
            for i, m in enumerate(matches):
                start = m.start()
                end = matches[i + 1].start() if i + 1 < len(matches) else len(entities_part)
                key = m.group(2).lower()
                self.__entities[key] = entities_part[start:end].strip()
        except Exception:
            self.__role_text = ""
            self.__entities = {}
            self.__behavior_text = ""
            self.__prompt_chatbot = ""

    def valid_local(self, hor: str, local: str):
        if self.__agent:
            try:
                prompt_completo = self.__prompt_valid_horario + '\ntime:' + hor + '\nlocal:' + local
                return self.__agent.invoke(prompt_completo).content
            except Exception:
                return '-1'
        return '-1'

    def __detect_relevant_entities(self, user_input: str) -> list[str]:
        input_lower = user_input.lower()
        keyword_matches = [
            ent for ent in self.__entities.keys()
            if re.search(r'\b' + re.escape(ent) + r'\b', input_lower)
        ]

        router_entities = []
        if self.__agent:
            try:
                available_list = ", ".join(self.__entities.keys())
                router_prompt = (
                    "You are an intent classifier for a University System.\n"
                    f"Available entities: {available_list}\n"
                    "Given the user message below, identify which 1 or 2 entities are relevant to the user request.\n"
                    "If the user message is a greeting, general chat, or does not relate to a specific entity, answer 'none'.\n"
                    "Answer ONLY with the comma-separated entity name(s) in lowercase, nothing else.\n\n"
                    f"User message:\n{user_input[-1500:]}"
                )
                response = self.__agent.invoke(router_prompt).content.lower().strip()
                for ent in self.__entities.keys():
                    if ent in response and ent not in router_entities:
                        router_entities.append(ent)
            except Exception:
                pass

        selected = router_entities
        for km in keyword_matches:
            if km not in selected:
                selected.append(km)

        return selected

    def chatbot(self, user_input: str) :
        if not self.__agent:
            return '-1'

        try:
            selected_entities = self.__detect_relevant_entities(user_input)

            if selected_entities:
                entities_content = "\n\n".join(
                    self.__entities[ent] for ent in selected_entities if ent in self.__entities
                )
            else:
                entities_content = (
                    "# ENTITIES SUMMARY:\n"
                    "The system manages the following entities: "
                    + ", ".join(self.__entities.keys())
                    + ".\nWhen the user specifies an entity or action, detailed methods will be referenced."
                )

            trimmed_input = user_input[-4000:] if len(user_input) > 4000 else user_input

            prompt_completo = (
                f"{self.__role_text}\n\n"
                f"# ENTITIES:\n\n{entities_content}\n\n"
                f"{self.__behavior_text}\n\n"
                f"# USER INPUT (TEXT):\n{trimmed_input}"
            )

            return self.__agent.invoke(prompt_completo).content
        except Exception as e:
            print(e)
            return '-1'
