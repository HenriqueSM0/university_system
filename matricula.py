import sqlite3
import aluno
import date_funcs

def _create_table_matricula (cursor: sqlite3.Cursor) :
    cursor.execute(
        '''CREATE TABLE IF NOT EXISTS matricula (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            id_aluno INTEGER NOT NULL,
            id_turma INTEGER NOT NULL,
            priority FLOAT,
            status TEXT,
            FOREIGN KEY (id_turma) REFERENCES turma(id) ON DELETE CASCADE ON UPDATE CASCADE,
            FOREIGN KEY (id_aluno) REFERENCES aluno(id) ON DELETE CASCADE ON UPDATE CASCADE,
            CONSTRAINT unique_matricula UNIQUE (id_turma, id_aluno, status)
        )'''
    )

def create_matricula_request (cursor: sqlite3.Cursor, id_aluno: int, id_turma: int, mat_period: bool) :
    try:
        cursor.execute('SELECT nome, cpf, id_cur FROM aluno WHERE id = ?', (id_aluno,))
        row = cursor.fetchone()
        if not row:
            return False, f"Aluno with ID {id_aluno} does not exist"
        nome_aluno = row[0]
        cpf_aluno = row[1]
        id_cur_aluno = row[2]
        cursor.execute('SELECT id_mat, sem FROM turma WHERE id = ?', (id_turma,))
        row = cursor.fetchone()
        if not row:
            return False, f"Turma with ID {id_turma} does not exist"
        id_mat = row[0]
        sem = row[1]
        current_sem = date_funcs.get_current_semester() 
        if current_sem != sem :
            return False, f'Nao e possivel solicitar matricula na turma "{id_turma}" de {sem} para {current_sem}'
        cursor.execute('''SELECT 1 FROM matricula JOIN turma ON id_turma = turma.id 
            WHERE id_aluno = ? AND id_mat = ? AND status = 'requested' ''', (id_aluno, id_mat,))
        row = cursor.fetchone()
        if row :
            return False, f'Aluno {nome_aluno} - {cpf_aluno} is already requesting for materia {id_mat} on turma {id_turma}'
        if mat_period :
            cursor.execute('''SELECT id_cur FROM turma_reserva WHERE id_turma = ?''', (id_turma,))
            rows = cursor.fetchall()
            allowed_curso = False
            for row in rows :
                if int(row[0]) == id_cur_aluno :
                    allowed_curso = True
                    break
            if not allowed_curso :
                return False, f'O curso {id_cur_aluno} nao possui reserva de matricula na turma {id_turma}'
        cursor.execute('SELECT nome FROM materia WHERE id = ?', (id_mat,))
        nome_mat = cursor.fetchone()[0]
        cursor.execute(
            'SELECT aluno_turma.status, turma.sem FROM aluno_turma JOIN turma ON aluno_turma.id_turma = turma.id WHERE aluno_turma.id_aluno = ? AND turma.id_mat = ?', 
            (id_aluno, id_mat,)
            )
        row = cursor.fetchone()
        if row :
            status_old = row[0]
            sem_old = row[1]
            if status_old == 'approved' :
                return False, f'O aluno {nome_aluno} - {cpf_aluno} já foi aprovado na matéria {nome_mat} em {sem_old}'
        cursor.execute(
            '''SELECT nome, type, status FROM (mat_reqs LEFT JOIN
            (aluno_turma JOIN turma ON id_turma = turma.id
            AND id_aluno = ?)
            ON id_mat_reqsid = turma.id_mat
            JOIN materia ON id_mat_reqsid = materia.id)
            WHERE id_mat_reqstt = ?''', (id_aluno, id_mat)
            )
        rows = cursor.fetchall()
        if rows :
            return_str = ''
            for row in rows:
                if row[2] is None or row[2] == 'reproved' or (row[1] == 'pre' and row[2] == 'in_progress') :
                    return_str += f'{nome_mat} {row[1]}-requires {row[0]}\n'
            if return_str:
                return_str = return_str.removesuffix('\n')
                return False, return_str 
        md = aluno.media_geral(cursor, id_aluno)[0]
        tx_ap = aluno.taxa_aprovacao(cursor, id_aluno)[0]
        per_aluno = aluno.periodo_aluno(cursor, id_aluno)[0]
        if per_aluno == 1:
            prioridade = 999999
        else:
            cursor.execute('SELECT periodo_fluxo FROM mat_curso WHERE id_cur = ? AND id_mat = ?', (id_cur_aluno, id_mat))
            row = cursor.fetchone()
            if row:
                dif_per_aluno_per_mat = abs(per_aluno - row[0]) + 1
            else:
                dif_per_aluno_per_mat = per_aluno + 1
            prioridade = tx_ap ** 2 * abs(md / dif_per_aluno_per_mat)
        cursor.execute('''
            INSERT INTO matricula (id_aluno, id_turma, priority, status) 
            VALUES (?, ?, ?, ?)
            ''', (id_aluno, id_turma, prioridade, 'requested'))
        return True, f'Requisição de matricula {nome_aluno} - {cpf_aluno} na turma {id_turma} criada com {cursor.lastrowid}'
    except sqlite3.IntegrityError as e:
        if "unique_matricula" in str(e) or ("UNIQUE" in str(e) and "matricula" in str(e)):
            return False, f"request '{nome_aluno} - {cpf_aluno} - {id_turma} - requested' already exists"
        else :
            return False, f"Database constraint error: {e}"
    except sqlite3.Error as e:
        return False, f"Database error: {e}"

def delete_matricula_request (cursor: sqlite3.Cursor, id: int = None, id_aluno: int = None, id_turma: int = None) :
    if id is not None :
        try :
            id_mat = int(id)
        except (ValueError, TypeError) :
            return False, 'Invalid id'
        cursor.execute('''SELECT m.id, a.nome, a.cpf, m.id_turma FROM matricula m
            JOIN aluno a ON m.id_aluno = a.id
            WHERE m.id = ? AND m.status = 'requested' ''', (id_mat,))
        row = cursor.fetchone()
        if not row :
            return False, f"Requisição de matricula com ID {id_mat} não encontrada"
        id_req = row[0]
        nome_aluno = row[1]
        cpf_aluno = row[2]
        id_turma_req = row[3]
    elif id_aluno is not None and id_turma is not None :
        cursor.execute('''SELECT m.id, a.nome, a.cpf FROM matricula m
            JOIN aluno a ON m.id_aluno = a.id
            WHERE m.id_aluno = ? AND m.id_turma = ? AND m.status = 'requested' ''', (id_aluno, id_turma,))
        row = cursor.fetchone()
        if not row :
            return False, f"Requisição de matricula para aluno {id_aluno} na turma {id_turma} não encontrada"
        id_req = row[0]
        nome_aluno = row[1]
        cpf_aluno = row[2]
        id_turma_req = id_turma
    else :
        return False, 'Either id or (id_aluno + id_turma) must be provided!'
    try :
        cursor.execute('DELETE FROM matricula WHERE id = ?', (id_req,))
        return True, f"Requisição de matricula '{nome_aluno} - {cpf_aluno} - turma {id_turma_req}' deletada com sucesso"
    except sqlite3.Error as e:
        return False, f"Database error: {e}"