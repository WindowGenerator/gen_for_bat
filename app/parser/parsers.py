from enum import Enum
from typing import List, Tuple

import xlrd
from docx import Document

from app.parser.base import QuestionsToAnswers, QuestionAnswerType, validate_and_return_questions


class FormatEnum(str, Enum):
    docx = 'docx'
    xls = 'xls'
    txt = 'txt'
    dir = 'dir'


def parse_factory(source_path: str, _format: FormatEnum) -> Tuple[QuestionAnswerType, QuestionsToAnswers]:
    questions_to_answers = None

    if FormatEnum.dir == _format:
        questions_to_answers = validate_and_return_questions(source_path)

    if questions_to_answers is None:
        raise ValueError(f"Format '{_format}' not available")

    return questions_to_answers
