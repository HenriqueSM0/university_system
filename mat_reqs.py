import sqlite3

def _create_table_mat_reqs (cursor: sqlite3.Cursor) :
    cursor.execute(
        '''CREATE TABLE IF NOT EXISTS mat_reqs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            id_mat_reqstt INTEGER NOT NULL,
            id_mat_reqsid INTEGER NOT NULL,
            type CHAR NOT NULL,
            FOREIGN KEY (id_mat_reqstt) REFERENCES materia(id) ON DELETE CASCADE ON UPDATE CASCADE,
            FOREIGN KEY (id_mat_reqsid) REFERENCES materia(id) ON DELETE CASCADE ON UPDATE CASCADE,
            CONSTRAINT unique_mat_reqs UNIQUE (id_mat_reqstt, id_mat_reqsid)
        )'''
    )

def create_mat_reqs (cursor: sqlite3.Cursor, id_mat_reqstt: int, id_mat_reqsid: int, type_param: str) :
    try :
        cursor.execute('SELECT nome FROM materia WHERE id = ?', (id_mat_reqstt,))
        row = cursor.fetchone()
        if not row :
            return False, f"Materia with ID {id_mat_reqstt} does not exist"
        name_reqstt = row[0]
        cursor.execute('SELECT nome FROM materia WHERE id = ?', (id_mat_reqsid,))
        row = cursor.fetchone()
        if not row :
            return False, f"Materia with ID {id_mat_reqsid} does not exist"
        if id_mat_reqstt == id_mat_reqsid :
            return False, f'id_mat_reqstt and id_mat_reqsid need to be different'
        name_reqsid = row[0]
        if type_param != 'pre' and type_param != 'co' : 
            return False, "Type need to be 'pre' or 'core'"
        cursor.execute(
            '''SELECT mat_curso.periodo_fluxo, mat_curso_copy.periodo_fluxo, mat_curso.id_cur FROM mat_curso JOIN mat_curso AS mat_curso_copy
            ON (mat_curso.id_cur = mat_curso_copy.id_cur)
            WHERE (mat_curso.id_mat = ? AND mat_curso_copy.id_mat = ?) 
            AND (mat_curso.periodo_fluxo <= mat_curso_copy.periodo_fluxo)''', (id_mat_reqstt, id_mat_reqsid)
        )
        rows = cursor.fetchall()
        if rows :
            return_str = ''
            for row in rows :
                if row[0] < row[1] or type_param == 'pre' :
                    return_str += f'{name_reqstt} is from {row[0]} period, while {name_reqsid} is from {row[1]} in curso with ID {row[2]}\n'
            if return_str != '' :        
                return_str = return_str.removesuffix('\n')
                return False, return_str 
        cursor.execute('''
            INSERT INTO mat_reqs (id_mat_reqstt, id_mat_reqsid, type) 
            VALUES (?, ?, ?)
            ''', (id_mat_reqstt, id_mat_reqsid, type_param))
        return True, f"mat_reqs '{name_reqstt} - {name_reqsid}' - type : {type_param}' created with ID {cursor.lastrowid}"
    except sqlite3.IntegrityError as e:
        if "unique_mat_reqs" in str(e) or ("UNIQUE" in str(e) and "mat_reqs" in str(e)):
            return False, f"mat_reqs '{name_reqstt} - {name_reqsid} - type : {type_param}' already exists"
        else :
            return False, f"Database constraint error: {e}"
    except sqlite3.Error as e:
        return False, f"Database error: {e}"

def id_mat_reqs (cursor: sqlite3.Cursor, id_mat_reqstt: int = None, id_mat_reqsid: int = None, mat_reqstt_name: str = None, mat_reqsid_name: str = None) :
    try :
        if id_mat_reqstt is None and mat_reqstt_name is not None :
            cursor.execute('SELECT id FROM materia WHERE nome = ?', (mat_reqstt_name,))
            row = cursor.fetchone()
            if not row : return 0
            id_mat_reqstt = row[0]
        if id_mat_reqsid is None and mat_reqsid_name is not None :
            cursor.execute('SELECT id FROM materia WHERE nome = ?', (mat_reqsid_name,))
            row = cursor.fetchone()
            if not row : return 0
            id_mat_reqsid = row[0]
        if id_mat_reqstt is None or id_mat_reqsid is None :
            return None, 'Both id_mat_reqstt and id_mat_reqsid (or their names) must be provided!'
        cursor.execute('SELECT id FROM mat_reqs WHERE id_mat_reqstt = ? AND id_mat_reqsid = ?', (int(id_mat_reqstt), int(id_mat_reqsid)))
        result = cursor.fetchone()
        if result : return result[0]
        return 0
    except (ValueError, TypeError) :
        return False, 'Invalid id'
    except sqlite3.Error as e :
        return False, f"Database error: {e}"