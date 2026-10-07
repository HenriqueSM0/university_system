import sqlite3

def _create_table_instituto (cursor: sqlite3.Cursor) :
    cursor.execute(
        '''CREATE TABLE IF NOT EXISTS instituto (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            sigla TEXT NOT NULL,
            CONSTRAINT unique_nome UNIQUE (nome),
            CONSTRAINT unique_sigla UNIQUE (sigla)
        )'''
    )

def create_instituto (cursor: sqlite3.Cursor, name: str, sigla: str) :
    try:
        cursor.execute('''
            INSERT INTO instituto (nome, sigla) 
            VALUES (?, ?)
        ''', (name, sigla))
        return True, f"Institute '{name}' created with ID {cursor.lastrowid}"
    except sqlite3.IntegrityError as e:
        if "unique_nome" in str(e) or "instituto.nome" in str(e):
            return False, f"Institute '{name}' already exists"
        elif "unique_sigla" in str(e) or "instituto.sigla" in str(e):
            return False, f"Sigla '{sigla}' already exists"
        else :
            return False, f"Database constraint error: {e}"
    except sqlite3.Error as e:
        return False, f"Database error: {e}"

def id_instituto (cursor: sqlite3.Cursor, id: int = None, nome: str = None, sigla: str = None) :
    try :
        if id is not None : 
            id_inst = int(id)
            cursor.execute('''SELECT id FROM instituto WHERE id = ?''', (id_inst,))
        elif nome is not None :
            cursor.execute('''SELECT id FROM instituto WHERE nome = ?''', (nome,))
        elif sigla is not None :
            cursor.execute('''SELECT id FROM instituto WHERE sigla = ?''', (sigla,))
        else : 
            return None, 'Either id, nome or sigla must be provided!'
        result = cursor.fetchone()  
        if result: return result[0] 
        return 0  
    except (ValueError, TypeError) :
        return None, 'Invalid id'    
    except sqlite3.Error as e:
       return None, f"Database error: {e}"

def delete_instituto (cursor: sqlite3.Cursor, id: int = None, nome: str = None, sigla: str = None) :
    if id is not None :
        try :
            id_inst = int(id)
        except (ValueError, TypeError) :
            return False, 'Invalid id'
        cursor.execute('''SELECT nome, sigla FROM instituto WHERE id = ?''', (id_inst,))
        row = cursor.fetchone()
        if not row : 
            return False, f"Instituto com ID {id_inst} não encontrado"
        sigla_inst = row[1]
        nome_inst = row[0]
    elif nome is not None :
        cursor.execute('''SELECT id, sigla FROM instituto WHERE nome = ?''', (nome,))
        row = cursor.fetchone()
        if not row : 
            return False, f"Instituto com nome {nome} não encontrado"
        id_inst = row[0]
        sigla_inst = row[1]
        nome_inst = nome
    elif sigla is not None :
        cursor.execute('''SELECT id, nome FROM instituto WHERE sigla = ?''', (sigla,))
        row = cursor.fetchone()
        if not row : 
            return False, f"Instituto com sigla {sigla} não encontrado"
        id_inst = row[0]
        sigla_inst = sigla
        nome_inst = row[1]
    else : 
        return False, 'Either id, nome or sigla must be provided!'
    try: 
        cursor.execute('DELETE FROM instituto WHERE id = ?', (id_inst,))
        return True, f"Instituto '{nome_inst} - {sigla_inst}' deletado com sucesso"
    except sqlite3.Error as e:
        return False, f"Database error: {e}"