from __future__ import annotations

def normalize(value: object) -> str:
    return ' '.join(str(value or '').strip().lower().split())

def grade_questions(questions: list[dict], answers: dict[str, object], passing_score: float = 70) -> dict:
    results=[]
    for q in questions:
        expected=normalize(q.get('correct_answer')); actual=normalize(answers.get(str(q.get('id'))))
        correct=actual == expected
        results.append({'question_id':q.get('id'),'correct':correct,'expected':q.get('correct_answer'),'answer':answers.get(str(q.get('id'))),'explanation':q.get('explanation',''),'skill_id':q.get('skill_id')})
    total=len(results); correct=sum(1 for r in results if r['correct']); score=round(correct/total*100,2) if total else 0
    return {'score':score,'passed':score>=passing_score,'correct_count':correct,'total':total,'results':results}
