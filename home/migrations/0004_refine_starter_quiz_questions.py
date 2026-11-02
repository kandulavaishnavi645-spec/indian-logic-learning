from django.db import migrations


STARTER_QUESTIONS = [
    {
        'old_prompt': 'Which of these is a recognized means of knowledge (pramāṇa) in Nyāya?',
        'prompt': 'Which of the following is a means of valid knowledge (pramāṇa) in Nyāya?',
        'options': ['Karma', 'Anumāna', 'Mokṣa', 'Saṃsāra'],
        'correct_option': 1,
        'explanation': 'Anumāna, or inference, is one of the means of valid knowledge described in Nyāya.',
    },
    {
        'old_prompt': 'What is a central focus of the Vaiśeṣika school of philosophy?',
        'prompt': 'What is the main focus of Vaiśeṣika philosophy?',
        'options': [
            'Ritual action and interpretation of the Vedas',
            'Classification of reality',
            'Spiritual practice and discipline',
            'Ultimate reality through meditation',
        ],
        'correct_option': 1,
        'explanation': 'Vaiśeṣika classifies reality into categories known as padārthas.',
    },
    {
        'old_prompt': 'Which component of a knowledge-based AI system applies logical rules to derive conclusions?',
        'prompt': 'Which component of a knowledge-based AI system applies logical rules to derive conclusions?',
        'options': [
            'Knowledge acquisition',
            'Knowledge base',
            'Inference engine',
            'User interface',
        ],
        'correct_option': 2,
        'explanation': 'The inference engine applies rules to facts in the knowledge base to derive conclusions.',
    },
    {
        'old_prompt': 'In the Nyāya five-member argument, which part states the claim to be established?',
        'prompt': 'In Nyāya logic, which part of the five-member argument gives a general example?',
        'options': ['Pratijñā', 'Hetu', 'Udāharaṇa', 'Nigamana'],
        'correct_option': 2,
        'explanation': 'Udāharaṇa provides the general example that supports an inference.',
    },
    {
        'old_prompt': 'What makes a rule-based knowledge system different from a plain data store?',
        'prompt': 'According to the comparison with modern computing, what can pratyakṣa be compared with?',
        'options': [
            'Inference engine',
            'Data input from sensors',
            'Knowledge base',
            'Expert testimony',
        ],
        'correct_option': 1,
        'explanation': 'Pratyakṣa means perception; a limited computing comparison is data gathered from sensors.',
    },
]


def refine_starter_questions(apps, schema_editor):
    question_model = apps.get_model('home', 'QuizQuestion')
    for data in STARTER_QUESTIONS:
        question = question_model.objects.filter(
            prompt=data['old_prompt'],
        ).first()
        if question:
            question.prompt = data['prompt']
            question.options = data['options']
            question.correct_option = data['correct_option']
            question.explanation = data['explanation']
            question.save(update_fields=[
                'prompt',
                'options',
                'correct_option',
                'explanation',
            ])


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0003_shortanswerquestion'),
    ]

    operations = [
        migrations.RunPython(refine_starter_questions, migrations.RunPython.noop),
    ]
