import re

def extract_questions(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.read()

    questions = []
    seen_questions = set()  # 用于存储已经出现过的题目的组合

    # 处理单选题
    single_choice_pattern = re.compile(
        r'(\d+)\.\s*\(单选题\)\s*(.*?)\nA\s*(.*?)\nB\s*(.*?)\nC\s*(.*?)\nD\s*(.*?)\n我的答案:.*?正确答案:\s*(\w)',
        re.DOTALL)
    single_choice_matches = single_choice_pattern.findall(lines)

    for match in single_choice_matches:
        number, question, option_a, option_b, option_c, option_d, answer = match
        options = [option_a.strip(), option_b.strip(), option_c.strip(), option_d.strip()]
        question_key = (question.strip(), tuple(options), answer.strip())
        if question_key not in seen_questions:
            seen_questions.add(question_key)
            questions.append((number, "单选题", question.strip(), options, answer))

    # 处理判断题
    true_false_pattern = re.compile(r'(\d+)\.\s*\(判断题\)\s*(.*?)\nA\s*(.*?)\nB\s*(.*?)\n我的答案:.*?正确答案:\s*(\w)',
                                    re.DOTALL)
    true_false_matches = true_false_pattern.findall(lines)

    for match in true_false_matches:
        number, question, option_a, option_b, answer = match
        options = [option_a.strip(), option_b.strip()]
        question_key = (question.strip(), tuple(options), answer.strip())
        if question_key not in seen_questions:
            seen_questions.add(question_key)
            questions.append((number, "判断题", question.strip(), options, answer))

    # 处理填空题
    fill_in_the_blank_pattern = re.compile(
        r'(\d+)\.\s*\(填空题\)\s*(.*?)\n(?:我的答案：.*?)?\n正确答案：\n((?:\(.*?\).+?\n)+)',
        re.DOTALL)
    fill_in_the_blank_matches = fill_in_the_blank_pattern.findall(lines)

    for match in fill_in_the_blank_matches:
        number, question, answers_block = match
        question = re.sub(r'第[1-4]空', '', question.strip())  # 删除 "第1空" 到 "第4空"
        answers = re.findall(r"\((.*?)\)\s+(.+?)\n", answers_block)
        correct_answers = ', '.join(f"{option}: {text}" for option, text in answers)
        question_key = (question.strip(), tuple(), correct_answers.strip())  # 填空题没有选项，传入空元组
        if question_key not in seen_questions:
            seen_questions.add(question_key)
            questions.append((number, "填空题", question.strip(), [], correct_answers))

    # 替换正确答案的表达方式
    for i, (number, qtype, question, options, answer) in enumerate(questions):
        if answer == '对':
            answer = 'A'
        elif answer == '错':
            answer = 'B'
        questions[i] = (number, qtype, question, options, answer)

    return questions

def save_questions_to_file(questions, output_file_path):
    with open(output_file_path, 'w', encoding='utf-8') as file:
        for number, qtype, question, options, answer in questions:
            file.write(f"{number}. ({qtype}) {question}\n")
            if qtype != "填空题":
                for idx, option in enumerate(options):
                    file.write(f"    {chr(65 + idx)}. {option}\n")
            file.write(f"正确答案: {answer}\n\n")

if __name__ == "__main__":
    input_file_path = '题目.txt'
    output_file_path = '提取的题目.txt'

    questions = extract_questions(input_file_path)
    if questions:
        save_questions_to_file(questions, output_file_path)
        print(f"提取到的题目已保存到 {output_file_path}")
    else:
        print("没有提取到任何题目.")
