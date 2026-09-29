import sqlite3

def _create_table_materia (cursor: sqlite3.Cursor) :
    cursor.execute(
        '''CREATE TABLE IF NOT EXISTS materia (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            CONSTRAINT unique_nome UNIQUE (nome),
            id_inst INTEGER NOT NULL,
            carga_hor INTEGER NOT NULL,
            FOREIGN KEY (id_inst) REFERENCES instituto(id) ON DELETE CASCADE ON UPDATE CASCADE,
        )'''
    )

def create_materia (cursor: sqlite3.Cursor, name: str, id_inst: int, carga_hor: int) :
    if carga_hor % 16 != 0 and 16 <= carga_hor <= 1792 :
        try:
            cursor.execute('SELECT id, nome FROM instituto WHERE id = ?', (id_inst,))
            inst = cursor.fetchone()
            if not inst :
                return False, f"Instituto with ID {id_inst} does not exist"                    
            else :
                nome_inst = inst[1]
            cursor.execute('''
                INSERT INTO materia (nome, id_inst, carga_hor) 
                VALUES (?, ?, ?)
            ''', (name, id_inst, carga_hor))
            return True, f"Materia '{name} - {nome_inst}' created with ID {cursor.lastrowid}"
        except sqlite3.IntegrityError as e:
            if "unique_nome" in str(e):
                return False, f"Materia '{name}' already exists"
            return False, f"Constraint error: {e}"
        except sqlite3.Error as e:
            return False, f"Database error: {e}" 
    else :
        return False, f'Invalid number of hours' 

def id_materia (cursor: sqlite3.Cursor, nome: str) :
    cursor.execute('''SELECT id FROM materia WHERE nome = ?''', (nome))
    result = cursor.fetchone()  
    try: 
        if result: return result[0] 
        return 0      
    except sqlite3.Error as e:
        return None, f"Database error: {e}"

def delete_materia (cursor: sqlite3.Cursor, method: str, param: str) :
    if method == 'id' :
        try :
            id_mat = int(param)
        except :
            return False, 'Invalid id'
        cursor.execute('''SELECT nome, id_inst FROM materia WHERE nome = ?''', (id_mat,))
        row = cursor.fetchone()
        if not row : 
            return False, f"Materia com ID {id_mat} não encontrada"
        id_inst = row[1]
        nome_mat = row[0]
    elif method == 'nome' :
        cursor.execute('''SELECT id, id_inst FROM materia WHERE nome = ?''', (param,))
        row = cursor.fetchone()
        if not row : 
            return False, f"materia com nome {param} não encontrado"
        id_inst = row[1]
        nome_mat = param
    else : 
        return None, 'Param must be nome or sigla!'
    try: 
        cursor.execute('''SELECT sigla FROM instituto WHERE id = ?''', (id_inst,))
        sigla_inst = cursor.fetchone()[0]
        cursor.execute('DELETE FROM materia WHERE id = ?', (id_mat,))
        return True, f"Materia '{nome_mat} - {sigla_inst}' deletada com sucesso"
    except sqlite3.Error as e:
        return False, f"Database error: {e}"