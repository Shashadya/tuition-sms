# academic_core/templates_views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.db import transaction, IntegrityError
from django.forms import inlineformset_factory
from django.contrib import messages
from django.db.models.deletion import ProtectedError
import re

# CBV-friendly decorators (from accounts/decorators.py)
from accounts.decorators import admin_required_cbv, staff_or_admin_required_cbv

from .models import (
    Teacher, TuitionClass, Subject, SubjectAssignment,
    Student, Enrollment, Guardian
)
from .forms import (
    TeacherForm, TuitionClassForm, SubjectForm, SubjectAssignmentForm,
    StudentForm, EnrollmentForm, GuardianForm
)


def index(request):
    ctx = {
        'total_students': Student.objects.count(),
        'total_teachers': Teacher.objects.count(),
        'total_classes': TuitionClass.objects.count(),
    }
    return render(request, 'academic_core/index.html', ctx)


# -----------------------
# Teacher views
# -----------------------
class TeacherListView(ListView):
    model = Teacher
    template_name = 'academic_core/teacher_list.html'
    context_object_name = 'teachers'
    queryset = Teacher.objects.all().order_by('last_name', 'first_name')


@staff_or_admin_required_cbv
class TeacherCreateView(CreateView):
    model = Teacher
    form_class = TeacherForm
    template_name = 'academic_core/teacher_form.html'
    success_url = reverse_lazy('academic_core:teacher_list')


class TeacherDetailView(DetailView):
    model = Teacher
    template_name = 'academic_core/teacher_detail.html'
    context_object_name = 'teacher'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        # show current assignments for teacher (most recent first)
        ctx['assignments'] = (
            self.object.assignments.select_related('subject')
            .order_by('-start_date')
        )
        # show classes taught
        ctx['classes'] = (
            self.object.tuition_classes.select_related('class_teacher')
            .order_by('class_id')
        )
        return ctx


@staff_or_admin_required_cbv
class TeacherUpdateView(UpdateView):
    model = Teacher
    form_class = TeacherForm
    template_name = 'academic_core/teacher_form.html'
    success_url = reverse_lazy('academic_core:teacher_list')


@admin_required_cbv
class TeacherDeleteView(DeleteView):
    model = Teacher
    template_name = 'academic_core/teacher_confirm_delete.html'
    success_url = reverse_lazy('academic_core:teacher_list')

    def post(self, request, *args, **kwargs):
        """
        Attempt delete. If ProtectedError due to related classes or assignments,
        show a reassign UI so admin can move those relations to other teacher(s)
        before deleting. If reassign targets provided, perform move then delete.
        """
        self.object = self.get_object()

        # If admin submitted reassign targets, perform reassign then delete
        reassign_classes_to = request.POST.get('reassign_classes_to')
        reassign_assignments_to = request.POST.get('reassign_assignments_to')

        if reassign_classes_to or reassign_assignments_to:
            with transaction.atomic():
                moved_classes = 0
                moved_assignments = 0
                if reassign_classes_to:
                    try:
                        target_teacher = Teacher.objects.get(pk=int(reassign_classes_to))
                        moved_classes = TuitionClass.objects.filter(class_teacher=self.object).update(class_teacher=target_teacher)
                    except (Teacher.DoesNotExist, ValueError):
                        messages.error(request, "Target teacher for classes not found.")
                        return redirect('academic_core:teacher_delete', pk=self.object.pk)

                if reassign_assignments_to:
                    try:
                        target_teacher2 = Teacher.objects.get(pk=int(reassign_assignments_to))
                        moved_assignments = SubjectAssignment.objects.filter(teacher=self.object).update(teacher=target_teacher2)
                    except (Teacher.DoesNotExist, ValueError):
                        messages.error(request, "Target teacher for subject assignments not found.")
                        return redirect('academic_core:teacher_delete', pk=self.object.pk)

                # After reassigning, delete the teacher
                self.object.delete()

            messages.success(request, f"Reassigned {moved_classes} classes and {moved_assignments} assignments, and deleted teacher.")
            return redirect(self.success_url)

        # No reassign request: attempt normal delete; if ProtectedError then show UI
        try:
            return super().post(request, *args, **kwargs)
        except ProtectedError:
            # find dependents
            dependent_classes = TuitionClass.objects.filter(class_teacher=self.object)
            dependent_assignments = SubjectAssignment.objects.filter(teacher=self.object)
            other_teachers = Teacher.objects.exclude(pk=self.object.pk).order_by('last_name', 'first_name')
            return render(request, 'academic_core/teacher_cannot_delete.html', {
                'object': self.object,
                'dependent_classes': dependent_classes,
                'dependent_assignments': dependent_assignments,
                'other_teachers': other_teachers,
            })

    def delete(self, request, *args, **kwargs):
        obj = self.get_object()
        name = str(obj)
        response = super().delete(request, *args, **kwargs)
        messages.success(request, f"Teacher '{name}' deleted.")
        return response


# -----------------------
# Class views
# -----------------------
class TuitionClassListView(ListView):
    model = TuitionClass
    template_name = 'academic_core/class_list.html'
    context_object_name = 'classes'
    queryset = TuitionClass.objects.all().order_by('class_id')


@staff_or_admin_required_cbv
class TuitionClassCreateView(CreateView):
    model = TuitionClass
    form_class = TuitionClassForm
    template_name = 'academic_core/class_form.html'
    success_url = reverse_lazy('academic_core:class_list')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        last_class = TuitionClass.objects.order_by('-id').first()
        ctx['last_class_id'] = last_class.class_id if last_class else None
        return ctx


class TuitionClassDetailView(DetailView):
    model = TuitionClass
    template_name = 'academic_core/class_detail.html'
    context_object_name = 'class_obj'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        # show students currently in this class and assignments (if useful)
        ctx['students'] = self.object.students.select_related('current_class').order_by('reg_no')
        ctx['teacher'] = self.object.class_teacher
        return ctx


@staff_or_admin_required_cbv
class TuitionClassUpdateView(UpdateView):
    model = TuitionClass
    form_class = TuitionClassForm
    template_name = 'academic_core/class_form.html'
    success_url = reverse_lazy('academic_core:class_list')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        last_class = TuitionClass.objects.order_by('-id').first()
        ctx['last_class_id'] = last_class.class_id if last_class else None
        return ctx


@admin_required_cbv
class TuitionClassDeleteView(DeleteView):
    model = TuitionClass
    template_name = 'academic_core/class_confirm_delete.html'
    success_url = reverse_lazy('academic_core:class_list')

    def post(self, request, *args, **kwargs):
        """
        If reassign_to provided -> move students to target class then delete.
        If ProtectedError raised -> render a friendly UI asking admin to choose target class.
        """
        self.object = self.get_object()
        reassign_to = request.POST.get('reassign_to')
        if reassign_to:
            try:
                target = TuitionClass.objects.get(pk=int(reassign_to))
            except (TuitionClass.DoesNotExist, ValueError):
                messages.error(request, "Chosen target class not found.")
                return redirect('academic_core:class_delete', pk=self.object.pk)

            with transaction.atomic():
                students_qs = Student.objects.filter(current_class=self.object)
                count = students_qs.update(current_class=target)
                self.object.delete()
            messages.success(request, f"Moved {count} student(s) to '{target}' and deleted class.")
            return redirect(self.success_url)

        try:
            return super().post(request, *args, **kwargs)
        except ProtectedError:
            dependents = Student.objects.filter(current_class=self.object)
            other_classes = TuitionClass.objects.exclude(pk=self.object.pk).order_by('class_id')
            return render(request, 'academic_core/class_cannot_delete.html', {
                'object': self.object,
                'dependents': dependents,
                'other_classes': other_classes,
            })

    def delete(self, request, *args, **kwargs):
        obj = self.get_object()
        name = str(obj)
        response = super().delete(request, *args, **kwargs)
        messages.success(request, f"Class '{name}' deleted.")
        return response


# -----------------------
# Subject views
# -----------------------
class SubjectListView(ListView):
    model = Subject
    template_name = 'academic_core/subject_list.html'
    context_object_name = 'subjects'
    queryset = Subject.objects.all().order_by('subject_id')


@staff_or_admin_required_cbv
class SubjectCreateView(CreateView):
    model = Subject
    form_class = SubjectForm
    template_name = 'academic_core/subject_form.html'
    success_url = reverse_lazy('academic_core:subject_list')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        last = Subject.objects.order_by('-id').first()
        ctx['last_subject_id'] = last.subject_id if last else None
        return ctx


@staff_or_admin_required_cbv
class SubjectUpdateView(UpdateView):
    model = Subject
    form_class = SubjectForm
    template_name = 'academic_core/subject_form.html'
    success_url = reverse_lazy('academic_core:subject_list')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        last = Subject.objects.order_by('-id').first()
        ctx['last_subject_id'] = last.subject_id if last else None
        return ctx


@admin_required_cbv
class SubjectDeleteView(DeleteView):
    model = Subject
    template_name = 'academic_core/subject_confirm_delete.html'
    success_url = reverse_lazy('academic_core:subject_list')

    def post(self, request, *args, **kwargs):
        """
        If reassign_to provided -> move assignments to target subject then delete.
        If ProtectedError -> show UI to choose target subject.
        """
        self.object = self.get_object()
        reassign_to = request.POST.get('reassign_to')
        if reassign_to:
            try:
                target = Subject.objects.get(pk=int(reassign_to))
            except (Subject.DoesNotExist, ValueError):
                messages.error(request, "Chosen target subject not found.")
                return redirect('academic_core:subject_delete', pk=self.object.pk)

            with transaction.atomic():
                count = SubjectAssignment.objects.filter(subject=self.object).update(subject=target)
                self.object.delete()
            messages.success(request, f"Reassigned {count} assignments to '{target}' and deleted subject.")
            return redirect(self.success_url)

        try:
            return super().post(request, *args, **kwargs)
        except ProtectedError:
            dependents = SubjectAssignment.objects.filter(subject=self.object)
            other_subjects = Subject.objects.exclude(pk=self.object.pk).order_by('subject_id')
            return render(request, 'academic_core/subject_cannot_delete.html', {
                'object': self.object,
                'dependents': dependents,
                'other_subjects': other_subjects,
            })

    def delete(self, request, *args, **kwargs):
        obj = self.get_object()
        name = str(obj)
        response = super().delete(request, *args, **kwargs)
        messages.success(request, f"Subject '{name}' deleted.")
        return response


# -----------------------
# SubjectAssignment (list / create / update / delete)
# -----------------------
class SubjectAssignmentListView(ListView):
    model = SubjectAssignment
    template_name = 'academic_core/subjectassign_list.html'
    context_object_name = 'assignments'
    queryset = SubjectAssignment.objects.select_related('subject', 'teacher').order_by('-start_date')


@staff_or_admin_required_cbv
class SubjectAssignmentCreateView(CreateView):
    model = SubjectAssignment
    form_class = SubjectAssignmentForm
    template_name = 'academic_core/subjectassign_form.html'
    success_url = reverse_lazy('academic_core:subjectassign_list')

    def get_initial(self):
        initial = super().get_initial()
        # allow pre-selecting subject via ?subject=ID
        subject_pk = self.request.GET.get('subject')
        if subject_pk:
            initial['subject'] = subject_pk

        # prefilling assign id with "next" from last record if the field is empty
        last = SubjectAssignment.objects.order_by('-id').first()
        if last and not initial.get('assign_id'):
            prev = last.assign_id or ''
            m = re.search(r'(\d+)$', prev)
            if m:
                num = m.group(1)
                nxt = str(int(num) + 1).zfill(len(num))
                base = prev[:m.start(1)]
                initial['assign_id'] = base + nxt
            else:
                initial['assign_id'] = prev + '-1'
        return initial

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        last = SubjectAssignment.objects.order_by('-id').first()
        ctx['last_assign_id'] = last.assign_id if last else None
        return ctx

    def form_valid(self, form):
        """
        Enforce uniqueness of (subject, teacher) at the form level as well as catching DB IntegrityError.
        Model already has a UniqueConstraint; here we surface a friendly error message.
        """
        try:
            return super().form_valid(form)
        except IntegrityError:
            form.add_error(None, "An assignment for this subject and teacher already exists.")
            return self.form_invalid(form)


@staff_or_admin_required_cbv
class SubjectAssignmentUpdateView(UpdateView):
    model = SubjectAssignment
    form_class = SubjectAssignmentForm
    template_name = 'academic_core/subjectassign_form.html'
    success_url = reverse_lazy('academic_core:subjectassign_list')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        last = SubjectAssignment.objects.order_by('-id').first()
        ctx['last_assign_id'] = last.assign_id if last else None
        return ctx

    def form_valid(self, form):
        try:
            return super().form_valid(form)
        except IntegrityError:
            form.add_error(None, "An assignment for this subject and teacher already exists.")
            return self.form_invalid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Please fix the errors in the assignment form.")
        return super().form_invalid(form)


@admin_required_cbv
class SubjectAssignmentDeleteView(DeleteView):
    model = SubjectAssignment
    template_name = 'academic_core/subjectassign_confirm_delete.html'
    success_url = reverse_lazy('academic_core:subjectassign_list')

    def delete(self, request, *args, **kwargs):
        obj = self.get_object()
        name = str(obj)
        response = super().delete(request, *args, **kwargs)
        messages.success(request, f"Assignment '{name}' deleted.")
        return response


# Subject detail view to expose assignments for the subject
class SubjectDetailView(DetailView):
    model = Subject
    template_name = 'academic_core/subject_detail.html'
    context_object_name = 'subject'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['assignments'] = self.object.assignments.select_related('teacher').order_by('-start_date')
        return ctx


# -----------------------
# Student (create / detail / update / delete)
# -----------------------
class StudentListView(ListView):
    model = Student
    template_name = 'academic_core/student_list.html'
    context_object_name = 'students'
    queryset = Student.objects.select_related('current_class').order_by('reg_no')


@staff_or_admin_required_cbv
class StudentCreateView(CreateView):
    model = Student
    form_class = StudentForm
    template_name = 'academic_core/student_form.html'
    success_url = reverse_lazy('academic_core:student_list')

    def get_guardian_formset_class(self):
        return inlineformset_factory(
            Student, Guardian,
            form=GuardianForm,
            fields=('name', 'relationship', 'phone', 'whatsapp', 'email', 'is_primary'),
            extra=1,
            can_delete=True
        )

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        last_student = Student.objects.order_by('-id').first()
        ctx['last_reg_no'] = last_student.reg_no if last_student else None

        GuardianFormSet = self.get_guardian_formset_class()
        if self.request.method == 'POST':
            ctx['guardian_formset'] = GuardianFormSet(self.request.POST, prefix='guardians')
        else:
            ctx['guardian_formset'] = GuardianFormSet(prefix='guardians')
        return ctx

    def form_valid(self, form):
        GuardianFormSet = self.get_guardian_formset_class()
        formset = GuardianFormSet(self.request.POST, prefix='guardians')

        # Validate formset
        if not formset.is_valid():
            return self.form_invalid(form)

        # Ensure at least one non-deleted guardian exists
        non_deleted = [f for f in formset.forms if f.cleaned_data and not f.cleaned_data.get('DELETE', False)]
        if len(non_deleted) == 0:
            form.add_error(None, "Please add at least one guardian.")
            return self.form_invalid(form)

        with transaction.atomic():
            student = form.save()
            formset.instance = student
            formset.save()

            # Enforce exactly one primary guardian:
            primaries = student.guardians.filter(is_primary=True)
            if primaries.count() == 0:
                first = student.guardians.first()
                if first:
                    first.is_primary = True
                    first.save(update_fields=['is_primary'])
            elif primaries.count() > 1:
                # keep earliest marked primary, unset others
                keep = primaries.earliest('id')
                student.guardians.exclude(pk=keep.pk).update(is_primary=False)

        return super().form_valid(form)

    def form_invalid(self, form):
        context = self.get_context_data(form=form)
        if 'guardian_formset' not in context:
            GuardianFormSet = self.get_guardian_formset_class()
            context['guardian_formset'] = GuardianFormSet(self.request.POST, prefix='guardians')
        return render(self.request, self.template_name, context)


class StudentDetailView(DetailView):
    model = Student
    template_name = 'academic_core/student_detail.html'
    context_object_name = 'student'


@staff_or_admin_required_cbv
class StudentUpdateView(UpdateView):
    model = Student
    form_class = StudentForm
    template_name = 'academic_core/student_form.html'
    success_url = reverse_lazy('academic_core:student_list')

    def get_guardian_formset_class(self):
        return inlineformset_factory(
            Student, Guardian,
            form=GuardianForm,
            fields=('name', 'relationship', 'phone', 'whatsapp', 'email', 'is_primary'),
            extra=0,
            can_delete=True
        )

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        last_student = Student.objects.order_by('-id').first()
        ctx['last_reg_no'] = last_student.reg_no if last_student else None

        GuardianFormSet = self.get_guardian_formset_class()
        if self.request.method == 'POST':
            ctx['guardian_formset'] = GuardianFormSet(self.request.POST, instance=self.object, prefix='guardians')
        else:
            ctx['guardian_formset'] = GuardianFormSet(instance=self.object, prefix='guardians')
        return ctx

    def form_valid(self, form):
        GuardianFormSet = self.get_guardian_formset_class()
        formset = GuardianFormSet(self.request.POST, instance=self.object, prefix='guardians')

        if not formset.is_valid():
            return self.form_invalid(form)

        non_deleted = [f for f in formset.forms if f.cleaned_data and not f.cleaned_data.get('DELETE', False)]
        if len(non_deleted) == 0:
            form.add_error(None, "Please keep at least one guardian.")
            return self.form_invalid(form)

        with transaction.atomic():
            student = form.save()
            formset.instance = student
            formset.save()

            primaries = student.guardians.filter(is_primary=True)
            if primaries.count() == 0:
                first = student.guardians.first()
                if first:
                    first.is_primary = True
                    first.save(update_fields=['is_primary'])
            elif primaries.count() > 1:
                keep = primaries.earliest('id')
                student.guardians.exclude(pk=keep.pk).update(is_primary=False)

        messages.success(self.request, f"Student '{student.reg_no}' updated.")
        return super().form_valid(form)

    def form_invalid(self, form):
        """
        When either the Student form or the guardian formset is invalid we:
        - bind the guardian formset so errors are preserved,
        - log the errors to the server console (helps debugging),
        - render the template with both form and guardian_formset included.
        """
        GuardianFormSet = self.get_guardian_formset_class()
        # bind posted formset to display errors
        formset = GuardianFormSet(self.request.POST, instance=self.object, prefix='guardians')

        # Server-side debug (check runserver console)
        # Remove or replace prints with logging in production
        print("=== Student form errors ===")
        print(form.errors.as_json() if hasattr(form.errors, 'as_json') else form.errors)
        print("=== Guardian formset non-form errors ===")
        print(formset.non_form_errors())
        print("=== Guardian formset per-form errors ===")
        for i, gf in enumerate(formset.forms):
            print(f"Form #{i} errors:", gf.errors)

        # Add a warning message so the user sees an alert
        messages.error(self.request, "Please fix the errors and try again.")

        # Make sure template receives the bound formset so it can show errors
        context = self.get_context_data(form=form)
        context['guardian_formset'] = formset

        return render(self.request, self.template_name, context)



@admin_required_cbv
class StudentDeleteView(DeleteView):
    model = Student
    template_name = 'academic_core/student_confirm_delete.html'
    success_url = reverse_lazy('academic_core:student_list')

    def delete(self, request, *args, **kwargs):
        obj = self.get_object()
        name = str(obj)
        response = super().delete(request, *args, **kwargs)
        messages.success(request, f"Student '{name}' deleted.")
        return response


# -----------------------
# Enrollment (admin only)
# -----------------------
@admin_required_cbv
class EnrollmentCreateView(CreateView):
    model = Enrollment
    form_class = EnrollmentForm
    template_name = 'academic_core/enrollment_form.html'
    success_url = reverse_lazy('academic_core:enrollment_create')
