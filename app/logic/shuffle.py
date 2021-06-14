from random import sample
from typing import List, Generator, Hashable, Union

from app.parser.base import QuestionInVarsType, QuestionsToAnswers


TicketsListType = List[List[str]]


def tickets_generator(
    questions_to_answers: QuestionsToAnswers,
    questions_count: int, 
    shuffle_function: str = "split_on_chunks"
) -> TicketsListType:
    if shuffle_function == "split_on_chunks":
        return list(_get_ticket_generator(questions_to_answers, questions_count))


def _get_ticket_generator(questions_to_answers: QuestionsToAnswers, questions_count: int) -> Generator:
    all_questions_count_real = len(questions_to_answers.keys())

    if questions_count > all_questions_count_real:
        raise ValueError(
            "Вопросов для билета не может быть больше общего количества вопросов"
        )

    if all_questions_count_real % questions_count != 0:
        raise ValueError(
            f"Общее количество вопросов {all_questions_count_real} "
            f"не делится нацело на количество вопросов {questions_count} в одном билете"
        )

    # TODO: не надо парсить то, что уже пришло мысль про это: `int(quesion.split('.')[0])``
    questions_list: List[int] = sorted(questions_to_answers.keys(), key=sort_quesions)

    return _chunks(questions_list, questions_count)


def _chunks(l, n):
    for i in range(0, len(l), n):
        yield l[i:i+n]


def sort_quesions(quesion: Hashable):
    if isinstance(quesion, str):
        return int(quesion.split('.')[0])
    if isinstance(quesion, int):
        return quesion
    
    raise RuntimeError('sort questions не удался(')
