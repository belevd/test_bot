def calculator(string):
    try:
        string = string.lower().replace(' ', '')
        parts = string.split('+')

        for plus in range(len(parts)):
            if '-' in parts[plus]:
                parts[plus] = parts[plus].split('-')

        for plus in range(len(parts)):
            parts[plus] = precalculator(parts[plus])

        result = sum(parts)
    except ValueError:
        result = 'Введены некорректные данные'
    except ZeroDivisionError:
        result = 'Деление на 0 невозможно'
    return result

def precalculator(part):

    if type(part) is str:

        if '*' in part:
            result = 1
            for subpart in part.split('*'):
                result *= precalculator(subpart)
            return result
        
        elif '/' in part:
            parts = list(map(precalculator, part.split('/')))
            result = parts[0]
            for subpart in parts[1:]:
                result /= subpart
            return result
        
        else:
            return float(part)

    elif type(part) is list:

        for i in range(len(part)):
            part[i] = precalculator(part[i])

        return part[0]-sum(part[1:])


    return part


if __name__ == '__main__':
    print(calculator('3 / 2 + 10 + 2 * 3 * 2.5 - 4 + 1 / 2'))
