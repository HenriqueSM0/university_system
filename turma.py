import sqlite3
import horario as H
import ai_funcs as AI
import materia

def _create_table_turma (cursor: sqlite3.Cursor) :
    cursor.execute(
        '''CREATE TABLE IF NOT EXISTS turma (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            local TEXT NOT NULL,
            id_mat INTEGER NOT NULL,
            id_prof INTEGER NOT NULL,
            hor TEXT NOT NULL,
            sem TEXT NOT NULL,
            n_vagas INT NOT NULL,
            FOREIGN KEY (id_mat) REFERENCES materia(id) ON DELETE CASCADE ON UPDATE CASCADE,
            FOREIGN KEY (id_prof) REFERENCES professor(id) ON DELETE CASCADE ON UPDATE CASCADE
        )'''
    )

def create_turma (cursor: sqlite3.Cursor, id_prof: int, local: str, id_mat: int, hor: str, sem: str, n_vagas: int) :
    if not (0 <= n_vagas <= 120):
        return False, 'Numero de vagas e de (0-120)'
    if len(sem) < 6 or (sem[-1] not in ['1', '2']) or sem[-2] != '.' :
        return False, 'Invalid semester' 
    obj_hor = H.Horario(hor)
    if not obj_hor.array_form :
        return False, 'Invalid horario'
    try:
        obj_ai = AI.Ai_funcs()
        if not int(obj_ai.valid_local(obj_hor.formated_hor, local)) :
            return False, 'Invalid local'
        cursor.execute('SELECT id, nome, carga_hor FROM materia WHERE id = ?', (id_mat,))
        mat = cursor.fetchone()
        if not mat:
            return False, f"Materia with ID {id_mat} does not exist"
        cursor.execute('SELECT id, nome FROM professor WHERE id = ?', (id_prof,))
        prof = cursor.fetchone()
        if not prof:
            return False, f"Professor with ID {id_prof} does not exist"
        else : 
            nome_prof = prof[1]
            nome_mat = mat[1]
            ch_materia = mat[2]
            cursor.execute('SELECT hor FROM turma WHERE id_prof = ? AND sem = ?', (id_prof, sem))
            hors = cursor.fetchall()
            hors_existentes = [line[0] for line in hors]
            param_hors = hors_existentes + [obj_hor.formated_hor.strip()]
            if H.Horario.conflitant(*param_hors) :
                return False, f'Professor {nome_prof} already is on other turma at time {obj_hor.formated_hor}'
            if obj_hor.ch != ch_materia :
                return False, f'Materia {nome_mat} tem carga horaria {ch_materia}, e a turma tem {obj_hor.ch}'  
        cursor.execute('''
            INSERT INTO turma (id_prof, local, id_mat, hor, sem, n_vagas) 
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (id_prof, local, id_mat, obj_hor.formated_hor, sem, n_vagas))
        return True, f"Turma '{nome_mat} - {nome_prof} - {obj_hor.formated_hor} - {local} - {sem}' created with ID {cursor.lastrowid}"
    except sqlite3.IntegrityError as e:
        return False, f"Constraint error: {e}"
    except sqlite3.Error as e:
        return False, f"Database error: {e}" 

def id_turma (cursor: sqlite3.Cursor, id_mat: int = None, mat_name: str = None, id_prof: int = None, hor: str = None) :
    if id_mat is not None :
        try :
            id_mat_final = int(id_mat)
        except (ValueError, TypeError) :
            return False, 'Invalid id'
    elif mat_name is not None :
        id_mat_final = materia.id_materia(cursor, mat_name)
    else :
        return None, 'Either id_mat or mat_name must be provided!'
    if id_mat_final :
        try: 
            cursor.execute('SELECT id FROM turma WHERE id_mat = ? AND id_prof = ? AND hor = ?', (id_mat_final, id_prof, hor,))
            result = cursor.fetchone()  
            if result: return result[0] 
            return 0      
        except sqlite3.Error as e:
            return False, f"Database error: {e}"
    return 0          