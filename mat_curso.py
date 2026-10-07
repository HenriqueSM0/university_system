import sqlite3

def _create_table_mat_curso (cursor: sqlite3.Cursor) :
    cursor.execute(
        '''CREATE TABLE IF NOT EXISTS mat_curso (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            id_mat INTEGER NOT NULL,
            id_cur INTEGER NOT NULL,
            periodo_fluxo INTEGER NOT NULL,
            FOREIGN KEY (id_mat) REFERENCES materia(id) ON DELETE CASCADE ON UPDATE CASCADE,
            FOREIGN KEY (id_cur) REFERENCES curso(id) ON DELETE CASCADE ON UPDATE CASCADE,
            CONSTRAINT unique_mat_cur UNIQUE (id_mat, id_cur)
        )'''
    )

def create_mat_curso (cursor: sqlite3.Cursor, id_mat:int, id_cur:int, periodo_fluxo:int) :
    if 0 < periodo_fluxo <= 12 :
        try:
            cursor.execute('SELECT id, nome FROM curso WHERE id = ?', (id_cur,))
            cur = cursor.fetchone()
            if not cur:
                return False, f"Curso with ID {id_cur} does not exist"
            else : 
                nome_cur = cur[1]
            cursor.execute('SELECT id, nome FROM materia WHERE id = ?', (id_mat,))
            mat = cursor.fetchone()
            if not mat:
                return False, f"Materia with ID {id_mat} does not exist"
            else : 
                nome_mat = mat[1]
            cursor.execute('''
                INSERT INTO mat_curso (id_mat, id_cur, periodo_fluxo) 
                VALUES (?, ?, ?)
                ''', (id_mat, id_cur, periodo_fluxo))
            return True, f"mat_curso '{nome_cur} - {nome_mat} - {periodo_fluxo} periodo' created with ID {cursor.lastrowid}"
        except sqlite3.IntegrityError as e:
            if "unique_mat_cur" in str(e) or ("UNIQUE" in str(e) and "mat_curso" in str(e)):
                return False, f"mat_curso '{nome_cur} - {nome_mat} - {periodo_fluxo} periodo' already exists"
            else :
                return False, f"Database constraint error: {e}"
        except sqlite3.Error as e:
            return False, f"Database error: {e}"
    else :
        return False, f'Invalid flux period'    

def id_materia (cursor: sqlite3.Cursor, id_mat:int, id_cur:int) :
    try:
        cursor.execute('''SELECT id FROM mat_curso WHERE id_mat = ? AND id_cur = ?''', (id_mat, id_cur))
        result = cursor.fetchone()  
        if result: return result[0] 
        return 0      
    except sqlite3.Error as e:
        return None, f"Database error: {e}"

def delete_mat_curso (cursor: sqlite3.Cursor, id_mat: int, id_cur: int) :
    cursor.execute('''SELECT id FROM mat_curso WHERE id_mat = ? AND id_cur = ?''', (id_mat, id_cur))
    row = cursor.fetchone()
    if not row:
        return False, f'mat_curso com id_mat {id_mat} e id_cur {id_cur} não encontrado'
    id = row[0]
    try:
        cursor.execute('DELETE FROM mat_curso WHERE id = ?', (id,))
        return True, f"mat_curso '{id}' deletado com sucesso"
    except sqlite3.Error as e:
        return False, f"Database error: {e}"