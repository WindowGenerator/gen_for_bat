from docx import Document
from docx.shared import Inches

from app.logic.shuffle import TicketsListType
from app.parser.base import QuestionInVarsType


def generate_answers(file_path: str, tickets: TicketsListType) -> None:
    document = Document()

    # TODO: поифксить кривой заголовок
    header = document.add_heading('\t\t\t\tОтветы на вопросы', level=1)

    columns = len(tickets[-1])
    rows = len(tickets)

    table = document.add_table(rows=1, cols=columns + 1)

    first_row_cells = table.rows[0].cells
    first_row_cells[0].text = "Билеты"
    first_row_cells[1].text = "Вопросы"

    for column_n in range(2, columns + 1):
        first_row_cells[1].merge(first_row_cells[column_n])
    
    second_row_cells = table.add_row().cells
    first_row_cells[0].merge(second_row_cells[0])

    for column_n in range(1, columns + 1):
        second_row_cells[column_n].text = str(column_n)
    
    for row_n, ticket in enumerate(tickets):

        row_cells = table.add_row().cells
        row_cells[0].text = str(row_n + 1)

        for column_n, answer in enumerate(ticket):
            row_cells[column_n + 1].text = str(answer)

    document.add_page_break()

    document.save(file_path)
