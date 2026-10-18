from datetime import datetime
import time

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

def current_day () :
    date = datetime.now()
    weekday = date.weekday() + 2
    if weekday == 8 :
        weekday = 1
    current_hor = date.time()
    HORARIOS_SLOTS = {
        'M1': (time(7, 10), time(8, 0)),
        'M2': (time(8, 0), time(8, 50)),
        'M3': (time(8, 50), time(9, 40)),
        'M4': (time(10, 0), time(10, 50)),
        'M5': (time(10, 50), time(11, 40)),
        'M6': (time(11, 40), time(12, 30)),
        'T1': (time(13, 10), time(14, 0)),
        'T2': (time(14, 0), time(14, 50)),
        'T3': (time(14, 50), time(15, 40)),
        'T4': (time(16, 0), time(16, 50)),
        'T5': (time(16, 50), time(17, 40)),
        'T6': (time(17, 40), time(18, 30)),
        'N1': (time(18, 30), time(19, 20)),
        'N2': (time(19, 20), time(20, 10)),
        'N3': (time(20, 20), time(21, 10)),
        'N4': (time(21, 10), time(22, 0)),
    }
    found_slot = 'I8'
    for slot, (ini, f) in HORARIOS_SLOTS.items():
        if ini <= current_hor <= f:
            found_slot = slot
    return date, str(weekday) + found_slot  