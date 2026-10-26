import sqlite3
import date_funcs
import horario

def _create_table_freq (cursor: sqlite3.Cursor) :
    cursor.execute(
        '''CREATE TABLE IF NOT EXISTS freq (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            id_aluno_turma INTEGER NOT NULL,
            day DATE NOT NULL,
            status TEXT NOT NULL,
            FOREIGN KEY (id_aluno_turma) REFERENCES aluno_turma(id) ON DELETE CASCADE ON UPDATE CASCADE,
            CONSTRAINT unique_aluno_turma_day UNIQUE (id_aluno_turma, day)
        )'''
    )

def lancar_presenca (cursor: sqlite3.Cursor, id_aluno: int, id_turma: int, status: str) :
    if status not in ['present', 'absent'] :
        return False, 'Status may be present or absent'
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
            return False, f'Nao e possivel registrar presenca na turma "{id_turma}" de {sem} em {current_sem}'
        cursor.execute('SELECT id, status FROM aluno_turma WHERE id_aluno = ? AND id_turma = ?', (id_aluno, id_turma,))
        row = cursor.fetchone()
        if not row:
            return False, f"aluno_turma with Aluno {cpf_aluno} - {nome_aluno} and Turma {id_turma} does not exist"
        id_aluno_turma = row[0]
        status_aluno = row[1]
        if status_aluno != 'in_progress' :
            return False, f'O aluno {nome_aluno} - {cpf_aluno} nao esta mais cursando a turma {id_turma}'
        cursor.execute('''SELECT hor, materia.nome FROM
        turma JOIN materia ON turma.id_mat = materia.id
        WHERE turma.id = ?''', (id_turma,))
        row = cursor.fetchone()
        hor = row[0]
        mat_nome = row[1]
        hor_pres = date_funcs.current_day()[1]
        if 'I8' in hor_pres:
            return False, 'Fora do horário de aula'
        elif horario.Horario.conflitant(hor_pres, hor) :
            return False, 'A chamada deve ser feita durante a aula!'
        cursor.execute('''INSERT INTO freq(id_aluno_turma, day, status) VALUES
            (?, DATE('now'), ?)''', (id_aluno_turma, status))
        return True, f'{nome_aluno} - {cpf_aluno} {status} in turma {id_turma} - {mat_nome} - {hor_pres} at {date_funcs.current_day()[0]}'
    except sqlite3.IntegrityError as e:
        if "unique_aluno_turma_day" in str(e) or ("UNIQUE" in str(e) and "freq" in str(e)):
            return False, f"Presenca de '{nome_aluno} - {cpf_aluno}' ja registrada hoje na turma {id_turma}"
        else :
            return False, f"Database constraint error: {e}"
    except sqlite3.Error as e:
        return False, f"Database error: {e}"

def id_freq (cursor: sqlite3.Cursor, id_aluno_turma: int = None, day: str = None, id_aluno: int = None, id_turma: int = None) :
    try :
        if id_aluno_turma is None and id_aluno is not None and id_turma is not None :
            cursor.execute('SELECT id FROM aluno_turma WHERE id_aluno = ? AND id_turma = ?', (int(id_aluno), int(id_turma)))
            row = cursor.fetchone()
            if not row : return 0
            id_aluno_turma = row[0]
        if id_aluno_turma is None or day is None :
            return None, 'Both id_aluno_turma (or id_aluno + id_turma) and day must be provided!'
        cursor.execute('SELECT id FROM freq WHERE id_aluno_turma = ? AND day = ?', (int(id_aluno_turma), day))
        result = cursor.fetchone()
        if result : return result[0]
        return 0
    except (ValueError, TypeError) :
        return False, 'Invalid id'
    except sqlite3.Error as e :
        return False, f"Database error: {e}"