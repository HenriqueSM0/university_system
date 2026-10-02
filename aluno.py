import sqlite3
import date_funcs as df
import json

def _create_table_aluno (cursor: sqlite3.Cursor) :
    cursor.execute(
        '''CREATE TABLE IF NOT EXISTS aluno (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            cpf CHAR(11) NOT NULL,
            id_cur INTEGER NOT NULL,
            sem_ing TEXT NOT NULL,
            CONSTRAINT unique_cpf UNIQUE (cpf),
            FOREIGN KEY (id_cur) REFERENCES curso(id) ON DELETE CASCADE ON UPDATE CASCADE
        )'''
    )

def create_aluno (cursor: sqlite3.Cursor, name: str, cpf: str, id_cur: int, sem_ing: str) :
    if len(cpf) != 11 : 
        return False, 'Invalid CPF'
    if sem_ing[-1] not in ['1', '2'] and sem_ing[-2] != '.' :
        return False, 'Invalid semester' 
    try:
        cursor.execute('SELECT id, nome FROM curso WHERE id = ?', (id_cur,))
        cur = cursor.fetchone()
        if not cur:
            return False, f"Curso with ID {id_cur} does not exist"
        else : 
            nome_cur = cur[1]
        cursor.execute('''
            INSERT INTO aluno (nome, cpf, id_cur, sem_ing) 
            VALUES (?, ?, ?, ?)
        ''', (name, cpf, id_cur, sem_ing))
        return True, f"Aluno '{name} - {cpf} - {nome_cur} - ' created with ID {cursor.lastrowid}"
    except sqlite3.IntegrityError as e:
        if "unique_cpf" in str(e):
            return False, f"CPF '{cpf}' already exists"
        return False, f"Constraint error: {e}"
    except sqlite3.Error as e:
        return False, f"Database error: {e}"   

def id_aluno (cursor: sqlite3.Cursor, cpf: str) :
    if len(cpf) != 11 : 
        return None
    cursor.execute('''SELECT id FROM aluno WHERE cpf = ?''', (cpf,))
    result = cursor.fetchone()  
    try: 
        if result: return result[0] 
        return 0      
    except sqlite3.Error as e:
        return None, f"Database error: {e}"

def periodo_aluno (cursor: sqlite3.Cursor, id: int = None, cpf: str = None) :
    if id is not None :
        try :
            id_aluno = int(id)
        except (ValueError, TypeError) :
            return -1, 'Invalid id'
        cursor.execute('''SELECT nome, cpf, sem_ing FROM aluno WHERE id = ?''', (id_aluno,))
        row = cursor.fetchone()
        if not row:
            return -1, f"Aluno com ID {id_aluno} não encontrado"
        cpf = row[1]
        sem_ing = row[2]
    elif cpf is not None :
        cursor.execute('''SELECT nome, sem_ing FROM aluno WHERE cpf = ?''', (cpf,))
        row = cursor.fetchone()
        if not row:
            return -1, f"Aluno com cpf {cpf} não encontrado"
        sem_ing = row[1]
    else :
        return 0, 'Either id or cpf must be provided!'
    nome_aluno = row[0]
    periodo = df.time_between_semesters(df.get_current_semester(), sem_ing) * 2 + 1
    return periodo, f'O aluno {nome_aluno} - {cpf} esta no periodo {periodo}' 

def media_geral (cursor: sqlite3.Cursor, id: int = None, cpf: str = None) :
    if id is not None :
        try :
            id_aluno = int(id)
        except (ValueError, TypeError) :
            return -1, 'Invalid id'
        cursor.execute('''SELECT nome, cpf FROM aluno WHERE id = ?''', (id_aluno,))
        row = cursor.fetchone()
        if not row:
            return -1, f"Aluno com ID {id_aluno} não encontrado"
        cpf = row[1]
    elif cpf is not None :
        cursor.execute('''SELECT nome, id FROM aluno WHERE cpf = ?''', (cpf,))
        row = cursor.fetchone()
        if not row:
            return -1, f"Aluno com cpf {cpf} não encontrado"
        id_aluno = row[1]
    else :
        return 0, 'Either id or cpf must be provided!'
    nome_aluno = row[0]
    cursor.execute('''
        SELECT notas, carga_horaria FROM (aluno_turma JOIN turma ON id_turma = turma.id) 
        JOIN (materia ON id_mat = materia.id)
        WHERE id_aluno = ?''', (id_aluno,))
    sum_gr = 0
    sum_ch = 0
    rows = cursor.fetchall()
    for row in rows:
        try :
            nota = json.loads(row[0])
            if 'NF' in nota :
                ch = int(row[1])
                sum_ch += ch
                sum_gr += float(nota['NF']) * ch 
        except (json.JSONDecodeError, TypeError) :
            continue
    if sum_ch == 0 :
        return -1, f'O aluno {nome_aluno} - {cpf} nao finalizou disciplinas ainda'
    mg = sum_gr / sum_ch
    return mg, f'O aluno {nome_aluno} - {cpf} tem média geral M = {mg}'

def delete_aluno (cursor: sqlite3.Cursor, cpf: str) :
    if len(cpf) != 11 : 
        return False
    cursor.execute('SELECT nome FROM aluno WHERE cpf = ?', (cpf,))
    row = cursor.fetchone()
    if not row:
        return False, f"Aluno com CPF {cpf} não encontrado"
    nome = row[0]
    try:
        cursor.execute('DELETE FROM aluno WHERE cpf = ?', (cpf,))
        return True, f"Aluno '{nome}' deletado com sucesso"
    except sqlite3.Error as e:
        return False, f"Database error: {e}"
    