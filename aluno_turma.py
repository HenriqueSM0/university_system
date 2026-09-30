import sqlite3, json

def _create_table_aluno_turma (cursor: sqlite3.Cursor) :
    cursor.execute(
        '''CREATE TABLE IF NOT EXISTS aluno_turma (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            id_aluno INTEGER NOT NULL,
            id_turma INTEGER NOT NULL,
            notas TEXT,
            status TEXT NOT NULL,
            FOREIGN KEY (id_turma) REFERENCES turma(id) ON DELETE CASCADE ON UPDATE CASCADE,
            FOREIGN KEY (id_aluno) REFERENCES aluno(id) ON DELETE CASCADE ON UPDATE CASCADE,
            CONSTRAINT unique_turma_aluno UNIQUE (id_turma, id_aluno)
        )'''
    )

def create_aluno_turma (cursor: sqlite3.Cursor, id_aluno: int, id_turma: int) :
    try:
        cursor.execute('SELECT nome, cpf FROM aluno WHERE id = ?', (id_aluno,))
        row = cursor.fetchone()
        if not row:
            return False, f"Aluno with ID {id_aluno} does not exist"
        nome_aluno = row[0]
        cpf_aluno = row[1]
        cursor.execute('SELECT id_mat, n_vagas FROM turma WHERE id = ?', (id_turma,))
        row = cursor.fetchone()
        if not row:
            return False, f"Turma with ID {id_turma} does not exist"
        id_mat = row[0]
        n_vagas_turma = row[1]
        cursor.execute('SELECT nome FROM materia WHERE id = ?', (id_mat,))
        nome_mat = cursor.fetchone()[0]
        cursor.execute(
            'SELECT status, sem FROM aluno_turma JOIN turma ON id_turma = id WHERE id_aluno = ? AND id_mat = ?', 
            (id_aluno, id_mat)
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
            return_str = return_str.removesuffix('\n')
            return False, return_str 
        cursor.execute('SELECT COUNT(*) FROM aluno_turma WHERE id_turma = ?', (id_turma,))
        vagas_disp = cursor.fetchone()[0]
        if n_vagas_turma - vagas_disp == 0 :
            return False, 'Nao ha vagas remanecentes nessa turma'
        cursor.execute('''
            INSERT INTO aluno_turma (id_aluno, id_turma, notas, status) 
            VALUES (?, ?, ?, ?)
            ''', (id_aluno, id_turma, '{}', 'in_progress'))
        return True, f"aluno_turma '{nome_aluno} - {cpf_aluno} -{id_turma} - {nome_mat}' created with ID {cursor.lastrowid}"
    except sqlite3.IntegrityError as e:
        if "unique_turma_aluno" in str(e):
            return False, f"aluno_turma '{nome_aluno} - {cpf_aluno} {id_turma} - {nome_mat}' already exists"
        return False, f"Database constraint error: {e}"
    except sqlite3.Error as e:
        return False, f"Database error: {e}"

def set_grade (cursor: sqlite3.Cursor, id_aluno: int, id_turma: int, nome_grade: str, grade: float) :
    if 0 <= grade <= 10 :
        try:
            cursor.execute('SELECT nome, cpf FROM aluno WHERE id = ?', (id_aluno,))
            row = cursor.fetchone()
            if not row:
                return False, f"Aluno with ID {id_aluno} does not exist"
            nome_aluno = row[0]
            cpf_aluno = row[1]
            cursor.execute('SELECT id_mat, sem FROM turma WHERE id = ?', (id_turma,))
            row = cursor.fetchone()
            if not row:
                return False, f"Turma with ID {id_turma} does not exist"
            id_mat = row[0]
            sem = row[1]
            cursor.execute('SELECT notas FROM aluno_turma WHERE id_turma = ? AND id_aluno = ?', (id_turma, id_aluno,))
            row = cursor.fetchone()
            if not row:
                return False, f"aluno_turma with ID {id_aluno} - {id_turma} does not exist"
            notas = json.loads(row[0])
            notas[nome_grade] = grade
            cursor.execute('UPDATE aluno_turma SET notas = ? WHERE id_aluno = ? AND id_turma = ?', 
                           (json.dumps(notas), id_aluno, id_turma,))
            return True, f"aluno_turma '{nome_aluno} - {cpf_aluno} - {id_turma} - {sem} - {id_mat} - {nome_grade}:{grade}' updated"
        except sqlite3.Error as e:
            return False, f"Database error: {e}"    
    else :
        return False, f"Grade need to be in [0, 10]!"    