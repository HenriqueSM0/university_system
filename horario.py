class Horario :
    def __init__(self, hor: str = None):
        self.hor = hor
        self.formated_hor = ''
        self.array_form = None
        self.ch = 0
        if hor : self.__compile_hor()

    def __compile_hor (self) :
        for c in self.hor : 
            if c not in ['1', '2', '3', '4', '5', '6', '7', 'M', 'T', 'N', ' '] :
                return  
        data = self.hor.split(' ')
        table = []
        inserts = []
        for part in data :
            read_letter = False
            inserts.clear()
            for c in part :
                if c.isdigit() and not read_letter :
                    found = False
                    for i in range(len(table)) :
                        if c in table[i] :
                            if i not in inserts : inserts.append(i)
                            found = True
                            break
                    if not found: 
                        table.append([c])
                        inserts.append(len(table) - 1)
                else :
                    if not c.isdigit() :
                        letter_pos = -1
                        read_letter = True
                        found = False
                        for insert in inserts :
                            for i in range(1, len(table[insert])) :
                                if table[insert][i][0] == c :
                                    letter_pos = i
                                    found = True
                                    break
                            if not found:
                                table[insert].append(c)
                    elif c < '7' :
                        if c < '5' and table[insert][letter_pos][0] == 'N' :
                            for insert in inserts :
                                if c not in table[insert][letter_pos] :
                                    table[insert][letter_pos] += c
                        elif table[insert][letter_pos][0] != 'N' :
                            for insert in inserts :
                                if c not in table[insert][letter_pos] :
                                    table[insert][letter_pos] += c
                        else :
                            return
        order = {'M' : 1, 'T' : 2, 'N' : 3}
        carga_horaria = 0
        for i in range(len(table)) :
            if len(table[i]) == 1 :
                return
            for j in range(1, len(table[i])) :
                table[i][j] = ''.join(sorted(table[i][j], key=lambda c: (c.isdigit(), c)))
                if len(table[i][j]) == 1 :
                    return
                else :
                    carga_horaria += 16 * (len(table[i][j]) - 1)
                for k in range(j + 1, len(table[i])) :
                    if order[table[i][j][0]] > order[table[i][k][0]] :
                        table[i][j], table[i][k] = table[i][k], table[i][j]
            for k in range(i + 1, len(table)) :
                    if int(table[i][0]) > int(table[k][0]) :
                        table[i][0], table[k][0] = table[k][0], table[i][0] 
        i = 0
        while i < len(table) :
            j = i + 1
            while j < len(table) :
                if table[i][0] == table[j][0] :
                    for k in range(1, len(table[i])) :
                        table[i][1] += table[j][k]
                    del table[j]
                elif len(table[i]) == len(table[j]) :
                    equal_conjs = True
                    for k in range(1, len(table[i])) :
                        if table[i][k] != table[j][k] :
                            equal_conjs = False
                            break
                    if equal_conjs : 
                        table[i][0] += table[j][0]
                        del table[j]
                    else :
                        j += 1
                else :
                    j += 1
            i += 1
        formated_hor = ''
        for tuple in table :
            for elem in tuple :
                formated_hor += elem
            formated_hor += ' '
        self.array_form = table
        self.formated_hor = formated_hor
        self.ch = carga_horaria

    @staticmethod
    def conflitant (*horarios : str) :
        matrix = [[0] * 16 for _ in range(7)]
        for horario in horarios :
            data = [p for p in horario.split(' ') if p.strip()]
            for part in data :
                if 'M' in part :
                    cipher = -1
                    combinaiton = part.split('M')
                elif 'T' in part :
                    cipher = 5
                    combinaiton = part.split('T')
                else :
                    cipher = 11
                    combinaiton = part.split('N')
                days = combinaiton[0]
                times = combinaiton[1]
                for day in days :
                    for time in times :
                        if matrix[int(day) - 1][int(time) + cipher] == 1 :
                            return True
                        else : 
                            matrix[int(day) - 1][int(time) + cipher] = 1
        return False