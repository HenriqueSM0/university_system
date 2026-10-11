import sqlite3
import ai_funcs as AI
import date_funcs

def _create_table_aluno_turma_cancel_request (cursor: sqlite3.Cursor) :
    cursor.execute(
        '''CREATE TABLE IF NOT EXISTS aluno_turma_cancel_request (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            id_aluno_turma INTEGER NOT NULL,
            result TEXT NOT NULL,
            reason TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, 
            resolved_at TIMESTAMP,
            FOREIGN KEY (id_aluno_turma) REFERENCES aluno_turma(id) ON DELETE CASCADE ON UPDATE CASCADE
        )'''
    )

def cancel_aluno_turma_request (cursor: sqlite3.Cursor, id_aluno: int, id_turma: int, reason: str) :
    try :
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
        sem = row[1]
        current_sem = date_funcs.get_current_semester() 
        if current_sem != sem :
            return False, f'Nao e possivel cancelar turma "{id_turma}" de {sem} em {current_sem}'
        cursor.execute('SELECT id, status FROM aluno_turma WHERE id_aluno = ? AND id_turma = ?', (id_aluno, id_turma,))
        row = cursor.fetchone()
        if not row:
            return False, f"aluno_turma with Aluno {cpf_aluno} - {nome_aluno} and Turma {id_turma} does not exist"
        id_aluno_turma = row[0]
        status = row[1]
        if status != 'in_progress' :
            return False, f'O aluno {nome_aluno} - {cpf_aluno} nao esta mais cursando a turma {id_turma}'
        valid_reason = AI.Ai_funcs().verify_aluno_turma_cancel(reason)
        if not int(valid_reason) :
            return False, 'Esta nao e uma razao considerada valida para o cancelamento da disciplina!'
        cursor.execute('''INSERT INTO aluno_turma_cancel_request(id_aluno_turma, result, reason) 
            VALUES (?, 'in_progress', ?)''', (id_aluno_turma, reason,))
        return True, f'Solicitacao de cancelamento em analise - fique atento, entraremos em contato!'
    except sqlite3.Error as e:
        return False, f"Database error: {e}"    
    