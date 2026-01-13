# academic_core/tests/test_core.py
from django.test import TestCase
from academic_core.models import Teacher, TuitionClass, Student, Subject, SubjectAssignment, Enrollment

class CoreModelsTest(TestCase):
    def test_create_teacher_class_student_enrollment(self):
        t = Teacher.objects.create(first_name='John', last_name='Doe')
        cls = TuitionClass.objects.create(class_id='T1', name='Math A', per_session_fee='500.00', class_teacher=t)
        student = Student.objects.create(reg_no='S001', first_name='Amy', last_name='Smith', current_class=cls)
        self.assertEqual(str(student), 'S001 - Amy Smith')
        enr = Enrollment.objects.create(student=student, tuition_class=cls)
        self.assertTrue(enr.active)
