import sqlite3
import horario as H
import ai_funcs as AI
import date_funcs
import materia
import aluno
import json

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

def create_turma (cursor: sqlite3.Cursor, id_prof: int, local: str, id_mat: int, hor: str, n_vagas: int) :
    if not (0 <= n_vagas <= 120):
        return False, 'Numero de vagas e de (0-120)'
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
            sem = date_funcs.get_current_semester()
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

def id_turma (cursor: sqlite3.Cursor, id_mat: int = None, mat_name: str = None, id_prof: int = None, hor: str = None, sem: str = None) :
    if mat_name is not None and hor is None:
        obj = H.Horario(mat_name)
        if obj.array_form:
            hor = mat_name
            mat_name = None
            if id_prof is None and id_mat is not None:
                id_prof = id_mat
                id_mat = None
    id_mat_final = None
    if id_mat is not None :
        try :
            id_mat_final = int(id_mat)
        except (ValueError, TypeError) :
            return False, 'Invalid id'
    elif mat_name is not None :
        id_mat_final = materia.id_materia(cursor, mat_name)
        if not id_mat_final:
            return 0
    id_prof_final = None
    if id_prof is not None :
        try :
            id_prof_final = int(id_prof)
        except (ValueError, TypeError) :
            return False, 'Invalid id'
    if hor is None :
        return None, 'hor must be provided!'
    if id_prof_final is None and id_mat_final is None :
        return None, 'Either id_prof or id_mat (or mat_name) must be provided!'
    obj_hor = H.Horario(hor)
    formated_hor = obj_hor.formated_hor if obj_hor.formated_hor else hor
    try: 
        conditions = []
        params = []
        if id_prof_final is not None:
            conditions.append('id_prof = ?')
            params.append(id_prof_final)

        if id_mat_final is not None:
            conditions.append('id_mat = ?')
            params.append(id_mat_final)

        if formated_hor == hor:
            conditions.append('hor = ?')
            params.append(hor)
        else:
            conditions.append('(hor = ? OR hor = ?)')
            params.extend([formated_hor, hor])
        if sem is not None:
            conditions.append('sem = ?')
            params.append(sem)
        where_clause = ' AND '.join(conditions)
        cursor.execute(f'SELECT id FROM turma WHERE {where_clause}', tuple(params))
        result = cursor.fetchone()  
        if result: return result[0] 
        return 0      
    except sqlite3.Error as e:
        return False, f"Database error: {e}"          

def fill_turmas (cursor: sqlite3.Cursor, mat_period: bool) :
    return_str = ''
    if mat_period :
        cursor.execute('''SELECT turma_reserva.n_vagas, id_cur, id_turma FROM 
            turma JOIN turma_reserva ON id_turma = turma.id 
            WHERE sem = ?''', (date_funcs.get_current_semester(),))
        rows = cursor.fetchall()
        for row in rows:
            n_vagas = row[0]
            id_cur = row[1]
            id_turma = row[2]
            cursor.execute('''SELECT id_aluno, cpf, nome, priority FROM matricula 
                JOIN turma ON id_turma = turma.id
                JOIN aluno ON id_aluno = aluno.id
                WHERE status = 'requested' 
                AND id_cur = ? AND id_turma = ?
                ORDER BY priority DESC''', (id_cur, id_turma,))
            alunos = cursor.fetchall()
            size = min(n_vagas, len(alunos))
            try :
                for i in range(size) :
                    cursor.execute('''INSERT INTO aluno_turma(id_aluno, id_turma, notas, status)
                        VALUES (?, ?, '{}', 'in_progress')''', (alunos[i][0], id_turma,))
                    return_str += f'Aluno {alunos[i][2]} - {alunos[i][1]} (p = {alunos[i][3]}) inserted in turma {id_turma} - {id_cur} with ID {cursor.lastrowid}\n'  
                    cursor.execute('''UPDATE matricula SET status = 'granted' WHERE id_aluno = ? AND id_turma = ?''', (alunos[i][0], id_turma,)) 
                for i in range(size, len(alunos)) :
                    cursor.execute('''UPDATE matricula SET status = 'rejected' WHERE id_aluno = ? AND id_turma = ?''', (alunos[i][0], id_turma,))
                    return_str += f'Aluno {alunos[i][2]} - {alunos[i][1]} (p = {alunos[i][3]}) out of turma {id_turma} - {id_cur} with ID {cursor.lastrowid}\n'
            except sqlite3.IntegrityError as e:
                if "unique_aluno_turma" in str(e) or ("UNIQUE" in str(e) and "aluno_turma" in str(e)):
                    return_str += f"Aluno {alunos[i][2]} - {alunos[i][1]} já está na turma {id_turma}\n"
                else :
                    return False, f"Database constraint error: {e}" 
            except sqlite3.Error as e:
                    return False, f"Database error: {e}"       
    else :
        cursor.execute('''SELECT n_vagas, id FROM turma WHERE sem = ?''', (date_funcs.get_current_semester(),))
        rows = cursor.fetchall()
        for row in rows:
            n_vagas = row[0]
            id_turma = row[1]
            cursor.execute('''SELECT id_aluno, cpf, nome, priority FROM matricula 
                JOIN aluno ON id_aluno = aluno.id
                WHERE status = 'requested' AND id_turma = ?
                ORDER BY priority DESC''', (id_turma,))
            alunos = cursor.fetchall()
            size = min(n_vagas, len(alunos))
            try :
                for i in range(size) :
                    cursor.execute('''INSERT INTO aluno_turma(id_aluno, id_turma, notas, status)
                        VALUES (?, ?, '{}', 'in_progress')''', (alunos[i][0], id_turma,))
                    return_str += f'Aluno {alunos[i][2]} - {alunos[i][1]} (p = {alunos[i][3]}) inserted in turma {id_turma} with ID {cursor.lastrowid}\n'  
                    cursor.execute('''UPDATE matricula SET status = 'granted' WHERE id_aluno = ? AND id_turma = ?''', (alunos[i][0], id_turma,)) 
                for i in range(size, len(alunos)) :
                    cursor.execute('''UPDATE matricula SET status = 'rejected' WHERE id_aluno = ? AND id_turma = ?''', (alunos[i][0], id_turma,))
                    return_str += f'Aluno {alunos[i][2]} - {alunos[i][1]} (p = {alunos[i][3]}) out of turma {id_turma} with ID {cursor.lastrowid}\n'
            except sqlite3.IntegrityError as e:
                if "unique_aluno_turma" in str(e) or ("UNIQUE" in str(e) and "aluno_turma" in str(e)):
                    return_str += f"Aluno {alunos[i][2]} - {alunos[i][1]} já está na turma {id_turma}\n"
                else :
                    return False, f"Database constraint error: {e}"
            except sqlite3.Error as e:
                return False, f"Database error: {e}"
    return_str = return_str.removesuffix('\n')
    return True, return_str

def finish_turmas (cursor: sqlite3.Cursor) :
    try :
        current_sem = date_funcs.get_current_semester()
        cursor.execute('''SELECT aluno.nome, aluno.cpf, aluno_turma.notas, aluno_turma.id_turma, aluno_turma.id, aluno_turma.id_aluno FROM 
            aluno_turma JOIN aluno ON aluno_turma.id_aluno = aluno.id
            JOIN turma ON aluno_turma.id_turma = turma.id 
            WHERE turma.sem = ? AND aluno_turma.status = 'in_progress' ''', (current_sem,))
        rows = cursor.fetchall()
        for row in rows:
            nome_aluno = row[0]
            cpf_aluno = row[1]
            notas_json = row[2]
            id_turma = row[3]
            notas = json.loads(notas_json)
            if 'NF' not in notas or notas.get('NF') is None :
                return False, f'O aluno {nome_aluno} - {cpf_aluno} nao tem nota final na turma ID {id_turma}'
        return_str = ''
        for row in rows:
            nome_aluno = row[0]
            cpf_aluno = row[1]
            notas_json = row[2]
            id_turma = row[3]
            id_aluno_turma = row[4]
            id_aluno = row[5]
            notas = json.loads(notas_json)
            nota_final = float(notas['NF'])
            tx_freq, _ = aluno.frequencia(cursor, id=id_aluno, id_turma=id_turma)
            if nota_final < 6 or tx_freq < 0.75 :
                new_status = 'reproved'
            else :
                new_status = 'approved'
            cursor.execute('''UPDATE aluno_turma SET status = ? WHERE id = ?''', (new_status, id_aluno_turma,))
            return_str += f'Aluno {nome_aluno} - {cpf_aluno} finalizado na turma {id_turma} com status {new_status}\n'
        return_str = return_str.removesuffix('\n')
        return True, return_str if return_str else f'Nenhuma turma em andamento no semestre {current_sem}'
    except sqlite3.Error as e:
        return False, f"Database error: {e}"    