from typing import Iterable
import itertools


def iterable_format_str(iter: Iterable) -> str:
    '''Вспомогательная функция для печати строковых представлений элементов множества
    на отдельных строках'''
    output = '\n'.join([f"{num}. {item}" for num, item in enumerate(iter, start=1)]) + '\n'
    return output