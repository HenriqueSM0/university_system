import sqlite3
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

"""
=============================================================================
ARVORE DE TABELAS (TREE OF TABLES) POR DEPENDÊNCIA DE CHAVES ESTRANGEIRAS
=============================================================================

Nível 0 (Raiz - sem dependências):
  └── instituto

Nível 1 (Depende de Nível 0):
  ├── curso           (FK: id_inst -> instituto.id)
  ├── materia         (FK: id_inst -> instituto.id)
  └── professor       (FK: id_inst -> instituto.id)

Nível 2 (Depende de Nível 1):
  ├── aluno           (FK: id_cur -> curso.id)
  ├── mat_curso       (FK: id_mat -> materia.id, id_cur -> curso.id)
  ├── mat_reqs        (FK: id_mat_reqstt -> materia.id, id_mat_reqsid -> materia.id)
  └── turma           (FK: id_mat -> materia.id, id_prof -> professor.id)

Nível 3 (Depende de Nível 2):
  ├── turma_reserva   (FK: id_turma -> turma.id, id_cur -> curso.id)
  └── aluno_turma     (FK: id_aluno -> aluno.id, id_turma -> turma.id)
=============================================================================
"""

def create_all_tables(cursor: sqlite3.Cursor):
    print("=" * 60)
    print("1. CRIANDO AS TABELAS NA ORDEM DA ÁRVORE DE DEPENDÊNCIAS")
    print("=" * 60)
    
    # Nível 0
    instituto._create_table_instituto(cursor)
    print("  [OK] Tabela 'instituto' criada")

    # Nível 1
    curso._create_table_curso(cursor)
    print("  [OK] Tabela 'curso' criada (depende de instituto)")

    materia._create_table_materia(cursor)
    print("  [OK] Tabela 'materia' criada (depende de instituto)")

    professor._create_table_professor(cursor)
    print("  [OK] Tabela 'professor' criada (depende de instituto)")

    # Nível 2
    aluno._create_table_aluno(cursor)
    print("  [OK] Tabela 'aluno' criada (depende de curso)")

    mat_curso._create_table_mat_curso(cursor)
    print("  [OK] Tabela 'mat_curso' criada (depende de materia e curso)")

    mat_reqs._create_table_mat_reqs(cursor)
    print("  [OK] Tabela 'mat_reqs' criada (depende de materia)")

    turma._create_table_turma(cursor)
    print("  [OK] Tabela 'turma' criada (depende de materia e professor)")

    # Nível 3
    turma_reserva._create_table_turma_reserva(cursor)
    print("  [OK] Tabela 'turma_reserva' criada (depende de turma e curso)")

    aluno_turma._create_table_aluno_turma(cursor)
    print("  [OK] Tabela 'aluno_turma' criada (depende de aluno e turma)")


def populate_database(cursor: sqlite3.Cursor):
    print("\n" + "=" * 60)
    print("2. INSERINDO DADOS UTILIZANDO APENAS AS FUNÇÕES PRONTAS")
    print("   (Propagando referências: antigo -> novo, ex: Maria -> Curso -> Turma)")
    print("=" * 60)

    # 1. Instituto
    ok, msg = instituto.create_instituto(cursor, "Instituto de Informatica", "INF")
    id_inst = instituto.id_instituto(cursor, "sigla", "INF")
    print(f"1. create_instituto: success={ok} | ID={id_inst} | msg: {msg}")

    # 2. Curso (usa id_inst)
    ok, msg = curso.create_curso(cursor, "Ciencia da Computacao", id_inst)
    id_curso = curso.id_curso(cursor, "Ciencia da Computacao")
    print(f"2. create_curso: success={ok} | ID={id_curso} | msg: {msg}")

    # 3. Matéria 1 (usa id_inst)
    ok, msg = materia.create_materia(cursor, "Algoritmos e Programacao", id_inst, 64)
    id_mat1 = materia.id_materia(cursor, "Algoritmos e Programacao")
    print(f"3. create_materia (Algoritmos): success={ok} | ID={id_mat1} | msg: {msg}")

    # 4. Matéria 2 (usa id_inst)
    ok, msg = materia.create_materia(cursor, "Estruturas de Dados", id_inst, 64)
    id_mat2 = materia.id_materia(cursor, "Estruturas de Dados")
    print(f"4. create_materia (Estruturas de Dados): success={ok} | ID={id_mat2} | msg: {msg}")

    # 5. Professor (usa id_inst)
    ok, msg = professor.create_prof(cursor, "Alan Turing", id_inst, "Ciencia da Computacao", "2020.1")
    cursor.execute("SELECT id FROM professor WHERE nome = ?", ("Alan Turing",))
    id_prof = cursor.fetchone()[0]
    print(f"5. create_prof: success={ok} | ID={id_prof} | msg: {msg}")

    # 6. Aluno Maria (usa id_curso de Ciência da Computação)
    cpf_maria = "12345678901"
    ok, msg = aluno.create_aluno(cursor, "Maria Silva", cpf_maria, id_curso, "2024.1")
    id_aluno_maria = aluno.id_aluno(cursor, cpf_maria)
    print(f"6. create_aluno (Maria Silva): success={ok} | ID={id_aluno_maria} | msg: {msg}")

    # 7. Mat_Curso para Algoritmos no 1º período (usa id_mat1 e id_curso)
    ok, msg = mat_curso.create_mat_curso(cursor, id_mat1, id_curso, 1)
    print(f"7. create_mat_curso (Algoritmos no 1º sem): success={ok} | msg: {msg}")

    # 8. Mat_Curso para Estruturas de Dados no 2º período (usa id_mat2 e id_curso)
    ok, msg = mat_curso.create_mat_curso(cursor, id_mat2, id_curso, 2)
    print(f"8. create_mat_curso (Estruturas no 2º sem): success={ok} | msg: {msg}")

    # 9. Mat_Reqs: Estruturas de Dados pré-requisita Algoritmos (usa id_mat2 e id_mat1)
    ok, msg = mat_reqs.create_mat_reqs(cursor, id_mat2, id_mat1, "pre")
    print(f"9. create_mat_reqs (Estruturas pre-req Algoritmos): success={ok} | msg: {msg}")

    # 10. Turma de Algoritmos com o Prof. Alan Turing (usa id_prof e id_mat1)
    ok, msg = turma.create_turma(cursor, id_prof, "ICC Ala Sul - Sala 10", id_mat1, "24M12", "2024.1", 40)
    cursor.execute("SELECT id FROM turma WHERE id_mat = ? AND sem = ?", (id_mat1, "2024.1"))
    id_turma_alg = cursor.fetchone()[0]
    print(f"10. create_turma (Algoritmos 2024.1): success={ok} | ID={id_turma_alg} | msg: {msg}")

    # 11. Reserva de vagas da Turma para o Curso de Ciência da Computação (usa id_turma_alg e id_curso)
    ok, msg = turma_reserva.create_turma_reseva(cursor, id_turma_alg, id_curso, 20)
    print(f"11. create_turma_reseva (20 vagas para CC): success={ok} | msg: {msg}")

    # 12. Matrícula de Maria na Turma de Algoritmos (usa id_aluno_maria e id_turma_alg)
    ok, msg = aluno_turma.create_aluno_turma(cursor, id_aluno_maria, id_turma_alg)
    print(f"12. create_aluno_turma (Matricular Maria na turma): success={ok} | msg: {msg}")

    # 13. Lançamento da primeira nota de Maria na turma
    ok, msg = aluno_turma.set_grade(cursor, id_aluno_maria, id_turma_alg, "P1", 9.5)
    print(f"13. set_grade (Nota P1 da Maria): success={ok} | msg: {msg}")


def main():
    db_name = "school.db"
    conn = sqlite3.connect(db_name)
    conn.execute("PRAGMA foreign_keys = ON;")
    cursor = conn.cursor()

    try:
        create_all_tables(cursor)
        populate_database(cursor)
        conn.commit()
        print("\n" + "=" * 60)
        print(f"Banco de dados '{db_name}' estruturado e populado com sucesso!")
        print("=" * 60)
    except Exception as e:
        conn.rollback()
        print(f"\nErro durante execução: {e}")
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    main()
