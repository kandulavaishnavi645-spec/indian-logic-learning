from django.db import migrations


def match_reference_question(apps, schema_editor):
    question_model = apps.get_model('home', 'QuizQuestion')
    question_model.objects.filter(
        prompt='According to the comparison with modern computing, what can pratyakṣa be compared with?',
    ).update(
        prompt='According to V. S. Sarma, what can be compared with pratyakṣa in modern computing?',
        explanation='Pratyakṣa means perception; in the paper’s comparison, it relates to data input from sensors.',
    )


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0004_refine_starter_quiz_questions'),
    ]

    operations = [
        migrations.RunPython(match_reference_question, migrations.RunPython.noop),
    ]
