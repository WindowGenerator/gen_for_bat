import random
from typing import List, Generator, Hashable, Any

from app.parser.base import QuestionsToAnswers

TicketsListType = List[List[str]]


def shuffle_if_needed(
        questions_to_answers: QuestionsToAnswers,
        with_shuffle_q: bool = False,
        with_shuffle_a: bool = False,
) -> QuestionsToAnswers:
    if with_shuffle_q:
        questions_to_answers = _shuffle_q(questions_to_answers)
    if with_shuffle_a:
        questions_to_answers = _shuffle_a(questions_to_answers)
    return questions_to_answers


def tickets_generator(
        questions_to_answers: QuestionsToAnswers,
        questions_count: int,
        shuffle_function: str = "split_on_chunks",
) -> TicketsListType:
    _validate_questions(questions_to_answers, questions_count)

    if shuffle_function == "split_on_chunks":
        return list(_get_ticket_generator_split_on_chunks(questions_to_answers, questions_count))


def _get_ticket_generator_split_on_chunks(questions_to_answers: QuestionsToAnswers, questions_count: int) -> Generator:
    # TODO: не надо парсить то, что уже пришло мысль про это: `int(quesion.split('.')[0])``
    questions_list: List[int] = sorted(questions_to_answers.keys(), key=sort_questions)

    return _chunks(questions_list, questions_count)


def _shuffle_q(questions_to_answers: QuestionsToAnswers) -> QuestionsToAnswers:
    new_questions_to_answers: QuestionsToAnswers = dict()

    questions_n_list = list(questions_to_answers.keys())
    random.shuffle(questions_n_list)

    for index, q in enumerate(questions_n_list):
        new_questions_to_answers[index + 1] = questions_to_answers[q]

    return new_questions_to_answers


def _shuffle_a(questions_to_answers: QuestionsToAnswers) -> QuestionsToAnswers:
    new_questions_to_answers: QuestionsToAnswers = dict()

    for q_n in questions_to_answers.keys():
        current_question_image_path, answer, current_answers_image_paths = questions_to_answers[q_n]

        random.shuffle(current_answers_image_paths)

        new_current_answers_image_paths = []

        print(current_answers_image_paths)

        new_answer = answer
        for index, _answer in enumerate(current_answers_image_paths):
            answer_n, answer_path = _answer
            if answer_n == answer:
                print(index + 1)
                new_answer = index + 1
            new_current_answers_image_paths.append((index + 1, answer_path))

        new_questions_to_answers[q_n] = (current_question_image_path, new_answer, new_current_answers_image_paths)

    return new_questions_to_answers


def _validate_questions(questions_to_answers: QuestionsToAnswers, questions_count: int) -> None:
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


def _chunks(l: List[Any], n: int):
    for i in range(0, len(l), n):
        yield l[i:i + n]


def sort_questions(question: Hashable):
    if isinstance(question, str):
        return int(question.split('.')[0])
    if isinstance(question, int):
        return question

    raise RuntimeError('sort questions не удался(')
