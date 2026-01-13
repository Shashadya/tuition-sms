# academic_core/urls.py
from django.urls import path, include
from . import templates_views as tv
from rest_framework import routers
from . import views as api_views

app_name = 'academic_core'

urlpatterns = [
    path('', tv.index, name='index'),

    # -----------------------
    # TEACHERS
    # -----------------------
    path('teachers/', tv.TeacherListView.as_view(), name='teacher_list'),
    path('teachers/create/', tv.TeacherCreateView.as_view(), name='teacher_create'),
    path('teachers/<int:pk>/', tv.TeacherDetailView.as_view(), name='teacher_detail'),
    path('teachers/<int:pk>/edit/', tv.TeacherUpdateView.as_view(), name='teacher_update'),
    path('teachers/<int:pk>/delete/', tv.TeacherDeleteView.as_view(), name='teacher_delete'),

    # -----------------------
    # CLASSES
    # -----------------------
    path('classes/', tv.TuitionClassListView.as_view(), name='class_list'),
    path('classes/create/', tv.TuitionClassCreateView.as_view(), name='class_create'),
    path('classes/<int:pk>/', tv.TuitionClassDetailView.as_view(), name='class_detail'),
    path('classes/<int:pk>/edit/', tv.TuitionClassUpdateView.as_view(), name='class_update'),
    path('classes/<int:pk>/delete/', tv.TuitionClassDeleteView.as_view(), name='class_delete'),

    # -----------------------
    # SUBJECTS
    # -----------------------
    path('subjects/', tv.SubjectListView.as_view(), name='subject_list'),
    path('subjects/create/', tv.SubjectCreateView.as_view(), name='subject_create'),
    path('subjects/<int:pk>/edit/', tv.SubjectUpdateView.as_view(), name='subject_update'),
    path('subjects/<int:pk>/delete/', tv.SubjectDeleteView.as_view(), name='subject_delete'),
    # optional: subject detail (shows assignments)
    path('subjects/<int:pk>/', tv.SubjectDetailView.as_view(), name='subject_detail'),

    # -----------------------
    # SUBJECT ASSIGNMENTS
    # -----------------------
    path('subject-assignments/', tv.SubjectAssignmentListView.as_view(), name='subjectassign_list'),
    path('subject-assignments/create/', tv.SubjectAssignmentCreateView.as_view(), name='subjectassign_create'),
    path('subject-assignments/<int:pk>/edit/', tv.SubjectAssignmentUpdateView.as_view(), name='subjectassign_update'),
    path('subject-assignments/<int:pk>/delete/', tv.SubjectAssignmentDeleteView.as_view(), name='subjectassign_delete'),

    # -----------------------
    # STUDENTS
    # -----------------------
    path('students/', tv.StudentListView.as_view(), name='student_list'),
    path('students/create/', tv.StudentCreateView.as_view(), name='student_create'),
    path('students/<int:pk>/', tv.StudentDetailView.as_view(), name='student_detail'),
    path('students/<int:pk>/edit/', tv.StudentUpdateView.as_view(), name='student_update'),
    path('students/<int:pk>/delete/', tv.StudentDeleteView.as_view(), name='student_delete'),

    # -----------------------
    # ENROLLMENT (ADMIN ONLY)
    # -----------------------
    path('enrollments/create/', tv.EnrollmentCreateView.as_view(), name='enrollment_create'),
]

# ---------------------------------------------------------
# API ROUTER (DRF)
# ---------------------------------------------------------
router = routers.DefaultRouter()
router.register(r'teachers', api_views.TeacherViewSet)
router.register(r'classes', api_views.TuitionClassViewSet)
router.register(r'subjects', api_views.SubjectViewSet)
router.register(r'subject-assignments', api_views.SubjectAssignmentViewSet)
router.register(r'students', api_views.StudentViewSet)
router.register(r'guardians', api_views.GuardianViewSet)
router.register(r'enrollments', api_views.EnrollmentViewSet)

urlpatterns += [
    path('api/v1/', include(router.urls)),
]
