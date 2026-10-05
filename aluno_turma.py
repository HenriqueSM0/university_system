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

def fill_turmas (cursor: sqlite3.Cursor, mat_period: bool) :
    try:
        return_str = ''
        if mat_period :
            cursor.execute('''SELECT n_vagas, id_cur, id_turma FROM 
                turma JOIN turma_reserva ON id_turma = turma.id ''')
            rows = cursor.fetchall()
            for row in rows:
                n_vagas = row[0]
                id_cur = row[1]
                id_turma = row[2]
                cursor.execute('''SELECT id_aluno, cpf, nome FROM matricula 
                    JOIN turma ON id_turma = turma.id
                    JOIN aluno ON id_aluno = aluno.id
                    WHERE status = 'requested' AND id_cur = ?
                    ORDER BY priority DESC''', (id_cur,))
                alunos = cursor.fetchall()
                size = min(n_vagas, len(alunos))
                try :
                    for i in range(size) :
                        cursor.execute('''INSERT INTO aluno_turma(id_aluno, id_turma, notas, status)
                            VALUES (?, ?, '{}', 'in_progress')''', (alunos[i][0], id_turma,))
                        return_str += f'Aluno {alunos[i][2]} - {alunos[i][1]} inserted in turma {id_turma} - {id_cur} with ID {cursor.lastrowid}'  
                        cursor.execute('''UPDATE matricula SET status = 'granted' WHERE id_aluno = ? AND id_turma = ?''', (alunos[i][0], id_turma,)) 
                    for i in range(size, len(alunos)) :
                        cursor.execute('''UPDATE matricula SET status = 'rejected' WHERE id_aluno = ? AND id_turma = ?''', (alunos[i][0], id_turma,))
                        return_str += f'Aluno {alunos[i][2]} - {alunos[i][1]} out of turma {id_turma} - {id_cur} with ID {cursor.lastrowid}'
                except sqlite3.IntegrityError as e:
                    if "unique_aluno_turma" in str(e):
                        return False, f"Aluno {alunos[i][2]} ({alunos[i][1]}) já está na turma {id_turma}"
                    return False, f"Database constraint error: {e}"        
        else :
            cursor.execute('''SELECT n_vagas, id FROM turma''')
            rows = cursor.fetchall()
            for row in rows:
                n_vagas = row[0]
                id_turma = row[1]
                cursor.execute('''SELECT id_aluno, cpf, nome FROM matricula 
                    JOIN aluno ON id_aluno = aluno.id
                    WHERE status = 'requested' AND id_turma = ?
                    ORDER BY priority DESC''', (id_turma,))
                alunos = cursor.fetchall()
                size = min(n_vagas, len(alunos))
                try :
                    for i in range(size) :
                        cursor.execute('''INSERT INTO aluno_turma(id_aluno, id_turma, notas, status)
                            VALUES (?, ?, '{}', 'in_progress')''', (alunos[i][0], id_turma,))
                        return_str += f'Aluno {alunos[i][2]} - {alunos[i][1]} inserted in turma {id_turma} with ID {cursor.lastrowid}'  
                        cursor.execute('''UPDATE matricula SET status = 'granted' WHERE id_aluno = ? AND id_turma = ?''', (alunos[i][0], id_turma,)) 
                    for i in range(size, len(alunos)) :
                        cursor.execute('''UPDATE matricula SET status = 'rejected' WHERE id_aluno = ? AND id_turma = ?''', (alunos[i][0], id_turma,))
                        return_str += f'Aluno {alunos[i][2]} - {alunos[i][1]} out of turma {id_turma} with ID {cursor.lastrowid}'
                except sqlite3.IntegrityError as e:
                    if "unique_aluno_turma" in str(e):
                        return False, f"Aluno {alunos[i][2]} ({alunos[i][1]}) já está na turma {id_turma}"
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