import xlwt


workbook = xlwt.Workbook(encoding='utf-8')
worksheet = workbook.add_sheet('sheet1')
for i in range(0,9):
    for j in range(0,9):
        worksheet.write(i, j, f'{i+1}x{j+1}={(i+1)*(j+1)}')
workbook.save('student3.xls')
