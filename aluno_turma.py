import sqlite3
import json
import date_funcs

def _create_table_aluno_turma (cursor: sqlite3.Cursor) :
    cursor.execute(
        '''CREATE TABLE IF NOT EXISTS aluno_turma (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            id_aluno INTEGER NOT NULL,
            id_turma INTEGER NOT NULL,
            notas TEXT,
            status TEXT NOT NULL,
            FOREIGN KEY (id_turma) REFERENCES turma(id) ON DELETE CASCADE ON UPDATE CASCADE,
            FOREIGN KEY (id_aluno) REFERENCES aluno(id) ON DELETE CASCADE ON UPDATE CASCADE,
            CONSTRAINT unique_aluno_turma UNIQUE (id_turma, id_aluno)
        )'''
    )

def set_grade (cursor: sqlite3.Cursor, id_aluno: int, id_turma: int, nome_grade: str, grade: float) :
    if 0 <= grade <= 10 :
        try:
            cursor.execute('SELECT nome, cpf FROM aluno WHERE id = ?', (id_aluno,))
            row = cursor.fetchone()
            if not row:
                return False, f"Aluno with ID {id_aluno} does not exist"
            nome_aluno = row[0]
            cpf_aluno = row[1]
            cursor.execute('SELECT id_mat, sem FROM turma WHERE id = ?', (id_turma,))
            row = cursor.fetchone()
            if not row:
                return False, f"Turma with ID {id_turma} does not exist"
            id_mat = row[0]
            sem = row[1]
            current_sem = date_funcs.get_current_semester() 
            if current_sem != sem :
                return False, f'Nao e possivel configurar notas de alunos da turma "{id_turma}" de {sem} em {current_sem}'
            cursor.execute(
                'SELECT notas, status FROM aluno_turma WHERE id_turma = ? AND id_aluno = ?',
                (id_turma, id_aluno)
                )
            row = cursor.fetchone()
            if not row:
                return False, f"aluno_turma with ID {id_aluno} - {id_turma} does not exist"
            notas_json = row[0]
            status = row[1]
            if status == 'canceled':
                return False, f'Aluno {nome_aluno} cancelou a turma {id_turma}!'
            notas = json.loads(notas_json)
            notas[nome_grade] = grade
            cursor.execute('UPDATE aluno_turma SET notas = ? WHERE id_aluno = ? AND id_turma = ?', 
                           (json.dumps(notas), id_aluno, id_turma,))
            return True, f"aluno_turma '{nome_aluno} - {cpf_aluno} - {id_turma} - {sem} - {id_mat} - {nome_grade}:{grade}' updated"
        except sqlite3.Error as e:
            return False, f"Database error: {e}"    
    else :
        return False, f"Grade need to be in [0, 10]!"

def id_aluno_turma (cursor: sqlite3.Cursor, id_aluno: int = None, id_turma: int = None, cpf: str = None) :
    try :
        if id_aluno is None and cpf is not None :
            cursor.execute('SELECT id FROM aluno WHERE cpf = ?', (cpf,))
            row = cursor.fetchone()
            if not row : return 0
            id_aluno = row[0]
        if id_aluno is None or id_turma is None :
            return None, 'Both id_aluno (or cpf) and id_turma must be provided!'
        cursor.execute('SELECT id FROM aluno_turma WHERE id_aluno = ? AND id_turma = ?', (int(id_aluno), int(id_turma)))
        result = cursor.fetchone()
        if result : return result[0]
        return 0
    except (ValueError, TypeError) :
        return False, 'Invalid id'
    except sqlite3.Error as e :
        return False, f"Database error: {e}"