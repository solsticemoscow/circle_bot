
import xlsxwriter
from sqlalchemy import select

from BOT.config import ROOT_DIR
from BOT.db.db import DB_SESSION
from BOT.db.tables import Users



async def write_to_excel_all():

    workbook = xlsxwriter.Workbook(filename=ROOT_DIR + '/data/statistics/stat.xlsx')
    worksheet = workbook.add_worksheet()

    stmt = select(Users)
    result = await DB_SESSION.execute(statement=stmt)
    users = result.all()
    await DB_SESSION.close()

    INFO: list = []
    ALL: list = []
    INFO.clear()
    ALL.clear()

    if users:
        for user in users:
            INFO: list = []
            INFO.append(user[0].id)
            INFO.append(user[0].username)
            INFO.append(user[0].firstname)
            INFO.append(user[0].lastname)
            INFO.append(user[0].language_code)
            INFO.append(user[0].profile_description)
            INFO.append(user[0].time_added)
            INFO.append(user[0].blocked)
            INFO.append(user[0].is_premium)
            ALL.append(INFO)

    row = 0
    bold = workbook.add_format(
        {
            'bold': True,
            'text_wrap': True,
            'bg_color': '#00C7CE'
        }
    )
    worksheet.write(row, 0, 'id', bold, )
    worksheet.write(row, 1, 'username', bold)
    worksheet.write(row, 2, 'firstname', bold)
    worksheet.write(row, 3, 'lastname', bold)
    worksheet.write(row, 4, 'language_code', bold)
    worksheet.write(row, 5, 'profile_description', bold)
    worksheet.write(row, 6, 'time_added', bold)
    worksheet.write(row, 7, 'blocked', bold)
    worksheet.write(row, 8, 'is_premium', bold)
    worksheet.autofit()
    worksheet.default_row_height = 30
    worksheet.default_col_width = 500
    format5 = workbook.add_format({'num_format': 'mmm d yyyy hh:mm AM/PM'})
    worksheet.set_column('G:G', 2, format5)

    row = 1

    for user in ALL:
        col = 0
        for item in user:
            worksheet.write(row, col, item)
            col += 1
        row += 1

    workbook.close()


async def write_to_excel_whitelist():

    workbook = xlsxwriter.Workbook(filename=ROOT_DIR + '/data/statistics/whitelist.xlsx')
    worksheet = workbook.add_worksheet()

    stmt = select(Users).where(Users.is_whitelist)
    result = await DB_SESSION.execute(statement=stmt)
    users = result.all()
    await DB_SESSION.close()

    INFO: list = []
    ALL: list = []
    INFO.clear()
    ALL.clear()

    if users:
        for user in users:
            INFO: list = []
            INFO.append(user[0].id)
            INFO.append(user[0].username)
            INFO.append(user[0].firstname)
            INFO.append(user[0].lastname)
            ALL.append(INFO)
        row = 0
        bold = workbook.add_format(
            {
                'bold': True,
                'text_wrap': True,
                'bg_color': '#00C7CE'
            }
        )
        worksheet.write(row, 0, 'id', bold, )
        worksheet.write(row, 1, 'username', bold)
        worksheet.write(row, 2, 'firstname', bold)
        worksheet.write(row, 3, 'lastname', bold)
        worksheet.autofit()
        worksheet.default_row_height = 30
        worksheet.default_col_width = 500
        format5 = workbook.add_format({'num_format': 'mmm d yyyy hh:mm AM/PM'})
        worksheet.set_column('G:G', 2, format5)

        row = 1

        for user in ALL:
            col = 0
            for item in user:
                worksheet.write(row, col, item)
                col += 1
            row += 1

        workbook.close()
        return True
    else:
        return


