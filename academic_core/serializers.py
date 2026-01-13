from rest_framework import serializers
from .models import (Teacher, TuitionClass, Subject, SubjectAssignment,
                     Student, Guardian, Enrollment)


class TeacherSerializer(serializers.ModelSerializer):
    class Meta:
        model = Teacher
        fields = ['id', 'title', 'first_name', 'last_name', 'phone', 'email']


class TuitionClassSerializer(serializers.ModelSerializer):
    # include teacher fields nested for convenience (may be null)
    class_teacher = TeacherSerializer(read_only=True)

    class Meta:
        model = TuitionClass
        fields = ['id', 'class_id', 'name', 'description', 'class_mode',
                  'fee_type', 'per_session_fee', 'monthly_fee',
                  'class_teacher', 'capacity', 'active']


class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = ['id', 'subject_id', 'name', 'description']


class SubjectAssignmentSerializer(serializers.ModelSerializer):
    # nested subject + teacher so UI has names
    subject = SubjectSerializer(read_only=True)
    teacher = TeacherSerializer(read_only=True)

    class Meta:
        model = SubjectAssignment
        fields = ['id', 'assign_id', 'subject', 'teacher', 'start_date', 'end_date', 'notes']


class GuardianSerializer(serializers.ModelSerializer):
    class Meta:
        model = Guardian
        fields = ['id', 'student', 'name', 'relationship', 'phone', 'whatsapp', 'email', 'is_primary']


class StudentSerializer(serializers.ModelSerializer):
    guardians = GuardianSerializer(many=True, read_only=True)
    current_class = TuitionClassSerializer(read_only=True)

    class Meta:
        model = Student
        fields = ['id', 'reg_no', 'profile_photo', 'first_name', 'last_name',
                  'dob', 'joined_date', 'nic', 'school', 'gender',
                  'current_class', 'address', 'phone', 'whatsapp', 'email', 'is_active', 'guardians']


class EnrollmentSerializer(serializers.ModelSerializer):
    student = StudentSerializer(read_only=True)
    tuition_class = TuitionClassSerializer(read_only=True)

    class Meta:
        model = Enrollment
        fields = ['id', 'student', 'tuition_class', 'start_date', 'end_date', 'active', 'fee_override']
