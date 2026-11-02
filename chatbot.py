#!/usr/bin/env python3
import sqlite3
import re
import ast
import json
import inspect

import ai_funcs
import instituto
import curso
import materia
import professor
import aluno
import mat_curso
import mat_reqs
import turma
import turma_reserva
import aluno_turma
import matricula
import aluno_turma_cancel_request
import freq
import date_funcs

DB_PATH = 'university.db'

# ── Helper print function ─────────────────────────────────────────────────────

def print_result(result):
    if isinstance(result, tuple):
        ok, msg = result
        prefix = "✓ Sucesso:" if ok else "✗ Erro:"
        print(f"\n{prefix} {msg}\n")
    else:
        print(f"\nResultado: {result}\n")


# ── Table initialization ──────────────────────────────────────────────────────

def ensure_tables_exist(cursor: sqlite3.Cursor, conn: sqlite3.Connection):
    instituto._create_table_instituto(cursor)
    curso._create_table_curso(cursor)
    materia._create_table_materia(cursor)
    professor._create_table_professor(cursor)
    aluno._create_table_aluno(cursor)
    mat_curso._create_table_mat_curso(cursor)
    mat_reqs._create_table_mat_reqs(cursor)
    turma._create_table_turma(cursor)
    turma_reserva._create_table_turma_reserva(cursor)
    aluno_turma._create_table_aluno_turma(cursor)
    matricula._create_table_matricula(cursor)
    aluno_turma_cancel_request._create_table_aluno_turma_cancel_request(cursor)
    freq._create_table_freq(cursor)
    conn.commit()


# ── Action Parser ─────────────────────────────────────────────────────────────

def parse_action(text: str) -> dict | None:
    """
    Extracts action dictionary from LLM response text, e.g.:
      {method: 'create_curso', name: 'Computer Science', id_inst: 5}
      {'method': 'create_aluno', 'name': 'Maria', 'cpf': '12345678901', 'id_cur': 1}
      {"method": "set_grade", "id_aluno": 1, "id_turma": 2, "nome_grade": "NF", "grade": 8.5}
    """
    if not text:
        return None

    # Find the outermost dictionary containing the 'method' key
    match = re.search(r'\{[^{}]*[\'\"]?method[\'\"]?\s*:\s*[^{}]*\}', text, re.DOTALL)
    if not match:
        return None

    raw = match.group(0).strip()

    # 1. Try standard json.loads
    try:
        data = json.loads(raw)
        if isinstance(data, dict) and 'method' in data:
            return data
    except Exception:
        pass

    # 2. Try ast.literal_eval (supports single-quoted Python dicts)
    try:
        data = ast.literal_eval(raw)
        if isinstance(data, dict) and 'method' in data:
            return data
    except Exception:
        pass

    # 3. Handle unquoted key syntax e.g. {method: 'create_curso', name: 'CS'}
    try:
        quoted = re.sub(r'([{,]\s*)([a-zA-Z_][a-zA-Z0-9_]*)\s*:', r'\1"\2":', raw)
        data = ast.literal_eval(quoted)
        if isinstance(data, dict) and 'method' in data:
            return data
    except Exception:
        pass

    try:
        as_json = quoted.replace("'", '"')
        data = json.loads(as_json)
        if isinstance(data, dict) and 'method' in data:
            return data
    except Exception:
        pass

    return None


# ── Action Dispatcher & Executor ──────────────────────────────────────────────

METHODS = {
    # University initialization
    'create_university': ensure_tables_exist,

    # Instituto
    'create_instituto': instituto.create_instituto,
    'id_instituto': instituto.id_instituto,
    'delete_instituto': instituto.delete_instituto,

    # Curso
    'create_curso': curso.create_curso,
    'id_curso': curso.id_curso,
    'get_min_periods': curso.get_min_periods,
    'delete_curso': curso.delete_curso,

    # Materia
    'create_materia': materia.create_materia,
    'id_materia': materia.id_materia,
    'delete_materia': materia.delete_materia,

    # Professor
    'create_prof': professor.create_prof,
    'create_professor': professor.create_prof,
    'id_professor': professor.id_professor,
    'delete_professor': professor.delete_professor,

    # Aluno
    'create_aluno': aluno.create_aluno,
    'id_aluno': aluno.id_aluno,
    'periodo_aluno': aluno.periodo_aluno,
    'media_geral': aluno.media_geral,
    'frequencia': aluno.frequencia,
    'taxa_aprovacao': aluno.taxa_aprovacao,
    'taxa_integralizacao': aluno.taxa_integralizacao,
    'delete_aluno': aluno.delete_aluno,

    # Mat_curso
    'create_mat_curso': mat_curso.create_mat_curso,
    'id_mat_curso': mat_curso.id_mat_curso,
    'delete_mat_curso': mat_curso.delete_mat_curso,

    # Mat_reqs
    'create_mat_reqs': mat_reqs.create_mat_reqs,
    'id_mat_reqs': mat_reqs.id_mat_reqs,

    # Turma
    'create_turma': turma.create_turma,
    'id_turma': turma.id_turma,
    'fill_turmas': turma.fill_turmas,
    'finish_turmas': turma.finish_turmas,

    # Turma_reserva
    'create_turma_reseva': turma_reserva.create_turma_reseva,
    'create_turma_reserva': turma_reserva.create_turma_reseva,
    'id_turma_reserva': turma_reserva.id_turma_reserva,
    'delete_turma_reserva': turma_reserva.delete_turma_reserva,

    # Aluno_turma
    'set_grade': aluno_turma.set_grade,
    'id_aluno_turma': aluno_turma.id_aluno_turma,

    # Matricula
    'create_matricula_request': matricula.create_matricula_request,
    'id_matricula': matricula.id_matricula,
    'delete_matricula_request': matricula.delete_matricula_request,

    # Aluno_turma_cancel_request
    'cancel_aluno_turma_request': aluno_turma_cancel_request.cancel_aluno_turma_request,
    'cancel_aluno_turma_resolve': aluno_turma_cancel_request.cancel_aluno_turma_resolve,
    'id_aluno_turma_cancel_request': aluno_turma_cancel_request.id_aluno_turma_cancel_request,

    # Freq
    'lancar_presenca': freq.lancar_presenca,
    'id_freq': freq.id_freq,
}

ALIAS_MAP = {
    'nome': 'name',
    'ch': 'carga_hor',
    'carga_horaria': 'carga_hor',
    'horario': 'hor',
    'tipo': 'type_param',
    'vagas': 'n_vagas',
    'semestre': 'sem',
    'periodo': 'periodo_fluxo',
    'nota': 'grade',
}

def execute_action(cursor: sqlite3.Cursor, conn: sqlite3.Connection, action: dict):
    method_name = str(action.get('method', '')).strip().lower()
    fn = METHODS.get(method_name)

    if not fn:
        return False, f"Método '{method_name}' não reconhecido pelo sistema."

    # Special handling for create_university
    if method_name == 'create_university':
        ensure_tables_exist(cursor, conn)
        return True, "Banco de dados e tabelas inicializados com sucesso."

    sig = inspect.signature(fn)
    fn_params = list(sig.parameters.keys())

    # Map parameters
    call_kwargs = {}
    for p in fn_params:
        if p == 'cursor':
            continue
        if p in action:
            call_kwargs[p] = action[p]
        else:
            # Check aliases
            for alias, target in ALIAS_MAP.items():
                if target == p and alias in action:
                    call_kwargs[p] = action[alias]
                    break
                elif alias == p and target in action:
                    call_kwargs[p] = action[target]
                    break

    # Type conversions
    for k, v in list(call_kwargs.items()):
        if v is None:
            continue
        if k.startswith('id') or k in ['carga_hor', 'n_vagas', 'periodo_fluxo']:
            try:
                call_kwargs[k] = int(v)
            except (ValueError, TypeError):
                pass
        elif k in ['grade', 'priority']:
            try:
                call_kwargs[k] = float(v)
            except (ValueError, TypeError):
                pass
        elif k in ['mat_period', 'result']:
            if isinstance(v, str):
                call_kwargs[k] = v.lower() in ['true', '1', 's', 'sim', 'yes', 'y']
            else:
                call_kwargs[k] = bool(v)

    try:
        res = fn(cursor, **call_kwargs)
        conn.commit()
        return res
    except TypeError as e:
        # Fallback to positional arguments if keyword binding failed
        try:
            positional_args = [call_kwargs[p] for p in fn_params if p != 'cursor' and p in call_kwargs]
            res = fn(cursor, *positional_args)
            conn.commit()
            return res
        except Exception:
            return False, f"Erro nos parâmetros ao executar '{method_name}': {e}"
    except Exception as e:
        return False, f"Erro ao executar '{method_name}': {e}"


# ── Interactive Chat Loop ─────────────────────────────────────────────────────

def main():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    cursor = conn.cursor()

    ensure_tables_exist(cursor, conn)
    ai_agent = ai_funcs.Ai_funcs()

    sem_atual = date_funcs.get_current_semester()
    print("\n" + "="*58)
    print(f"       🎓 UNIVERSITY SYSTEM - AI CHATBOT (Sem: {sem_atual})")
    print("="*58)
    print("Converse com o agente para consultar dados ou executar ações.")
    print("Exemplos:")
    print("  - 'Crie um curso de Ciência da Computação no instituto 1'")
    print("  - 'Qual a média geral do aluno com CPF 11111111111?'")
    print("  - 'Lance a nota final 8.5 para o aluno 1 na turma 1'")
    print("Digite '0' ou 'sair' para encerrar a sessão.")
    print("="*58 + "\n")

    talk = ""

    while True:
        try:
            user_input = input("Você: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n\nSessão encerrada.")
            break

        if not user_input:
            continue

        if user_input.lower() in ['0', 'sair', 'exit', 'quit']:
            print("\nEncerrando a conversa. Até logo!\n")
            break

        # Accumulate conversation history
        if not talk:
            talk = user_input
        else:
            talk += "\n" + user_input

        # Call chatbot method in Ai_funcs
        bot_reply = ai_agent.chatbot(talk)

        if bot_reply == '-1':
            print("\n[Assistente]: Desculpe, não consegui me conectar ao serviço de IA no momento.\n")
            continue

        print(f"\n[Assistente]:\n{bot_reply}\n")

        # Parse and execute action if the model returned an executable dictionary
        action = parse_action(bot_reply)
        execution_note = ""

        if action and action.get('method'):
            method_name = action.get('method')
            print(f"⚙️  [Executando]: {method_name} com parâmetros { {k: v for k, v in action.items() if k != 'method'} }...")
            exec_res = execute_action(cursor, conn, action)
            print_result(exec_res)

            # Inform the conversation history about the actual execution outcome
            execution_note = f"\n[System Execution: {method_name} -> {exec_res}]"

        # Update talk with assistant reply and system execution outcome for next turns
        talk += "\n" + bot_reply + execution_note

    conn.close()


if __name__ == '__main__':
    main()
