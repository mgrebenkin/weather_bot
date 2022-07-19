def set_format_str(tasks: set) -> str:
    '''Вспомогательная функция для печати строковых представлений элементов множества
    на отдельных строках'''
    cnt = 1
    output = ""
    for item in tasks:
        output =  output + "\n" + str(cnt) + ". " + item.__str__()
        cnt += 1
    return output