from app.generator.answers import generate_answers
from app.generator.quesions import generate_questions_factory
from app.logic.shuffle import tickets_generator, shuffle_if_needed
from app.parser.parsers import parse_factory, FormatEnum

if __name__ == '__main__':
    questions_answers_type, questions_to_answers = parse_factory('./data/target_dir', FormatEnum.dir)

    tickets = tickets_generator(questions_to_answers, 5)
    questions_to_answers = shuffle_if_needed(questions_to_answers)

    generate_questions_factory('out_data/tickets', questions_to_answers, questions_answers_type, tickets)

    # generate_answers('out_data/answers_test.docx', tickets)
