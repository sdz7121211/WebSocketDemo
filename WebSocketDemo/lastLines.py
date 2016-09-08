# coding: utf-8
import os


def last_lines(fin, file_size, lines = 1000):
    fin.seek(0, 2)
    fin.seek(max(-file_size, -100000), 2)
    result = []
    for row in fin.readlines()[1:]:
        result.append(row.strip())
    tmp = result[-lines:]
    tmp.reverse()
    return tmp

if __name__ == '__main__':
    # import sys
    path = "C:/wstest.log"
    isloop = True
    last_lines("C:/wstest.log", 1000)  # print the last 5 lines of THIS file
