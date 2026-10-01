import sqlite3

def _create_table_turma_reserva (cursor: sqlite3.Cursor) :
    cursor.execute(
        '''CREATE TABLE IF NOT EXISTS turma_reserva (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            id_turma INT NOT NULL,
            id_cur INTEGER NOT NULL,
            n_vagas INT NOT NULL,
            FOREIGN KEY (id_turma) REFERENCES turma(id) ON DELETE CASCADE ON UPDATE CASCADE,
            FOREIGN KEY (id_cur) REFERENCES curso(id) ON DELETE CASCADE ON UPDATE CASCADE,
            CONSTRAINT unique_turma_reserva UNIQUE (id_turma, id_cur)
        )'''
    )

def create_turma_reseva (cursor: sqlite3.Cursor, id_turma: int, id_cur: int, n_vagas: int) :
    try:
        cursor.execute('SELECT id_mat, n_vagas FROM turma WHERE id = ?', (id_turma,))
        row = cursor.fetchone()
        if not row:
            return False, f"Turma with ID {id_turma} does not exist"
        else : 
            id_mat = row[0]
            n_vagas_turma = row[1]
            cursor.execute(
                'SELECT COALESCE(SUM(n_vagas), 0) FROM turma_reserva WHERE id_turma = ?',
                (id_turma,)
            )
            sum_vagas = cursor.fetchone()[0]
            if n_vagas_turma - sum_vagas < n_vagas :
                return False, f'Nao e possivel reservar {n_vagas} vagas para a turma "{id_turma}", so estao disponiveis {n_vagas_turma - sum_vagas}'
            cursor.execute('SELECT nome FROM materia WHERE id = ?', (id_mat,))
            nome_mat = cursor.fetchone()[0]
        cursor.execute('SELECT nome FROM curso WHERE id = ?', (id_cur,))
        row = cursor.fetchone()
        if not row:
            return False, f"Curso with ID {id_cur} does not exist"
        else : 
            nome_cur = row[0]
        cursor.execute('''
            INSERT INTO turma_reserva (id_turma, id_cur, n_vagas) 
            VALUES (?, ?, ?)
            ''', (id_turma, id_cur, n_vagas))
        return True, f"turma_reserva '{nome_cur} - {id_turma} - {nome_mat} - {n_vagas}' created with ID {cursor.lastrowid}"
    except sqlite3.IntegrityError as e:
        if "unique_turma_reserva" in str(e):
            return False, f"turma_reserva '{nome_cur} - {id_turma} - {nome_mat}' already exists"
        return False, f"Database constraint error: {e}"
    except sqlite3.Error as e:
        return False, f"Database error: {e}"

def delete_turma_reserva (cursor: sqlite3.Cursor, id_turma: int, id_cur: int, sem: str) :
    cursor.execute('''SELECT id FROM turma_reserva WHERE id_turma = ? AND id_cur = ? AND sem = ?''', (id_turma, id_cur, sem))
    row = cursor.fetchone()
    if not row:
        return False, f'turma_reserva com id_turma {id_turma} e id_cur {id_cur} não encontrado'
    id = row[0]
    try:
        cursor.execute('DELETE FROM turma_reserva WHERE id = ?', (id,))
        return True, f"turma_reserva '{id}' deletado com sucesso"
    except sqlite3.Error as e:
        return False, f"Database error: {e}"