import sqlite3

def _create_table_aluno (cursor: sqlite3.Cursor) :
    cursor.execute(
        '''CREATE TABLE IF NOT EXISTS aluno (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            cpf CHAR(11) NOT NULL,
            CONSTRAINT unique_cpf UNIQUE (cpf),
            id_cur INTEGER NOT NULL,
            sem_ing TEXT NOT NULL
            FOREIGN KEY (id_cur) REFERENCES cur(id) ON DELETE CASCADE ON UPDATE CASCADE,
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
    cursor.execute('''SELECT id FROM aluno WHERE cpf = ?''', (cpf))
    result = cursor.fetchone()  
    try: 
        if result: return result[0] 
        return 0      
    except sqlite3.Error as e:
        return None, f"Database error: {e}"

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
    