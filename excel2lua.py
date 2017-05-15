# -*- coding: utf-8 -*-
#!/usr/bin/python
import xlrd
import os
from sys import argv

def loadFilePaths(path = '文件路径.txt'):
    print("正在解析路径列表: ", path)
    paths = []
    with open(path, 'rb') as f:
        text = f.read()
        text = text.decode('utf-8')
        paths = eval(text)
        for path in paths:
            path[0] = path[0] + '.xlsx'
            path[2] = path[2] + '.lua'
            #print(path)

        return paths
    print("[Error]: 解析路径列表失败")
    return paths

def data2int(data):
    try:
        if type(data) == str and data != '':
            data = int(data)
    except Exception as e:
        print('[Error]: Index Error in data 2 int: ', e)
    finally:
        return data

# tag = 0, 处理普通数据; tag = 1处理id数据
def formatData(data, tag = 0):
    try:
        if data == None or data == '':
            data = 'nil'
        elif type(data) != str:
            if data.is_integer():
                data = int(data)
            else:
                data = round(data, 5)
        # elif tag == 0:
        #     data = '"' + data + '"'
        return data
    except Exception as e:
        print("[FormatData Error]: ", e)
        return 'nil'

def parse_excel(pathList):
    print('开始解析表: ', pathList[0], '→', pathList[1], '，目标路径: ',pathList[2])
    try:
        book = xlrd.open_workbook(pathList[0])
    except Exception as e:
        print('[Error]: 找不到该excel文件: ', e)
        return
    # print("The number of worksheets is {0}".format(book.nsheets))
    # print("Worksheet name(s): {0}".format(book.sheet_names()))
    # 找到相应的Sheet
    sh = None
    for sn in book.sheet_names():
        if sn == pathList[1]:
            sh = book.sheet_by_name(sn)
    if sh == None:
        print('[Error]: 没有找到对应的Sheet: ' + pathList[0] + '→' + pathList[1] + '，请检查配置文件')
        return None

    # print("{0} {1} {2}".format(sh.name, sh.nrows, sh.ncols))
    # print("Cell D30 is {0}".format(sh.cell_value(rowx=29, colx=3)))
    # for rx in range(sh.nrows):
    #     print(sh.row(rx))
    #titleList = []
    #dataList = []
    #for cx in range(1, sh.ncols):
        # print(sh.cell_value(rowx=1, colx=cx))
        #titleList.append(sh.cell_value(rowx=1, colx=cx))
    #for rx in range(3, sh.nrows):
        #rowData = []
        #print(sh.row(rx))
        #print(sh.row_types(rx))
        #print(sh.row_values(rx))

    ##################

    # 开始写数据
    with open(pathList[2], 'w', encoding='utf8') as targetFile:
        # targetFile = open(pathList[2], 'w')
        # ---------- write -------------
        targetFile.write('local value_list = {} \n')
        # 从第三行开始是数据
        for rx in range(3, sh.nrows):
            # 处理是否导表
            # 1.导表 2.将id转为字符串 -1.不导表
            isload = sh.cell_value(rowx=rx, colx=0)
            if isload == '' or isload == None or isload == -1 or isload == 0 or data2int(isload) == -1:
                continue
            id = sh.cell_value(rowx=rx, colx=1)
            id = formatData(id, 1)
            if isload == 2:
                id = '"' + str(id) + '"'
            # print("id = ", type(id), id)
            targetFile.write('value_list[{0}] = '.format(id))
            targetFile.write('{')
            # 从第二列开始是数据
            for cx in range(1, sh.ncols):
                # 空.导表 2. 导出为字符串 -1. 不导表
                isload2 = sh.cell_value(rowx=2, colx=cx)
                # print(sh.cell_value(rowx=1, colx=cx))
                if isload2 == -1 or data2int(isload2) == -1:
                    continue

                cell_value = sh.cell_value(rowx=rx, colx=cx)
                cell_value = formatData(cell_value)

                if cell_value == None or cell_value == '' or cell_value == 'nil':
                    continue

                if isload2 == 2:
                    cell_value = '"' + str(cell_value) + '"'
                elif isload == 2 and cx == 1:
                    cell_value = '"' + str(cell_value) + '"'
                # 处理title
                title = sh.cell_value(rowx=1, colx=cx)
                if title == '' or title == None:
                    continue
                # 写 title = 数据,
                try:

                    targetFile.write(sh.cell_value(rowx=1, colx=cx))
                    targetFile.write(' = ')

                    targetFile.write(str(cell_value))
                    if cx != sh.ncols - 1:
                        targetFile.write(', ')
                except Exception as e:
                    print("[Error]: At ", rx, cx, e)

            targetFile.write('} \n')

        # --------- write end ----------
        # 合表
        if pathList[2].find('equipdata.lua') >= 0:
            targetFile.write('\nsetmetatable(value_list,{__index = require "data.item_data"})\n')
        elif pathList[2].find('elementstone_data.lua') >= 0:
            targetFile.write('\nsetmetatable(value_list,{__index = require "data.HelpGirl_data"})\n')
        elif pathList[2].find('component_data.lua') >= 0:
            targetFile.write('\nsetmetatable(value_list,{__index = require "data.elementstone_data"})\n')
        elif pathList[2].find('item_data.lua') >= 0:
            targetFile.write('\nsetmetatable(value_list,{__index = require "data.component_data"})\n')
        elif pathList[2].find('gift_drop_data.lua') >= 0:
            targetFile.write('\nsetmetatable(value_list,{__index = require "data.drop_data"})\n')

        targetFile.write('\nreturn value_list\n')

def parse_all_excels(paths):
    datas = []
    for path in paths:
        datas.append(parse_excel(path))
    return datas

def main():
    if len(argv) >= 2:
        paths = loadFilePaths(argv[1])
    else:
        paths = loadFilePaths()
    parse_all_excels(paths)

if __name__ == "__main__":
    print('>>>>>>>>>>>>>>>>>>>>>>')
    print('导表开始...')
    main()
    print('导表结束...')
    print('<<<<<<<<<<<<<<<<<<<<<<')
    os.system("pause")
