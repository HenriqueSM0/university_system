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
        if "unique_nome" in str(e) or "curso.nome" in str(e):
            return False, f"Curso '{name}' already exists"
        else :
            return False, f"Constraint error: {e}"
    except sqlite3.Error as e:
        return False, f"Database error: {e}"   

def id_curso (cursor: sqlite3.Cursor, nome: str) :
    try:
        cursor.execute('''SELECT id FROM curso WHERE nome = ?''', (nome,))
        result = cursor.fetchone()  
        if result: return result[0] 
        return 0      
    except sqlite3.Error as e:
        return None, f"Database error: {e}"

def get_min_periods (cursor: sqlite3.Cursor, id: int = None, name: str = None) :
    if id is not None :
        try :
            id_curso = int(id)
        except (ValueError, TypeError) :
            return -1, 'Invalid id'
        cursor.execute('''SELECT nome FROM curso WHERE id = ?''', (id_curso,))
        row = cursor.fetchone()
        if not row:
            return -1, f"Curso com ID {id_curso} não encontrado"
        nome_curso = row[0]
    elif name is not None :
        cursor.execute('''SELECT id FROM curso WHERE nome = ?''', (name,))
        row = cursor.fetchone()
        if not row:
            return -1, f"Curso com nome {name} não encontrado"
        nome_curso = name
        id_curso = row[0]
    else :
        return -2, 'Either id or name must be provided!'
    try:
        cursor.execute('SELECT COALESCE(MAX(periodo_fluxo), 0) FROM mat_curso WHERE id_cur = ?', (id_curso,))
        min_anos = int(cursor.fetchone()[0])
        if min_anos == 0:
            return 0, f'O curso {nome_curso} nao tem sua grade definida.'
        return min_anos, f'O curso {nome_curso} tem um minimo de {min_anos} periodos e maximo de {1.5 * min_anos}'
    except sqlite3.Error as e:
            return -2, f"Database error: {e}"
    
def delete_curso (cursor: sqlite3.Cursor, id: int = None, name: str = None) :
    if id is not None :
        try :
            id_curso = int(id)
        except (ValueError, TypeError) :
            return False, 'Invalid id'
        cursor.execute('''SELECT nome FROM curso WHERE id = ?''', (id_curso,))
        row = cursor.fetchone()
        if not row:
            return False, f"Curso com ID {id_curso} não encontrado"
        nome_curso = row[0]
    elif name is not None :
        cursor.execute('''SELECT id FROM curso WHERE nome = ?''', (name,))
        row = cursor.fetchone()
        if not row:
            return False, f"Curso com nome {name} não encontrado"
        nome_curso = name
        id_curso = row[0]
    else :
        return False, 'Either id or name must be provided!'
    try:
        cursor.execute('DELETE FROM curso WHERE id = ?', (id_curso,))
        return True, f"Curso '{nome_curso}' deletado com sucesso"
    except sqlite3.Error as e:
        return False, f"Database error: {e}"