from datetime import datetime

def get_current_semester():
    date = datetime.now()
    if 1 <= date.month <= 6:
        return f'{date.year}.1'
    else:
        return f'{date.year}.2'

def time_between_semesters(sem_1: str, sem_2: str) :
    if len(sem_1) < 6 or (sem_1[-1] not in ['1', '2']) or sem_1[-2] != '.' :
        return -1
    if len(sem_2) < 6 or (sem_2[-1] not in ['1', '2']) or sem_2[-2] != '.' :
        return -1
    try :
        year_1 = int(sem_1[:-2])
        year_2 = int(sem_2[:-2])
        sem_1 = int(sem_1[-1])
        sem_2 = int(sem_2[-1])
        return abs(year_2 * 2 + sem_2 - year_1 * 2 - sem_1)/2
    except :
        return -1