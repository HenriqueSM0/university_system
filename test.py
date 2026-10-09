import sqlite3
import os
import random

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
    instituto._create_table_instituto(cursor)
    print('  [✓] instituto')
    curso._create_table_curso(cursor)
    print('  [✓] curso')
    materia._create_table_materia(cursor)
    print('  [✓] materia')
    professor._create_table_professor(cursor)
    print('  [✓] professor')
    aluno._create_table_aluno(cursor)
    print('  [✓] aluno')
    mat_curso._create_table_mat_curso(cursor)
    print('  [✓] mat_curso')
    mat_reqs._create_table_mat_reqs(cursor)
    print('  [✓] mat_reqs')
    turma._create_table_turma(cursor)
    print('  [✓] turma')
    turma_reserva._create_table_turma_reserva(cursor)
    print('  [✓] turma_reserva')
    aluno_turma._create_table_aluno_turma(cursor)
    print('  [✓] aluno_turma')
    matricula._create_table_matricula(cursor)
    print('  [✓] matricula')

# ── data ───────────────────────────────────────────────────────────────────────

INSTITUTOS = [
    ('Instituto de Ciências Matemáticas e de Computação', 'ICMC'),
    ('Instituto de Física de São Carlos', 'IFSC'),
    ('Instituto de Química de São Carlos', 'IQSC'),
]

CURSOS = [
    ('Ciência da Computação', 'CC', 1),
    ('Engenharia de Computação', 'EC', 1),
    ('Sistemas de Informação', 'SI', 1),
    ('Matemática Aplicada', 'MA', 1),
    ('Física', 'FIS', 2),
    ('Química', 'QUI', 3),
]

MATERIAS = [
    # (nome, id_inst, carga_hor)
    ('Cálculo I', 1, 96),
    ('Cálculo II', 1, 96),
    ('Cálculo III', 1, 96),
    ('Álgebra Linear', 1, 64),
    ('Geometria Analítica', 1, 64),
    ('Matemática Discreta', 1, 64),
    ('Programação I', 1, 80),
    ('Programação II', 1, 80),
    ('Estrutura de Dados', 1, 80),
    ('Banco de Dados', 1, 80),
    ('Redes de Computadores', 1, 80),
    ('Sistemas Operacionais', 1, 80),
    ('Engenharia de Software', 1, 64),
    ('Inteligência Artificial', 1, 80),
    ('Compiladores', 1, 80),
    ('Física I', 2, 96),
    ('Física II', 2, 96),
    ('Física III', 2, 96),
    ('Física Experimental I', 2, 64),
    ('Química Geral', 3, 80),
    ('Química Orgânica', 3, 80),
    ('Química Analítica', 3, 80),
]

PROFESSORES = [
    ('José Silva', 1, 'Matemática'),
    ('Maria Santos', 1, 'Computação'),
    ('Carlos Oliveira', 1, 'Computação'),
    ('Ana Costa', 1, 'Matemática'),
    ('Pedro Almeida', 2, 'Física'),
    ('Juliana Lima', 2, 'Física'),
    ('Roberto Souza', 3, 'Química'),
    ('Fernanda Rocha', 3, 'Química'),
    ('Lucas Martins', 1, 'Computação'),
    ('Patrícia Ferreira', 1, 'Matemática'),
]

ALUNOS = [
    ('Ana Beatriz', '11111111111'),
    ('Bruno Costa', '22222222222'),
    ('Carla Dias', '33333333333'),
    ('Daniel Souza', '44444444444'),
    ('Eduarda Lima', '55555555555'),
    ('Felipe Rocha', '66666666666'),
    ('Gabriela Alves', '77777777777'),
    ('Henrique Silva', '88888888888'),
    ('Isabela Martins', '99999999999'),
    ('João Pedro', '10101010101'),
    ('Karina Oliveira', '11111111112'),
    ('Lucas Ferreira', '12121212121'),
    ('Mariana Santos', '13131313131'),
    ('Nicolas Almeida', '14141414141'),
    ('Olívia Costa', '15151515151'),
    ('Paulo Henrique', '16161616161'),
    ('Queren Dias', '17171717171'),
    ('Rafael Lima', '18181818181'),
    ('Sofia Rocha', '19191919191'),
    ('Thiago Alves', '20202020202'),
    ('Ursula Martins', '21212121212'),
    ('Vitor Silva', '22222222223'),
    ('Wagner Souza', '23232323232'),
    ('Xênia Costa', '24242424242'),
    ('Yuri Oliveira', '25252525252'),
    ('Zélia Ferreira', '26262626262'),
    ('Alice Santos', '27272727272'),
    ('Bernardo Lima', '28282828282'),
    ('Camila Rocha', '29292929292'),
    ('Diego Almeida', '30303030303'),
    ('Elisa Martins', '31313131313'),
    ('Fábio Costa', '32323232323'),
    ('Giovana Silva', '33333333333'),
    ('Heitor Souza', '34343434343'),
    ('Iara Oliveira', '35353535353'),
    ('Júlia Ferreira', '36363636363'),
    ('Kauã Santos', '37373737373'),
    ('Larissa Lima', '38383838383'),
    ('Miguel Rocha', '39393939393'),
    ('Nicole Almeida', '40404040404'),
    ('Otávio Martins', '41414141414'),
    ('Priscila Costa', '42424242424'),
    ('Raquel Silva', '43434343434'),
    ('Samuel Souza', '44444444445'),
    ('Tânia Oliveira', '45454545454'),
    ('Ubiratã Ferreira', '46464646464'),
    ('Vitória Santos', '47474747474'),
    ('Wesley Lima', '48484848484'),
    ('Yasmin Rocha', '49494949494'),
    ('Zoe Almeida', '50505050505'),
]

# ── population ─────────────────────────────────────────────────────────────────

def populate_database(cursor: sqlite3.Cursor):
    sem = date_funcs.get_current_semester()
    print(f'\n=== Populating database (semestre: {sem}) ===')

    # 1. Institutos
    print('\n-- Institutos --')
    for nome, sigla in INSTITUTOS:
        check(f'create_instituto {sigla}',
              instituto.create_instituto(cursor, nome, sigla))

    # 2. Cursos
    print('\n-- Cursos --')
    for nome, sigla, id_inst in CURSOS:
        check(f'create_curso {sigla}',
              curso.create_curso(cursor, nome, id_inst))

    # 3. Matérias
    print('\n-- Matérias --')
    for nome, id_inst, ch in MATERIAS:
        check(f'create_materia {nome}',
              materia.create_materia(cursor, nome, id_inst, ch))

    # 4. Professores
    print('\n-- Professores --')
    for nome, id_inst, area in PROFESSORES:
        check(f'create_prof {nome}',
              professor.create_prof(cursor, nome, id_inst, area, sem))

    # 5. Alunos
    print('\n-- Alunos --')
    for i, (nome, cpf) in enumerate(ALUNOS):
        id_cur = (i % len(CURSOS)) + 1  # Distribui entre os cursos
        check(f'create_aluno {nome}',
              aluno.create_aluno(cursor, nome, cpf, id_cur, sem))

    # 6. mat_curso — vincular matérias aos cursos
    print('\n-- mat_curso --')
    # CC: matérias de computação + matemática básica
    for id_mat, periodo in [
        (1, 1), (2, 2), (3, 3),   # Cálculo I, II, III
        (4, 1), (5, 1),            # Álgebra, Geometria
        (6, 2),                    # Discreta
        (7, 1), (8, 2), (9, 3),    # Programação I, II, Estrutura
        (10, 4), (11, 4), (12, 4), # BD, Redes, SO
        (13, 5), (14, 5), (15, 6), # ES, IA, Compiladores
    ]:
        check(f'mat_curso {id_mat} → CC p{periodo}',
              mat_curso.create_mat_curso(cursor, id_mat, 1, periodo))

    # EC: similar
    for id_mat, periodo in [
        (1, 1), (2, 2), (4, 1), (5, 1),
        (7, 1), (8, 2), (9, 3),
        (16, 2), (17, 3), (18, 4), (19, 2),
    ]:
        check(f'mat_curso {id_mat} → EC p{periodo}',
              mat_curso.create_mat_curso(cursor, id_mat, 2, periodo))

    # SI: similar
    for id_mat, periodo in [
        (1, 1), (4, 1), (7, 1), (8, 2),
        (10, 3), (11, 4), (12, 4), (13, 3),
    ]:
        check(f'mat_curso {id_mat} → SI p{periodo}',
              mat_curso.create_mat_curso(cursor, id_mat, 3, periodo))

    # MA: matemática
    for id_mat, periodo in [
        (1, 1), (2, 2), (3, 3), (4, 1), (5, 1), (6, 2),
    ]:
        check(f'mat_curso {id_mat} → MA p{periodo}',
              mat_curso.create_mat_curso(cursor, id_mat, 4, periodo))

    # FIS: física
    for id_mat, periodo in [
        (1, 1), (2, 2), (4, 1),
        (16, 1), (17, 2), (18, 3), (19, 2),
    ]:
        check(f'mat_curso {id_mat} → FIS p{periodo}',
              mat_curso.create_mat_curso(cursor, id_mat, 5, periodo))

    # QUI: química
    for id_mat, periodo in [
        (1, 1), (4, 1),
        (20, 1), (21, 2), (22, 3),
    ]:
        check(f'mat_curso {id_mat} → QUI p{periodo}',
              mat_curso.create_mat_curso(cursor, id_mat, 6, periodo))

    # 7. mat_reqs — pré-requisitos
    print('\n-- mat_reqs --')
    # Cálculo II precisa de Cálculo I
    check('pre: Cálculo II → Cálculo I',
          mat_reqs.create_mat_reqs(cursor, 2, 1, 'pre'))
    # Cálculo III precisa de Cálculo II
    check('pre: Cálculo III → Cálculo II',
          mat_reqs.create_mat_reqs(cursor, 3, 2, 'pre'))
    # Estrutura de Dados precisa de Programação II
    check('pre: Estrutura → Programação II',
          mat_reqs.create_mat_reqs(cursor, 9, 8, 'pre'))
    # Banco de Dados precisa de Estrutura
    check('pre: BD → Estrutura',
          mat_reqs.create_mat_reqs(cursor, 10, 9, 'pre'))
    # Redes precisa de SO
    check('pre: Redes → SO',
          mat_reqs.create_mat_reqs(cursor, 11, 12, 'pre'))
    # Física II precisa de Física I
    check('pre: Física II → Física I',
          mat_reqs.create_mat_reqs(cursor, 17, 16, 'pre'))
    # Física III precisa de Física II
    check('pre: Física III → Física II',
          mat_reqs.create_mat_reqs(cursor, 18, 17, 'pre'))
    # Física Experimental I precisa de Física I (co)
    check('co: Física Exp I → Física I',
          mat_reqs.create_mat_reqs(cursor, 19, 16, 'co'))
    # Química Orgânica precisa de Química Geral
    check('pre: Q. Orgânica → Q. Geral',
          mat_reqs.create_mat_reqs(cursor, 21, 20, 'pre'))
    # Química Analítica precisa de Q. Geral
    check('pre: Q. Analítica → Q. Geral',
          mat_reqs.create_mat_reqs(cursor, 22, 20, 'pre'))

    # 8. Turmas
    print('\n-- Turmas --')
    # Mapear matérias para professores
    PROF_MAT = {
        1: 1, 2: 1, 3: 1, 4: 4, 5: 4, 6: 4,
        7: 2, 8: 2, 9: 3, 10: 9, 11: 3, 12: 9,
        13: 2, 14: 9, 15: 3,
        16: 5, 17: 5, 18: 6, 19: 6,
        20: 7, 21: 8, 22: 7,
    }
    
    # Horários válidos (carga horária compatível)
    HORARIOS = {
        96: ['246M12', '35T12', '24M1234'],  # 6 slots
        80: ['24M12', '35T12', '246T1'],      # 5 slots
        64: ['24T12', '35M12', '2M1234'],     # 4 slots
    }
    
    turmas_criadas = []
    for id_mat, id_prof in PROF_MAT.items():
        cursor.execute('SELECT carga_hor FROM materia WHERE id = ?', (id_mat,))
        ch = cursor.fetchone()[0]
        hor = HORARIOS.get(ch, HORARIOS[80])[0]  # Pega o primeiro horário
        
        cursor.execute('SELECT nome FROM materia WHERE id = ?', (id_mat,))
        nome_mat = cursor.fetchone()[0]
        
        check(f'create_turma {nome_mat}',
              turma.create_turma(cursor, id_prof, f'Sala {id_mat}01', 
                                 id_mat, hor, sem, random.randint(20, 60)))
        
        # Pegar o ID da turma criada
        id_t = turma.id_turma(cursor, id_mat=id_mat, id_prof=id_prof, hor=hor)
        if not isinstance(id_t, tuple) and id_t > 0:
            turmas_criadas.append(id_t)

    print(f'  [✓] {len(turmas_criadas)} turmas criadas')

    # 9. turma_reserva — reservas
    print('\n-- turma_reserva --')
    # Reservar vagas para os cursos nas turmas
    for id_t in turmas_criadas:
        cursor.execute('SELECT id_mat FROM turma WHERE id = ?', (id_t,))
        id_mat = cursor.fetchone()[0]
        
        # Buscar cursos que têm essa matéria
        cursor.execute(
            'SELECT id_cur FROM mat_curso WHERE id_mat = ?',
            (id_mat,)
        )
        cursos = cursor.fetchall()
        
        for (id_cur,) in cursos[:2]:  # Reserva para até 2 cursos
            check(f'reserva turma {id_t} → curso {id_cur}',
                  turma_reserva.create_turma_reseva(cursor, id_t, id_cur, 
                                                     random.randint(5, 15)))

    # 10. matricula requests
    print('\n-- Matrículas --')
    # Cada aluno solicita 3-5 turmas
    for i, (nome, cpf) in enumerate(ALUNOS):
        id_aluno = aluno.id_aluno(cursor, cpf=cpf)
        if isinstance(id_aluno, tuple):
            continue
        
        # Escolher turmas aleatórias
        turmas_aluno = random.sample(turmas_criadas, min(5, len(turmas_criadas)))
        
        for id_t in turmas_aluno:
            # Verificar se a matéria é do curso do aluno
            cursor.execute('''
                SELECT a.id_cur, t.id_mat 
                FROM aluno a, turma t 
                WHERE a.id = ? AND t.id = ?
            ''', (id_aluno, id_t))
            row = cursor.fetchone()
            if not row:
                continue
            
            id_cur_aluno, id_mat_turma = row
            
            # Verificar se a matéria está no curso do aluno
            cursor.execute(
                'SELECT 1 FROM mat_curso WHERE id_cur = ? AND id_mat = ?',
                (id_cur_aluno, id_mat_turma)
            )
            if not cursor.fetchone():
                continue
            
            # Tentar matricular
            check(f'matricula {nome} → turma {id_t}',
                  matricula.create_matricula_request(cursor, id_aluno, id_t, 
                                                     mat_period=random.choice([True, False])))

    # ── 10.5 TESTE DE DUPLICIDADE ─────────────────────────────────────────
    print('\n-- TESTE: Duplicidade no fill_turmas --')
    
    # Pegar a turma 1 (Cálculo I) e a turma 2 (Álgebra Linear)
    # Verificar quem tem matrícula 'requested' na turma 1
    cursor.execute('''
        SELECT m.id, m.id_aluno, a.nome, t.id_mat
        FROM matricula m
        JOIN aluno a ON a.id = m.id_aluno
        JOIN turma t ON t.id = m.id_turma
        WHERE m.id_turma = 1 AND m.status = 'requested'
    ''')
    matriculas_t1 = cursor.fetchall()
    print(f'  Matrículas "requested" na turma 1: {len(matriculas_t1)}')
    for row in matriculas_t1:
        print(f'    id={row[0]}, id_aluno={row[1]}, nome={row[2]}, id_mat={row[3]}')
    
    # Verificar quem tem matrícula 'requested' na turma 2
    cursor.execute('''
        SELECT m.id, m.id_aluno, a.nome, t.id_mat
        FROM matricula m
        JOIN aluno a ON a.id = m.id_aluno
        JOIN turma t ON t.id = m.id_turma
        WHERE m.id_turma = 2 AND m.status = 'requested'
    ''')
    matriculas_t2 = cursor.fetchall()
    print(f'  Matrículas "requested" na turma 2: {len(matriculas_t2)}')
    for row in matriculas_t2:
        print(f'    id={row[0]}, id_aluno={row[1]}, nome={row[2]}, id_mat={row[3]}')
    
    # Ver alunos que têm matrícula em AMBAS as turmas (1 e 2)
    cursor.execute('''
        SELECT DISTINCT m1.id_aluno, a.nome
        FROM matricula m1
        JOIN matricula m2 ON m1.id_aluno = m2.id_aluno
        JOIN aluno a ON a.id = m1.id_aluno
        WHERE m1.id_turma = 1 AND m2.id_turma = 2
          AND m1.status = 'requested' AND m2.status = 'requested'
    ''')
    alunos_ambas = cursor.fetchall()
    print(f'  Alunos com matrícula em AMBAS as turmas (1 e 2): {len(alunos_ambas)}')
    for row in alunos_ambas:
        print(f'    id_aluno={row[0]}, nome={row[1]}')
    
    # ── FIM TESTE ─────────────────────────────────────────────────────────

    # 11. fill_turmas
    print('\n-- fill_turmas --')
    check('fill_turmas (mat_period=True)',
          aluno_turma.fill_turmas(cursor, mat_period=True))

    # 12. set_grade — notas aleatórias
    print('\n-- set_grade --')
    cursor.execute('SELECT id_aluno, id_turma FROM aluno_turma')
    matriculas = cursor.fetchall()
    
    for id_aluno, id_turma in matriculas[:30]:  # Só 30 para não demorar
        # Nota aleatória
        if random.random() < 0.7:  # 70% de chance de ter NF
            nf = round(random.uniform(0, 10), 1)
            check(f'set_grade {id_aluno} turma {id_turma} NF={nf}',
                  aluno_turma.set_grade(cursor, id_aluno, id_turma, 'NF', nf))

    # 13. Consultas finais
    print('\n-- Consultas finais --')
    for i, (nome, cpf) in enumerate(ALUNOS[:5]):  # 5 alunos
        id_aluno = aluno.id_aluno(cursor, cpf=cpf)
        if isinstance(id_aluno, tuple):
            continue
        
        per, msg_per = aluno.periodo_aluno(cursor, id=id_aluno)
        print(f'  [✓] periodo_aluno {nome}: {msg_per}')
        
        md, msg_md = aluno.media_geral(cursor, id=id_aluno)
        print(f'  [✓] media_geral {nome}: {msg_md}')
        
        tx, msg_tx = aluno.taxa_aprovacao(cursor, id=id_aluno)
        print(f'  [✓] taxa_aprovacao {nome}: {msg_tx}')

    # 14. Estatísticas finais
    print('\n-- Estatísticas --')
    for table in ['instituto', 'curso', 'materia', 'professor', 'aluno', 
                  'turma', 'turma_reserva', 'aluno_turma', 'matricula', 
                  'mat_curso', 'mat_reqs']:
        cursor.execute(f'SELECT COUNT(*) FROM {table}')
        count = cursor.fetchone()[0]
        print(f'  [✓] {table}: {count} registros')

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