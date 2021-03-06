import os
import re
from typing import Dict, List, Tuple
from enum import Enum

QuestionInVarsType = Dict[str, List[str]]

Question = str
Answer = Tuple[int, str]
AnswerQuestion = int
QuestionAndAnswer = Tuple[Question, AnswerQuestion, List[Answer]]
QuestionsToAnswers = Dict[int, QuestionAndAnswer]


class QuestionAnswerType(str, Enum):
    image_files = 'image_files'


QUESTIONS = 'questions'
ANSWERS = 'answers.txt'


def validate_and_return_questions(
        source_path: str, questions_count: int = 4
) -> Tuple[QuestionAnswerType, QuestionsToAnswers]:

    asb_dir = os.path.abspath(source_path)
    questions_dir = os.path.join(asb_dir, QUESTIONS)
    answers_file = os.path.join(asb_dir, ANSWERS)

    questions_count = None

    questions_to_answers: QuestionsToAnswers = dict()
    _q_answers: Dict[int, int] = dict()

    if not os.path.exists(answers_file) or not os.path.isfile(answers_file):
        raise RuntimeError('Отсутствует файл с ответами `answers` или не существует')

    with open(answers_file, 'rt') as _file_fd:
        for index, line in enumerate(_file_fd.readlines()):
            split_line = line.split()

            if len(split_line) != 2:
                raise RuntimeError(f'Что-то не так в строке №{index}. Вместо вопроса ответа там что-то еще')

            q_n, q_a = line.split()

            try:
                q_n = int(q_n)
                q_a = int(q_a)
            except ValueError as exc:
                raise RuntimeError(
                    f'Вопрос или ответа на строке №{index}, '
                    'не соответствует представлению способному преобразовываться к числу'
                ) from exc

            _q_answers[q_n] = q_a

    for current_dir, dirs, files in os.walk(asb_dir):

        if current_dir == source_path:
            if QUESTIONS not in dirs:
                raise RuntimeError('Отсутствует директория `questions` с вопросами')
            continue

        if questions_dir == current_dir:
            questions_set = set(dirs)
            if len(dirs) != len(questions_set):
                raise RuntimeError('Почему-то длина не совпадает)')

            questions_set_to_validate = set([str(num) for num in range(1, len(questions_set) + 1)])

            if questions_set != questions_set_to_validate:
                raise RuntimeError(
                    f'Не хватает вопросов {questions_set_to_validate - questions_set} '
                    f'Также есть лишние вопросы: {questions_set - questions_set_to_validate}'
                )

            for question_number in questions_set:
                try:
                    int(question_number)
                except ValueError as exc:
                    raise RuntimeError(
                        f'Вопрос № {question_number} не является числом'
                    ) from exc
            continue

        if current_dir.startswith(questions_dir):
            if current_dir == questions_dir:
                raise RuntimeError('Почему-то директории совпадают')

            if questions_count is None:
                questions_count = len(files) - 1
            else:
                if questions_count + 1 != len(files):
                    raise RuntimeError(f'Количество вопросов меньше чем заявлено {questions_count} dir: {files}')

            question = None
            answers = []

            answers_numbers = set()

            for _file in files:
                if _file.startswith('q'):
                    question = os.path.join(current_dir, _file)
                    continue

                answer_num, *_ = _file.split('.', maxsplit=1)
                try:
                    answer_num = int(answer_num)
                except ValueError as exc:
                    raise RuntimeError(
                        f'Ответ {answer_num} в билете {current_dir} имеет не числовое представление'
                    ) from exc

                answers_numbers.add(answer_num)
                answers.append((answer_num, os.path.join(current_dir, _file)))

            question_number = int(os.path.basename(os.path.normpath(current_dir)))

            answer = _q_answers.get(question_number, None)
            if answer is None:
                raise RuntimeError(
                    f'Не существует такого ответа для вопроса №{question_number}'
                )

            questions_to_answers[question_number] = (question, answer, sorted(answers, key=lambda x: x[0]))

    return QuestionAnswerType.image_files, questions_to_answers
