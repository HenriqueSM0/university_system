#!/usr/bin/env python3
import sqlite3
import os

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

# ── Helper input functions ────────────────────────────────────────────────────

def print_result(result):
    if isinstance(result, tuple):
        ok, msg = result
        prefix = "✓ Sucesso:" if ok else "✗ Erro:"
        print(f"\n{prefix} {msg}\n")
    else:
        print(f"\nResultado: {result}\n")


def prompt_str(message: str, allow_empty: bool = False) -> str:
    while True:
        val = input(message).strip()
        if val or allow_empty:
            return val
        print("Entrada não pode ser vazia. Tente novamente.")


def prompt_int(message: str, allow_empty: bool = False) -> int | None:
    while True:
        val = input(message).strip()
        if not val and allow_empty:
            return None
        try:
            return int(val)
        except ValueError:
            print("Valor inválido. Por favor, digite um número inteiro.")


def prompt_float(message: str, allow_empty: bool = False) -> float | None:
    while True:
        val = input(message).strip()
        if not val and allow_empty:
            return None
        try:
            return float(val)
        except ValueError:
            print("Valor inválido. Por favor, digite um número válido.")


def prompt_id_or_cpf() -> tuple[int | None, str | None]:
    print("\nIdentificar aluno por:")
    print("  1 - ID")
    print("  2 - CPF")
    op = prompt_str("Escolha (1 ou 2): ")
    if op == '1':
        id_val = prompt_int("Digite o ID do aluno: ")
        return id_val, None
    elif op == '2':
        cpf_val = prompt_str("Digite o CPF do aluno (11 dígitos): ")
        return None, cpf_val
    else:
        print("Opção inválida.")
        return None, None


# ── 1. Create University ──────────────────────────────────────────────────────

def create_university(cursor: sqlite3.Cursor, conn: sqlite3.Connection):
    print("\nInicializando banco de dados e criando todas as tabelas...")
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
    print("✓ Banco de dados 'university.db' e todas as tabelas criados com sucesso!\n")


# ── 2. Create Institute ───────────────────────────────────────────────────────

def menu_create_institute(cursor: sqlite3.Cursor, conn: sqlite3.Connection):
    print("\n--- Create Institute ---")
    nome = prompt_str("Nome do Instituto: ")
    sigla = prompt_str("Sigla do Instituto: ")
    res = instituto.create_instituto(cursor, nome, sigla)
    conn.commit()
    print_result(res)


# ── 3. Create Curso ───────────────────────────────────────────────────────────

def menu_create_curso(cursor: sqlite3.Cursor, conn: sqlite3.Connection):
    print("\n--- Create Curso ---")
    nome = prompt_str("Nome do Curso: ")
    id_inst = prompt_int("ID do Instituto: ")
    res = curso.create_curso(cursor, nome, id_inst)
    conn.commit()
    print_result(res)


# ── 4. Create Matéria ─────────────────────────────────────────────────────────

def menu_create_materia(cursor: sqlite3.Cursor, conn: sqlite3.Connection):
    print("\n--- Create Matéria ---")
    nome = prompt_str("Nome da Matéria: ")
    id_inst = prompt_int("ID do Instituto: ")
    ch = prompt_int("Carga Horária (múltiplo de 16, ex: 64, 80, 96): ")
    res = materia.create_materia(cursor, nome, id_inst, ch)
    conn.commit()
    print_result(res)


# ── 5. Create Professor ───────────────────────────────────────────────────────

def menu_create_professor(cursor: sqlite3.Cursor, conn: sqlite3.Connection):
    print("\n--- Create Professor ---")
    nome = prompt_str("Nome do Professor: ")
    id_inst = prompt_int("ID do Instituto: ")
    area = prompt_str("Área de Atuação: ")
    res = professor.create_prof(cursor, nome, id_inst, area)
    conn.commit()
    print_result(res)


# ── 6. Create Aluno ───────────────────────────────────────────────────────────

def menu_create_aluno(cursor: sqlite3.Cursor, conn: sqlite3.Connection):
    print("\n--- Create Aluno ---")
    nome = prompt_str("Nome do Aluno: ")
    cpf = prompt_str("CPF do Aluno (11 dígitos): ")
    id_cur = prompt_int("ID do Curso: ")
    res = aluno.create_aluno(cursor, nome, cpf, id_cur)
    conn.commit()
    print_result(res)


# ── 7. Menu Aluno ─────────────────────────────────────────────────────────────

def menu_aluno(cursor: sqlite3.Cursor, conn: sqlite3.Connection):
    while True:
        print("\n" + "="*40)
        print("          🎓 MENU DO ALUNO")
        print("="*40)
        print("1 - Aluno name (Consultar Dados do Aluno)")
        print("2 - Aluno taxa_aprovacao")
        print("3 - Aluno media_geral")
        print("4 - Aluno periodo")
        print("5 - Aluno frequencia")
        print("6 - Buscar ID do Aluno por CPF")
        print("7 - Deletar Aluno")
        print("0 - Voltar ao Menu Principal")
        print("="*40)

        op = prompt_str("Escolha uma opção: ")

        if op == '1':
            id_val, cpf_val = prompt_id_or_cpf()
            if id_val is not None:
                cursor.execute("SELECT id, nome, cpf, id_cur, sem_ing FROM aluno WHERE id = ?", (id_val,))
            elif cpf_val is not None:
                cursor.execute("SELECT id, nome, cpf, id_cur, sem_ing FROM aluno WHERE cpf = ?", (cpf_val,))
            else:
                continue
            row = cursor.fetchone()
            if row:
                print(f"\n✓ Aluno encontrado:")
                print(f"  ID: {row[0]}")
                print(f"  Nome: {row[1]}")
                print(f"  CPF: {row[2]}")
                print(f"  ID Curso: {row[3]}")
                print(f"  Semestre de Ingresso: {row[4]}\n")
            else:
                print("\n✗ Aluno não encontrado.\n")

        elif op == '2':
            id_val, cpf_val = prompt_id_or_cpf()
            if id_val is not None or cpf_val is not None:
                res = aluno.taxa_aprovacao(cursor, id=id_val, cpf=cpf_val)
                print_result(res)

        elif op == '3':
            id_val, cpf_val = prompt_id_or_cpf()
            if id_val is not None or cpf_val is not None:
                res = aluno.media_geral(cursor, id=id_val, cpf=cpf_val)
                print_result(res)

        elif op == '4':
            id_val, cpf_val = prompt_id_or_cpf()
            if id_val is not None or cpf_val is not None:
                res = aluno.periodo_aluno(cursor, id=id_val, cpf=cpf_val)
                print_result(res)

        elif op == '5':
            id_val, cpf_val = prompt_id_or_cpf()
            if id_val is not None or cpf_val is not None:
                id_turma = prompt_int("ID da Turma: ")
                res = aluno.frequencia(cursor, id=id_val, cpf=cpf_val, id_turma=id_turma)
                print_result(res)

        elif op == '6':
            cpf = prompt_str("Digite o CPF do aluno: ")
            res = aluno.id_aluno(cursor, cpf)
            if res and not isinstance(res, tuple):
                print(f"\n✓ ID do Aluno: {res}\n")
            else:
                print("\n✗ Aluno não encontrado com este CPF.\n")

        elif op == '7':
            cpf = prompt_str("Digite o CPF do aluno a deletar: ")
            res = aluno.delete_aluno(cursor, cpf)
            conn.commit()
            print_result(res)

        elif op == '0':
            break
        else:
            print("Opção inválida. Tente novamente.")


# ── 8. Menu Turma ─────────────────────────────────────────────────────────────

def menu_turma(cursor: sqlite3.Cursor, conn: sqlite3.Connection):
    while True:
        print("\n" + "="*40)
        print("          📚 MENU DE TURMAS")
        print("="*40)
        print("1 - Create Turma")
        print("2 - Buscar ID da Turma")
        print("3 - Reservar Vagas para Curso (turma_reserva)")
        print("4 - Preencher Turmas (fill_turmas)")
        print("5 - Finalizar Semestre / Turmas (finish_turmas)")
        print("0 - Voltar ao Menu Principal")
        print("="*40)

        op = prompt_str("Escolha uma opção: ")

        if op == '1':
            id_prof = prompt_int("ID do Professor: ")
            local = prompt_str("Local / Sala: ")
            id_mat = prompt_int("ID da Matéria: ")
            hor = prompt_str("Horário (ex: 24M12, 35T123): ")
            n_vagas = prompt_int("Número de Vagas (0-120): ")
            res = turma.create_turma(cursor, id_prof, local, id_mat, hor, n_vagas)
            conn.commit()
            print_result(res)

        elif op == '2':
            id_prof = prompt_int("ID do Professor: ")
            hor = prompt_str("Horário: ")
            id_mat = prompt_int("ID da Matéria (opcional, pressione Enter para ignorar): ", allow_empty=True)
            res = turma.id_turma(cursor, id_prof=id_prof, hor=hor, id_mat=id_mat)
            if isinstance(res, int) and res > 0:
                print(f"\n✓ ID da Turma encontrada: {res}\n")
            else:
                print_result(res)

        elif op == '3':
            id_turma_val = prompt_int("ID da Turma: ")
            id_cur = prompt_int("ID do Curso: ")
            n_vagas = prompt_int("Número de Vagas Reservadas: ")
            res = turma_reserva.create_turma_reseva(cursor, id_turma_val, id_cur, n_vagas)
            conn.commit()
            print_result(res)

        elif op == '4':
            period_str = prompt_str("Período de matrícula oficial? (s/n): ").lower()
            mat_period = (period_str == 's' or period_str == 'sim')
            res = turma.fill_turmas(cursor, mat_period)
            conn.commit()
            print_result(res)

        elif op == '5':
            print("Finalizando turmas do semestre atual...")
            res = turma.finish_turmas(cursor)
            conn.commit()
            print_result(res)

        elif op == '0':
            break
        else:
            print("Opção inválida. Tente novamente.")


# ── 9. Menu Matrícula ─────────────────────────────────────────────────────────

def menu_matricula(cursor: sqlite3.Cursor, conn: sqlite3.Connection):
    while True:
        print("\n" + "="*40)
        print("          📝 MENU DE MATRÍCULAS")
        print("="*40)
        print("1 - Solicitar Matrícula em Turma")
        print("2 - Buscar ID da Solicitação de Matrícula")
        print("3 - Deletar Solicitação de Matrícula")
        print("0 - Voltar ao Menu Principal")
        print("="*40)

        op = prompt_str("Escolha uma opção: ")

        if op == '1':
            id_aluno = prompt_int("ID do Aluno: ")
            id_turma = prompt_int("ID da Turma: ")
            period_str = prompt_str("Período de matrícula oficial? (s/n): ").lower()
            mat_period = (period_str == 's' or period_str == 'sim')
            res = matricula.create_matricula_request(cursor, id_aluno, id_turma, mat_period)
            conn.commit()
            print_result(res)

        elif op == '2':
            id_aluno = prompt_int("ID do Aluno: ")
            id_turma = prompt_int("ID da Turma: ")
            status = prompt_str("Status (opcional, ex: requested, granted): ", allow_empty=True)
            res = matricula.id_matricula(cursor, id_aluno=id_aluno, id_turma=id_turma, status=status or None)
            if isinstance(res, int) and res > 0:
                print(f"\n✓ ID da Matrícula: {res}\n")
            else:
                print_result(res)

        elif op == '3':
            print("Deletar por:")
            print("  1 - ID da solicitação")
            print("  2 - ID Aluno + ID Turma")
            del_op = prompt_str("Escolha: ")
            if del_op == '1':
                id_req = prompt_int("ID da Solicitação: ")
                res = matricula.delete_matricula_request(cursor, id=id_req)
            elif del_op == '2':
                id_aluno = prompt_int("ID do Aluno: ")
                id_turma = prompt_int("ID da Turma: ")
                res = matricula.delete_matricula_request(cursor, id_aluno=id_aluno, id_turma=id_turma)
            else:
                print("Opção inválida.")
                continue
            conn.commit()
            print_result(res)

        elif op == '0':
            break
        else:
            print("Opção inválida. Tente novamente.")


# ── 10. Menu Notas e Frequência ───────────────────────────────────────────────

def menu_notas_freq(cursor: sqlite3.Cursor, conn: sqlite3.Connection):
    while True:
        print("\n" + "="*40)
        print("      📊 NOTAS E FREQUÊNCIA")
        print("="*40)
        print("1 - Lançar / Atualizar Nota (set_grade)")
        print("2 - Lançar Presença / Falta (lancar_presenca)")
        print("3 - Consultar Frequência de Aluno em Turma")
        print("4 - Buscar ID de Registro de Frequência")
        print("0 - Voltar ao Menu Principal")
        print("="*40)

        op = prompt_str("Escolha uma opção: ")

        if op == '1':
            id_aluno = prompt_int("ID do Aluno: ")
            id_turma = prompt_int("ID da Turma: ")
            nome_grade = prompt_str("Identificador da Nota (ex: P1, P2, NF): ")
            grade = prompt_float("Nota (0.0 a 10.0): ")
            res = aluno_turma.set_grade(cursor, id_aluno, id_turma, nome_grade, grade)
            conn.commit()
            print_result(res)

        elif op == '2':
            id_aluno = prompt_int("ID do Aluno: ")
            id_turma = prompt_int("ID da Turma: ")
            status = prompt_str("Status ('present' ou 'absent'): ").lower()
            res = freq.lancar_presenca(cursor, id_aluno, id_turma, status)
            conn.commit()
            print_result(res)

        elif op == '3':
            id_val, cpf_val = prompt_id_or_cpf()
            if id_val is not None or cpf_val is not None:
                id_turma = prompt_int("ID da Turma: ")
                res = aluno.frequencia(cursor, id=id_val, cpf=cpf_val, id_turma=id_turma)
                print_result(res)

        elif op == '4':
            id_aluno = prompt_int("ID do Aluno: ")
            id_turma = prompt_int("ID da Turma: ")
            day = prompt_str("Data da Aula (YYYY-MM-DD): ")
            res = freq.id_freq(cursor, id_aluno=id_aluno, id_turma=id_turma, day=day)
            if isinstance(res, int) and res > 0:
                print(f"\n✓ ID do Registro de Frequência: {res}\n")
            else:
                print_result(res)

        elif op == '0':
            break
        else:
            print("Opção inválida. Tente novamente.")


# ── 11. Menu Cancelamento de Turma ────────────────────────────────────────────

def menu_cancelamento(cursor: sqlite3.Cursor, conn: sqlite3.Connection):
    while True:
        print("\n" + "="*40)
        print("    🚫 CANCELAMENTO DE DISCIPLINA")
        print("="*40)
        print("1 - Solicitar Cancelamento de Turma")
        print("2 - Resolver Solicitação de Cancelamento")
        print("3 - Buscar ID de Solicitação de Cancelamento")
        print("0 - Voltar ao Menu Principal")
        print("="*40)

        op = prompt_str("Escolha uma opção: ")

        if op == '1':
            id_aluno = prompt_int("ID do Aluno: ")
            id_turma = prompt_int("ID da Turma: ")
            reason = prompt_str("Justificativa do cancelamento: ")
            res = aluno_turma_cancel_request.cancel_aluno_turma_request(cursor, id_aluno, id_turma, reason)
            conn.commit()
            print_result(res)

        elif op == '2':
            id_solic = prompt_int("ID da Solicitação de Cancelamento: ")
            veredito_str = prompt_str("Deferir cancelamento? (s/n): ").lower()
            deferido = (veredito_str == 's' or veredito_str == 'sim')
            res = aluno_turma_cancel_request.cancel_aluno_turma_resolve(cursor, id_solic, deferido)
            conn.commit()
            print_result(res)

        elif op == '3':
            id_aluno = prompt_int("ID do Aluno: ")
            id_turma = prompt_int("ID da Turma: ")
            res = aluno_turma_cancel_request.id_aluno_turma_cancel_request(cursor, id_aluno=id_aluno, id_turma=id_turma)
            if isinstance(res, int) and res > 0:
                print(f"\n✓ ID da Solicitação de Cancelamento: {res}\n")
            else:
                print_result(res)

        elif op == '0':
            break
        else:
            print("Opção inválida. Tente novamente.")


# ── 12. Menu Matriz Curricular & Requisitos ────────────────────────────────────

def menu_matriz(cursor: sqlite3.Cursor, conn: sqlite3.Connection):
    while True:
        print("\n" + "="*40)
        print("  📖 MATRIZ CURRICULAR E REQUISITOS")
        print("="*40)
        print("1 - Associar Matéria ao Curso (mat_curso)")
        print("2 - Criar Pré-requisito / Co-requisito (mat_reqs)")
        print("3 - Buscar ID da Matéria no Curso (id_mat_curso)")
        print("4 - Buscar ID de Pré-requisito (id_mat_reqs)")
        print("0 - Voltar ao Menu Principal")
        print("="*40)

        op = prompt_str("Escolha uma opção: ")

        if op == '1':
            id_mat = prompt_int("ID da Matéria: ")
            id_cur = prompt_int("ID do Curso: ")
            periodo = prompt_int("Período de Fluxo Ideal (1-10): ")
            res = mat_curso.create_mat_curso(cursor, id_mat, id_cur, periodo)
            conn.commit()
            print_result(res)

        elif op == '2':
            id_reqstt = prompt_int("ID da Matéria Alvo (com requisito): ")
            id_reqsid = prompt_int("ID da Matéria Requisitada (necessária): ")
            tipo = prompt_str("Tipo ('pre' para pré-requisito ou 'co' para co-requisito): ").lower()
            res = mat_reqs.create_mat_reqs(cursor, id_reqstt, id_reqsid, tipo)
            conn.commit()
            print_result(res)

        elif op == '3':
            id_mat = prompt_int("ID da Matéria: ")
            id_cur = prompt_int("ID do Curso: ")
            res = mat_curso.id_mat_curso(cursor, id_mat=id_mat, id_cur=id_cur)
            if isinstance(res, int) and res > 0:
                print(f"\n✓ ID do mat_curso: {res}\n")
            else:
                print_result(res)

        elif op == '4':
            id_reqstt = prompt_int("ID da Matéria Alvo: ")
            id_reqsid = prompt_int("ID da Matéria Requisitada: ")
            res = mat_reqs.id_mat_reqs(cursor, id_mat_reqstt=id_reqstt, id_mat_reqsid=id_reqsid)
            if isinstance(res, int) and res > 0:
                print(f"\n✓ ID do mat_reqs: {res}\n")
            else:
                print_result(res)

        elif op == '0':
            break
        else:
            print("Opção inválida. Tente novamente.")


# ── Main Loop ─────────────────────────────────────────────────────────────────

def main():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    cursor = conn.cursor()

    try:
        while True:
            sem_atual = date_funcs.get_current_semester()
            print("\n" + "="*50)
            print(f"       🎓 UNIVERSITY SYSTEM (Semestre: {sem_atual})")
            print("="*50)
            print("1  - Create University (Inicializar Tabelas)")
            print("2  - Create Institute")
            print("3  - Create Curso")
            print("4  - Create Matéria")
            print("5  - Create Professor")
            print("6  - Create Aluno")
            print("7  - Aluno (Consultas, Notas, Frequência, Taxa de Aprovação)")
            print("8  - Turma (Criação, Reserva, fill_turmas, finish_turmas)")
            print("9  - Matrícula (Solicitações de Inscrição)")
            print("10 - Notas e Frequência (Lançamentos e Verificações)")
            print("11 - Cancelamento de Disciplina (Solicitação e Parecer)")
            print("12 - Matriz Curricular e Pré-requisitos")
            print("0  - Sair")
            print("="*50)

            op = prompt_str("Escolha uma opção: ")

            if op == '1':
                create_university(cursor, conn)
            elif op == '2':
                menu_create_institute(cursor, conn)
            elif op == '3':
                menu_create_curso(cursor, conn)
            elif op == '4':
                menu_create_materia(cursor, conn)
            elif op == '5':
                menu_create_professor(cursor, conn)
            elif op == '6':
                menu_create_aluno(cursor, conn)
            elif op == '7':
                menu_aluno(cursor, conn)
            elif op == '8':
                menu_turma(cursor, conn)
            elif op == '9':
                menu_matricula(cursor, conn)
            elif op == '10':
                menu_notas_freq(cursor, conn)
            elif op == '11':
                menu_cancelamento(cursor, conn)
            elif op == '12':
                menu_matriz(cursor, conn)
            elif op == '0':
                print("\nEncerrando o University System. Até logo!\n")
                break
            else:
                print("Opção inválida. Por favor, escolha um número válido.")
    finally:
        conn.close()


if __name__ == '__main__':
    main()

