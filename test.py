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
import date_funcs

DB_PATH = 'university.db'

# ── helpers ────────────────────────────────────────────────────────────────────

def check(label: str, result):
    """Print the result of every function call."""
    ok, msg = result if isinstance(result, tuple) else (result, '')
    status = '✓' if ok else '✗'
    print(f'  [{status}] {label}: {msg}')
    return ok

# ── table creation (dependency order) ─────────────────────────────────────────

def create_all_tables(cursor: sqlite3.Cursor):
    print('\n=== Creating tables ===')
    # Level 1
    instituto._create_table_instituto(cursor)
    print('  [✓] instituto')
    # Level 2
    curso._create_table_curso(cursor)
    print('  [✓] curso')
    materia._create_table_materia(cursor)
    print('  [✓] materia')
    professor._create_table_professor(cursor)
    print('  [✓] professor')
    # Level 3
    aluno._create_table_aluno(cursor)
    print('  [✓] aluno')
    mat_curso._create_table_mat_curso(cursor)
    print('  [✓] mat_curso')
    mat_reqs._create_table_mat_reqs(cursor)
    print('  [✓] mat_reqs')
    turma._create_table_turma(cursor)
    print('  [✓] turma')
    # Level 4
    turma_reserva._create_table_turma_reserva(cursor)
    print('  [✓] turma_reserva')
    aluno_turma._create_table_aluno_turma(cursor)
    print('  [✓] aluno_turma')
    # Level 5
    matricula._create_table_matricula(cursor)
    print('  [✓] matricula')

# ── population ─────────────────────────────────────────────────────────────────

def populate_database(cursor: sqlite3.Cursor):
    sem = date_funcs.get_current_semester()
    print(f'\n=== Populating database (semestre: {sem}) ===')

    # 1. Instituto
    print('\n-- Instituto --')
    check('create_instituto ICMC',
          instituto.create_instituto(cursor, 'Instituto de Ciências Matemáticas', 'ICMC'))

    id_inst = instituto.id_instituto(cursor, nome='Instituto de Ciências Matemáticas')
    if not isinstance(id_inst, tuple):
        print(f'  [✓] id_instituto: {id_inst}')
    else:
        print(f'  [✗] id_instituto: {id_inst[1]}')
        return

    # 2. Curso
    print('\n-- Curso --')
    check('create_curso Ciência da Computação',
          curso.create_curso(cursor, 'Ciência da Computação', id_inst))

    id_cur = curso.id_curso(cursor, 'Ciência da Computação')
    print(f'  [✓] id_curso: {id_cur}')

    # 3. Matérias
    print('\n-- Matérias --')
    check('create_materia Cálculo I',
          materia.create_materia(cursor, 'Cálculo I', id_inst, 96))
    check('create_materia Álgebra Linear',
          materia.create_materia(cursor, 'Álgebra Linear', id_inst, 64))

    id_calc = materia.id_materia(cursor, 'Cálculo I')
    id_alg  = materia.id_materia(cursor, 'Álgebra Linear')
    print(f'  [✓] id_materia Cálculo I: {id_calc}')
    print(f'  [✓] id_materia Álgebra Linear: {id_alg}')

    # 4. Professor
    print('\n-- Professor --')
    check('create_prof Prof. José',
          professor.create_prof(cursor, 'José Silva', id_inst, 'Matemática', sem))

    cursor.execute("SELECT id FROM professor WHERE nome = 'José Silva'")
    row = cursor.fetchone()
    id_prof = row[0] if row else None
    print(f'  [✓] id_professor: {id_prof}')

    # 5. Aluno — Maria (the main character)
    print('\n-- Aluno --')
    check('create_aluno Maria',
          aluno.create_aluno(cursor, 'Maria Oliveira', '98765432100', id_cur, sem))

    id_maria = aluno.id_aluno(cursor, cpf='98765432100')
    if not isinstance(id_maria, tuple):
        print(f'  [✓] id_aluno Maria: {id_maria}')
    else:
        print(f'  [✗] id_aluno: {id_maria[1]}')
        return

    # 6. mat_curso — attach matérias to curso with período de fluxo
    print('\n-- mat_curso --')
    check('create_mat_curso Cálculo I → CC período 1',
          mat_curso.create_mat_curso(cursor, id_calc, id_cur, 1))
    check('create_mat_curso Álgebra Linear → CC período 1',
          mat_curso.create_mat_curso(cursor, id_alg, id_cur, 1))

    # 7. Turma — Cálculo I (96h = 6 dias × M234 / a 16h por aula: 2M1234 3M1234)
    #    96 h / 16 h_por_slot = 6 slots por semana → "2 3 M1234" = 8 slots, tentemos
    #    Horário: "246 M1234" = dias 2,4,6 × 4 slots tarde = 12 slots × ? não bate
    #    Turma exige ch == horario.ch.  96 / 16 = 6 slots.
    #    Horário "246 M12" = 3 dias × 2 slots = 6 slots → ch = 6 × 16 = 96 ✓
    print('\n-- Turma --')
    hor_calc = '246M12'   # seg/qua/sex, manhã slots 1-2  → 6 × 16 = 96 h
    # Álgebra tem 64 h → 4 slots: "24T12" = 2 × 2 = 4 × 16 = 64 ✓
    hor_alg  = '24T12'

    check('create_turma Cálculo I',
          turma.create_turma(cursor, id_prof, 'Sala 101', id_calc, hor_calc, sem, 40))
    check('create_turma Álgebra Linear',
          turma.create_turma(cursor, id_prof, 'Sala 102', id_alg, hor_alg, sem, 30))

    id_t_calc = turma.id_turma(cursor, id_mat=id_calc, id_prof=id_prof, hor=hor_calc)
    id_t_alg  = turma.id_turma(cursor, id_mat=id_alg,  id_prof=id_prof, hor=hor_alg)
    print(f'  [✓] id_turma Cálculo I: {id_t_calc}')
    print(f'  [✓] id_turma Álgebra Linear: {id_t_alg}')

    # 8. turma_reserva — reserve vagas for CC on Cálculo I turma
    print('\n-- turma_reserva --')
    check('create_turma_reserva CC na turma Cálculo I',
          turma_reserva.create_turma_reseva(cursor, id_t_calc, id_cur, 20))

    # 9. matricula request — Maria solicita Cálculo I
    print('\n-- Matricula --')
    check('create_matricula_request Maria → Cálculo I',
          matricula.create_matricula_request(cursor, id_maria, id_t_calc, mat_period=True))

    # 10. período e média de Maria (recém-criada, sem disciplinas concluídas)
    print('\n-- Consultas --')
    per, msg_per = aluno.periodo_aluno(cursor, id=id_maria)
    print(f'  [✓] periodo_aluno Maria: período {per} — {msg_per}')

    md, msg_md = aluno.media_geral(cursor, id=id_maria)
    print(f'  [✓] media_geral Maria: {msg_md}')

    tx, msg_tx = aluno.taxa_aprovacao(cursor, id=id_maria)
    print(f'  [✓] taxa_aprovacao Maria: {msg_tx}')

    min_per, msg_mp = curso.get_min_periods(cursor, id=id_cur)
    print(f'  [✓] get_min_periods CC: {msg_mp}')

    # 11. aluno_turma — process the matricula requests (fill_turmas handles priority + enrollment)
    print('\n-- aluno_turma --')
    check('fill_turmas (mat_period=True)',
          aluno_turma.fill_turmas(cursor, mat_period=True))

    check('set_grade Maria NF=8.5',
          aluno_turma.set_grade(cursor, id_maria, id_t_calc, 'NF', 8.5))

    # 12. delete matricula request by aluno+turma combo (for Álgebra, which was never requested)
    #     — request one first, then delete it
    check('create_matricula_request Maria → Álgebra',
          matricula.create_matricula_request(cursor, id_maria, id_t_alg, mat_period=False))

    check('delete_matricula_request Maria → Álgebra (by id_aluno+id_turma)',
          matricula.delete_matricula_request(cursor, id_aluno=id_maria, id_turma=id_t_alg))

# ── main ───────────────────────────────────────────────────────────────────────

def main():
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
        print(f'Removed existing {DB_PATH}')

    con = sqlite3.connect(DB_PATH)
    con.execute('PRAGMA foreign_keys = ON')
    cursor = con.cursor()

    try:
        create_all_tables(cursor)
        populate_database(cursor)
        con.commit()
        print('\n=== Done. university.db committed. ===')
    except Exception as e:
        con.rollback()
        print(f'\n[ERRO] {e}')
        raise
    finally:
        con.close()

if __name__ == '__main__':
  main()
