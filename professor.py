import sqlite3
import date_funcs

def _create_table_professor (cursor: sqlite3.Cursor) :
    cursor.execute(
        '''CREATE TABLE IF NOT EXISTS professor (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            id_inst INTEGER NOT NULL,
            area TEXT,
            sem_ing_inicio TEXT NOT NULL,
            FOREIGN KEY (id_inst) REFERENCES instituto(id) ON DELETE CASCADE ON UPDATE CASCADE
        )'''
    )

def create_prof (cursor: sqlite3.Cursor, nome: str, id_inst: int, area: str) :
    if area.strip() == '' :
        area = None
    try:
        cursor.execute('SELECT id, nome FROM instituto WHERE id = ?', (id_inst,))
        inst = cursor.fetchone()
        if not inst :
            return False, f"Instituto with ID {id_inst} does not exist"
        else :
            nome_inst = inst[1]
        sem_ing_inicio = date_funcs.get_current_semester()
        cursor.execute('''
            INSERT INTO professor (nome, id_inst, area, sem_ing_inicio) 
            VALUES (?, ?, ?, ?)
        ''', (nome, id_inst, area, sem_ing_inicio))
        return True, f"Professor '{nome} - {nome_inst}' created with ID {cursor.lastrowid}"
    except sqlite3.IntegrityError as e:
        return False, f"Constraint error: {e}"
    except sqlite3.Error as e:
        return False, f"Database error: {e}" 

def id_professor (cursor: sqlite3.Cursor, id: int = None, nome: str = None, id_inst: int = None, area: str = None) :
    try :
        if id is not None :
            try :
                id_prof = int(id)
            except (ValueError, TypeError) :
                return False, 'Invalid id'
            cursor.execute('SELECT id FROM professor WHERE id = ?', (id_prof,))
        elif nome is not None :
            query = 'SELECT id FROM professor WHERE nome = ?'
            params = [nome]
            if id_inst is not None :
                query += ' AND id_inst = ?'
                params.append(int(id_inst))
            if area is not None :
                query += ' AND area = ?'
                params.append(area)
            cursor.execute(query, tuple(params))
        else :
            return None, 'Either id or nome must be provided!'
        result = cursor.fetchone()
        if result : return result[0]
        return 0
    except (ValueError, TypeError) :
        return False, 'Invalid id'
    except sqlite3.Error as e :
        return False, f"Database error: {e}"

def delete_professor (cursor: sqlite3.Cursor, id: int) :
    cursor.execute('SELECT nome FROM professor WHERE id = ?', (id,))
    row = cursor.fetchone()
    if not row:
        return False, f"Professor com id {id} não encontrado"
    nome = row[0]
    try:
        cursor.execute('DELETE FROM professor WHERE id = ?', (id,))
        return True, f"Professor '{nome} - {id}' deletado com sucesso"
    except sqlite3.Error as e:
        return False, f"Database error: {e}"