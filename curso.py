import sqlite3

def _create_table_curso (cursor: sqlite3.Cursor) :
    cursor.execute(
        '''CREATE TABLE IF NOT EXISTS curso (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            id_inst INTEGER NOT NULL,
            CONSTRAINT unique_nome UNIQUE (nome),
            FOREIGN KEY (id_inst) REFERENCES instituto(id) ON DELETE CASCADE ON UPDATE CASCADE
        )'''
    )

def create_curso (cursor: sqlite3.Cursor, name: str, id_inst: int) :
    try:
        cursor.execute('SELECT id FROM instituto WHERE id = ?', (id_inst,))
        if not cursor.fetchone():
            return False, f"Institute with ID {id_inst} does not exist"
        cursor.execute('''
            INSERT INTO curso (nome, id_inst) 
            VALUES (?, ?)
        ''', (name, id_inst))
        return True, f"Curso '{name}' created with ID {cursor.lastrowid}"
    except sqlite3.IntegrityError as e:
        if "unique_nome" in str(e):
            return False, f"Curso '{name}' already exists"
        return False, f"Constraint error: {e}"
    except sqlite3.Error as e:
        return False, f"Database error: {e}"   

def id_curso (cursor: sqlite3.Cursor, nome: str) :
    cursor.execute('''SELECT id FROM curso WHERE nome = ?''', (nome,))
    result = cursor.fetchone()  
    try: 
        if result: return result[0] 
        return 0      
    except sqlite3.Error as e:
        return None, f"Database error: {e}"

def delete_curso (cursor: sqlite3.Cursor, method: str, param: str) :
    if method == 'id' :
        try :
            id_curso = int(param)
        except :
            return False, 'Invalid id'
        cursor.execute('''SELECT nome FROM curso WHERE id = ?''', (id_curso,))
        row = cursor.fetchone()
        if not row:
            return False, f"Curso com ID {id_curso} não encontrado"
        nome_curso = row[1]
    elif method == 'name' :
        cursor.execute('''SELECT id FROM curso WHERE nome = ?''', (param,))
        row = cursor.fetchone()
        if not row:
            return False, f"Curso com nome {param} não encontrado"
        nome_curso = param
        id_curso = row[0]
    else :
        return None, 'Param must be nome_mat or id_mat!'
    try:
        cursor.execute('DELETE FROM curso WHERE id = ?', (id_curso,))
        return True, f"Curso '{nome_curso}' deletado com sucesso"
    except sqlite3.Error as e:
        return False, f"Database error: {e}"