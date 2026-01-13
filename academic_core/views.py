# academic_core/views.py
from rest_framework import viewsets, permissions, filters
from django.db.models import Prefetch

from .models import (
    Teacher, TuitionClass, Subject, SubjectAssignment,
    Student, Guardian, Enrollment
)
from .serializers import (
    TeacherSerializer, TuitionClassSerializer, SubjectSerializer,
    SubjectAssignmentSerializer, StudentSerializer, GuardianSerializer,
    EnrollmentSerializer
)


# Shared filter backends used by many viewsets
COMMON_FILTER_BACKENDS = [filters.SearchFilter, filters.OrderingFilter]


class TeacherViewSet(viewsets.ModelViewSet):
    """
    Teacher viewset.
    - searchable by first_name / last_name / email
    """
    queryset = Teacher.objects.all()
    serializer_class = TeacherSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = COMMON_FILTER_BACKENDS
    search_fields = ('first_name', 'last_name', 'email')
    ordering_fields = ('last_name', 'first_name', 'id')


class TuitionClassViewSet(viewsets.ModelViewSet):
    """
    TuitionClass viewset. Uses select_related on class_teacher so
    TuitionClassSerializer's nested teacher fields are available without extra queries.
    """
    queryset = TuitionClass.objects.select_related('class_teacher').all()
    serializer_class = TuitionClassSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = COMMON_FILTER_BACKENDS
    search_fields = ('class_id', 'name')
    ordering_fields = ('class_id', 'name')


class SubjectViewSet(viewsets.ModelViewSet):
    """
    Subject viewset.
    """
    queryset = Subject.objects.all()
    serializer_class = SubjectSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = COMMON_FILTER_BACKENDS
    search_fields = ('subject_id', 'name')
    ordering_fields = ('subject_id', 'name')


class SubjectAssignmentViewSet(viewsets.ModelViewSet):
    """
    SubjectAssignment viewset. Prefetch teacher + subject for compact nested serializers.
    """
    queryset = SubjectAssignment.objects.select_related('teacher', 'subject').all()
    serializer_class = SubjectAssignmentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = COMMON_FILTER_BACKENDS
    search_fields = ('assign_id', 'subject__name', 'teacher__first_name', 'teacher__last_name')
    ordering_fields = ('start_date', 'assign_id')


class StudentViewSet(viewsets.ModelViewSet):
    """
    Student viewset. Prefetch guardians and select_related current_class so nested fields
    in StudentSerializer are efficient.
    """
    queryset = Student.objects.select_related('current_class__class_teacher') \
                              .prefetch_related('guardians') \
                              .all()
    serializer_class = StudentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = COMMON_FILTER_BACKENDS
    search_fields = ('reg_no', 'first_name', 'last_name', 'phone', 'email')
    ordering_fields = ('reg_no', 'first_name', 'last_name')


class GuardianViewSet(viewsets.ModelViewSet):
    """
    Guardian viewset.
    """
    queryset = Guardian.objects.select_related('student').all()
    serializer_class = GuardianSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = COMMON_FILTER_BACKENDS
    search_fields = ('name', 'phone', 'email', 'student__reg_no')
    ordering_fields = ('name',)


class EnrollmentViewSet(viewsets.ModelViewSet):
    """
    Enrollment viewset. Use select_related for student and tuition_class to support nested serializer.
    """
    queryset = Enrollment.objects.select_related('student', 'tuition_class').all()
    serializer_class = EnrollmentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = COMMON_FILTER_BACKENDS
    search_fields = ('student__reg_no', 'tuition_class__class_id')
    ordering_fields = ('start_date',)
