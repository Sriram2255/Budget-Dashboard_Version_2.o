# ... existing imports ...
from django.contrib.auth.decorators import login_required, user_passes_test
from django.forms import modelformset_factory
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.db.models import Sum, Count, Q
from django.utils import timezone
import json
import csv
from io import StringIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from django.shortcuts import render # This line is redundant, already imported above
from django.http import HttpResponse # This line is redundant, already imported above
from django.contrib.auth.forms import UserCreationForm # Import UserCreationForm
from django.contrib.auth import login # Import login function

from .models import (Budget, Expense, Income, ProjectCosting, CostingJustificationFile, CostingRevision,
                    ProjectSubmission, ProjectFile, ReviewComment, Notification)
from .forms import (BudgetForm, ExpenseForm, IncomeForm, ProjectCostingForm, 
                   JustificationFileForm, CostingReviewForm, CostingRevisionForm,
                   ProjectSubmissionForm, ProjectFileForm, ReviewCommentForm, ProjectReviewForm)

# Helper function to check if user is a superuser
# This function MUST be defined before any view that uses @user_passes_test(is_superuser)
def is_superuser(user):
    return user.is_superuser

@login_required
def home(request):
    return HttpResponse("Welcome to the Budgeting App!")

@login_required
def create_budget(request):
    if request.method == 'POST':
        form = BudgetForm(request.POST)
        if form.is_valid():
            budget = form.save(commit=False)
            budget.user = request.user
            budget.save()
            messages.success(request, 'Budget created successfully!')
            return redirect('home') # Redirect to a relevant page after creation
    else:
        form = BudgetForm()
    return render(request, 'budget/create_budget.html', {'form': form})

@login_required
def budget_detail(request, budget_id):
    budget = get_object_or_404(Budget, pk=budget_id, user=request.user)
    expenses = budget.expenses.all()
    incomes = budget.incomes.all()
    
    context = {
        'budget': budget,
        'expenses': expenses,
        'incomes': incomes,
    }
    return render(request, 'budget/budget_detail.html', context)

# Add the add_expense view
@login_required
def add_expense(request, budget_id):
    budget = get_object_or_404(Budget, pk=budget_id, user=request.user)
    if request.method == 'POST':
        form = ExpenseForm(request.POST)
        if form.is_valid():
            expense = form.save(commit=False)
            expense.budget = budget
            expense.user = request.user # Assuming Expense model has a user field
            expense.save()
            messages.success(request, 'Expense added successfully!')
            return redirect('budget_detail', budget_id=budget.pk)
    else:
        form = ExpenseForm()
    return render(request, 'budget/add_expense.html', {'form': form, 'budget': budget})

# Add the add_income view
@login_required
def add_income(request, budget_id):
    budget = get_object_or_404(Budget, pk=budget_id, user=request.user)
    if request.method == 'POST':
        form = IncomeForm(request.POST)
        if form.is_valid():
            income = form.save(commit=False)
            income.budget = budget
            income.user = request.user # Assuming Income model has a user field
            income.save()
            messages.success(request, 'Income added successfully!')
            return redirect('budget_detail', budget_id=budget.pk)
    else:
        form = IncomeForm()
    return render(request, 'budget/add_income.html', {'form': form, 'budget': budget})

@login_required
def project_costing_list(request):
    """View for employees to see their submitted costings"""
    costings = ProjectCosting.objects.filter(submitted_by=request.user).order_by('-created_at')
    return render(request, 'budget/project_costing_list.html', {'costings': costings})

@login_required
def create_project_costing(request):
    """View for employees to create new project costing"""
    if request.method == 'POST':
        form = ProjectCostingForm(request.POST)
        file_form = JustificationFileForm(request.POST, request.FILES)
        
        if form.is_valid():
            costing = form.save(commit=False)
            costing.submitted_by = request.user
            costing.save()
            
            # Handle file uploads
            files = request.FILES.getlist('file')
            for f in files:
                file_instance = CostingJustificationFile(
                    project_costing=costing,
                    file=f,
                    file_name=f.name,
                    file_type=f.content_type
                )
                file_instance.save()
            
            messages.success(request, 'Project costing submitted successfully!')
            return redirect('project_costing_list')
    else:
        form = ProjectCostingForm()
        file_form = JustificationFileForm()
    
    return render(request, 'budget/create_project_costing.html', {
        'form': form,
        'file_form': file_form
    })

@login_required
def project_costing_detail(request, pk):
    """View for employees to see details of a specific costing"""
    costing = get_object_or_404(ProjectCosting, pk=pk)
    
    # Check if the user is the owner or a superuser
    if costing.submitted_by != request.user and not request.user.is_superuser:
        messages.error(request, "You don't have permission to view this costing.")
        return redirect('project_costing_list')
    
    justification_files = costing.justification_files.all()
    revisions = costing.revisions.all().order_by('revision_number')
    
    return render(request, 'budget/project_costing_detail.html', {
        'costing': costing,
        'justification_files': justification_files,
        'revisions': revisions
    })

@login_required
def edit_project_costing(request, pk):
    """View for employees to edit a costing that needs modification"""
    costing = get_object_or_404(ProjectCosting, pk=pk)
    
    # Check if the user is the owner and the costing is in modification_requested status
    if costing.submitted_by != request.user:
        messages.error(request, "You don't have permission to edit this costing.")
        return redirect('project_costing_list')
    
    if costing.status != 'modification_requested':
        messages.error(request, "This costing cannot be edited in its current status.")
        return redirect('project_costing_detail', pk=costing.pk)
    
    if request.method == 'POST':
        form = CostingRevisionForm(request.POST, instance=costing)
        file_form = JustificationFileForm(request.POST, request.FILES)
        
        if form.is_valid():
            # Create a revision record before saving changes
            revision_count = costing.revisions.count()
            revision = CostingRevision(
                original_costing=costing,
                revision_number=revision_count + 1,
                manpower_count=costing.manpower_count,
                manpower_cost=costing.manpower_cost,
                material_description=costing.material_description,
                material_cost=costing.material_cost,
                other_costs=costing.other_costs,
                other_costs_description=costing.other_costs_description,
                total_cost=costing.total_cost,
                justification=costing.justification,
                revised_by=request.user,
                revision_comments=f"Revision after modification request: {costing.review_comments}"
            )
            revision.save()
            
            # Save the updated costing
            updated_costing = form.save(commit=False)
            updated_costing.status = 'pending'  # Reset to pending for review
            updated_costing.save()
            
            # Handle new file uploads
            files = request.FILES.getlist('file')
            for f in files:
                file_instance = CostingJustificationFile(
                    project_costing=costing,
                    file=f,
                    file_name=f.name,
                    file_type=f.content_type
                )
                file_instance.save()
            
            messages.success(request, 'Project costing updated successfully and submitted for review!')
            return redirect('project_costing_detail', pk=costing.pk)
    else:
        form = CostingRevisionForm(instance=costing)
        file_form = JustificationFileForm()
    
    return render(request, 'budget/edit_project_costing.html', {
        'form': form,
        'file_form': file_form,
        'costing': costing
    })

@login_required
@user_passes_test(is_superuser) # This is line 165 in your traceback
def superuser_dashboard(request):
    """Dashboard view for superusers to review all costings"""
    # Get filter parameters
    status_filter = request.GET.get('status', '')
    domain_filter = request.GET.get('domain', '')
    
    # Base queryset
    costings = ProjectCosting.objects.all().order_by('-created_at')
    
    # Apply filters
    if status_filter:
        costings = costings.filter(status=status_filter)
    if domain_filter:
        costings = costings.filter(domain=domain_filter)
    
    # Statistics for dashboard
    total_costings = ProjectCosting.objects.count()
    pending_costings = ProjectCosting.objects.filter(status='pending').count()
    approved_costings = ProjectCosting.objects.filter(status='approved').count()
    rejected_costings = ProjectCosting.objects.filter(status='rejected').count()
    modification_requested = ProjectCosting.objects.filter(status='modification_requested').count()
    
    # Domain statistics
    civil_costings = ProjectCosting.objects.filter(domain='civil').count()
    mechanical_costings = ProjectCosting.objects.filter(domain='mechanical').count()
    both_domains = ProjectCosting.objects.filter(domain='both').count()
    
    # Cost statistics
    total_approved_cost = ProjectCosting.objects.filter(status='approved').aggregate(Sum('total_cost'))['total_cost__sum'] or 0
    
    context = {
        'costings': costings,
        'total_costings': total_costings,
        'pending_costings': pending_costings,
        'approved_costings': approved_costings,
        'rejected_costings': rejected_costings,
        'modification_requested': modification_requested,
        'civil_costings': civil_costings,
        'mechanical_costings': mechanical_costings,
        'both_domains': both_domains,
        'total_approved_cost': total_approved_cost,
        'status_filter': status_filter,
        'domain_filter': domain_filter
    }
    
    return render(request, 'budget/superuser_dashboard.html', context)

@login_required
@user_passes_test(is_superuser)
def review_project_costing(request, pk):
    """View for superusers to review and approve/reject costings"""
    costing = get_object_or_404(ProjectCosting, pk=pk)
    justification_files = costing.justification_files.all()
    revisions = costing.revisions.all().order_by('revision_number')
    
    if request.method == 'POST':
        form = CostingReviewForm(request.POST, instance=costing)
        if form.is_valid():
            updated_costing = form.save(commit=False)
            updated_costing.reviewed_by = request.user
            updated_costing.save()
            
            status_message = {
                'approved': 'approved',
                'rejected': 'rejected',
                'modification_requested': 'sent back for modification'
            }
            
            messages.success(request, f'Project costing has been {status_message.get(updated_costing.status, "updated")}!')
            return redirect('superuser_dashboard')
    else:
        form = CostingReviewForm(instance=costing)
    
    return render(request, 'budget/review_project_costing.html', {
        'costing': costing,
        'form': form,
        'justification_files': justification_files,
        'revisions': revisions
    })

@login_required
@user_passes_test(is_superuser)
def generate_quotation(request, pk):
    """Generate a quotation PDF for an approved project costing"""
    costing = get_object_or_404(ProjectCosting, pk=pk)
    
    if costing.status != 'approved':
        messages.error(request, "Quotation can only be generated for approved costings.")
        return redirect('review_project_costing', pk=costing.pk)
    
    # Create a PDF response
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="quotation_{costing.project_name}.pdf"'
    
    # Create the PDF document
    doc = SimpleDocTemplate(response, pagesize=letter)
    elements = []
    
    # Add styles
    styles = getSampleStyleSheet()
    title_style = styles['Heading1']
    subtitle_style = styles['Heading2']
    normal_style = styles['Normal']
    
    # Add title
    elements.append(Paragraph(f"Quotation for {costing.project_name}", title_style))
    elements.append(Paragraph(f"Domain: {costing.get_domain_display()}", subtitle_style))
    elements.append(Paragraph(f"Date: {timezone.now().strftime('%Y-%m-%d')}", normal_style))
    elements.append(Paragraph(f"Project Description: {costing.description}", normal_style))
    elements.append(Paragraph(" ", normal_style))  # Spacer
    
    # Create cost breakdown table
    data = [
        ["Item", "Description", "Cost (₹)"],
        ["Manpower", f"{costing.manpower_count} personnel", f"{costing.manpower_cost:.2f}"],
        ["Materials", costing.material_description, f"{costing.material_cost:.2f}"],
        ["Other Costs", costing.other_costs_description, f"{costing.other_costs:.2f}"],
        ["Total", "", f"{costing.total_cost:.2f}"]
    ]
    
    table = Table(data, colWidths=[100, 250, 100])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (2, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (2, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (2, 0), 'CENTER'),
        ('FONTNAME', (0, 0), (2, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (2, 0), 12),
        ('BOTTOMPADDING', (0, 0), (2, 0), 12),
        ('BACKGROUND', (0, 1), (2, 3), colors.beige),
        ('BACKGROUND', (0, 4), (2, 4), colors.grey),
        ('TEXTCOLOR', (0, 4), (2, 4), colors.whitesmoke),
        ('FONTNAME', (0, 4), (2, 4), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('ALIGN', (2, 1), (2, 4), 'RIGHT'),
    ]))
    
    elements.append(table)
    elements.append(Paragraph(" ", normal_style))  # Spacer
    
    # Terms and conditions
    elements.append(Paragraph("Terms and Conditions:", subtitle_style))
    elements.append(Paragraph("1. This quotation is valid for 30 days from the date of issue.", normal_style))
    elements.append(Paragraph("2. 50% advance payment required to initiate the project.", normal_style))
    elements.append(Paragraph("3. Remaining payment due upon project completion.", normal_style))
    elements.append(Paragraph("4. Taxes as applicable will be charged extra.", normal_style))
    
    # Build the PDF
    doc.build(elements)
    return response

@login_required
def dashboard_data(request):
    """API endpoint to provide data for dashboard visualizations"""
    # Status distribution
    status_data = ProjectCosting.objects.values('status').annotate(count=Count('status'))
    
    # Domain distribution
    domain_data = ProjectCosting.objects.values('domain').annotate(count=Count('domain'))
    
    # Monthly cost trends (approved projects)
    monthly_data = ProjectCosting.objects.filter(status='approved').extra({
        'month': "EXTRACT(month FROM created_at)",
        'year': "EXTRACT(year FROM created_at)"
    }).values('month', 'year').annotate(
        total=Sum('total_cost')
    ).order_by('year', 'month')
    
    # Format for chart.js
    formatted_monthly_data = [
        {
            'month': f"{int(item['month'])}/{int(item['year'])}",
            'total': float(item['total'])
        } for item in monthly_data
    ]
    
    return JsonResponse({
        'status_data': list(status_data),
        'domain_data': list(domain_data),
        'monthly_data': formatted_monthly_data
    })

# Add the edit_expense view
@login_required
def edit_expense(request, budget_id, expense_id):
    budget = get_object_or_404(Budget, pk=budget_id, user=request.user)
    expense = get_object_or_404(Expense, pk=expense_id, budget=budget)
    
    if request.method == 'POST':
        form = ExpenseForm(request.POST, instance=expense)
        if form.is_valid():
            form.save()
            messages.success(request, 'Expense updated successfully!')
            return redirect('budget_detail', budget_id=budget.pk)
    else:
        form = ExpenseForm(instance=expense)
        
    return render(request, 'budget/edit_expense.html', {'form': form, 'budget': budget, 'expense': expense})

# Add the edit_income view
@login_required
def edit_income(request, budget_id, income_id):
    budget = get_object_or_404(Budget, pk=budget_id, user=request.user)
    income = get_object_or_404(Income, pk=income_id, budget=budget)
    
    if request.method == 'POST':
        form = IncomeForm(request.POST, instance=income)
        if form.is_valid():
            form.save()
            messages.success(request, 'Income updated successfully!')
            return redirect('budget_detail', budget_id=budget.pk)
    else:
        form = IncomeForm(instance=income)
        
    return render(request, 'budget/edit_income.html', {'form': form, 'budget': budget, 'income': income})

# Add the delete_expense view
@login_required
def delete_expense(request, budget_id, expense_id):
    budget = get_object_or_404(Budget, pk=budget_id, user=request.user)
    expense = get_object_or_404(Expense, pk=expense_id, budget=budget)
    
    if request.method == 'POST': # Deletion should typically be handled via POST request
        expense.delete()
        messages.success(request, 'Expense deleted successfully!')
        return redirect('budget_detail', budget_id=budget.pk)
    
    # For a GET request, you might want to render a confirmation page.
    # For now, we'll just redirect to budget detail with a message if not POST.
    # Or, you could render a simple confirmation template:
    # return render(request, 'budget/confirm_delete_expense.html', {'budget': budget, 'expense': expense})
    messages.info(request, 'Please confirm deletion via POST request.')
    return redirect('budget_detail', budget_id=budget.pk)

# Add the delete_income view
@login_required
def delete_income(request, budget_id, income_id):
    budget = get_object_or_404(Budget, pk=budget_id, user=request.user)
    income = get_object_or_404(Income, pk=income_id, budget=budget)
    
    if request.method == 'POST': # Deletion should typically be handled via POST request
        income.delete()
        messages.success(request, 'Income deleted successfully!')
        return redirect('budget_detail', budget_id=budget.pk)
    
    # For a GET request, you might want to render a confirmation page.
    # For now, we'll just redirect to budget detail with a message if not POST.
    messages.info(request, 'Please confirm deletion via POST request.')
    return redirect('budget_detail', budget_id=budget.pk)


# Enhanced Dashboard Views
@login_required
def user_dashboard(request):
    """Dashboard for normal users to submit and track projects"""
    # Get user's submissions
    user_submissions = ProjectSubmission.objects.filter(submitted_by=request.user).order_by('-created_at')
    
    # Get user's notifications
    notifications = Notification.objects.filter(user=request.user, is_read=False).order_by('-created_at')[:5]
    
    # Statistics
    total_submissions = user_submissions.count()
    pending_submissions = user_submissions.filter(status='pending').count()
    approved_submissions = user_submissions.filter(status='approved').count()
    rejected_submissions = user_submissions.filter(status='rejected').count()
    
    context = {
        'user_submissions': user_submissions[:10],  # Show latest 10
        'notifications': notifications,
        'total_submissions': total_submissions,
        'pending_submissions': pending_submissions,
        'approved_submissions': approved_submissions,
        'rejected_submissions': rejected_submissions,
    }
    
    return render(request, 'budget/user_dashboard.html', context)


@login_required
def submit_project(request):
    """View for users to submit new projects"""
    if request.method == 'POST':
        form = ProjectSubmissionForm(request.POST)
        file_form = ProjectFileForm(request.POST, request.FILES)
        
        if form.is_valid():
            project = form.save(commit=False)
            project.submitted_by = request.user
            project.save()
            
            # Handle file uploads
            files = request.FILES.getlist('file')
            for f in files:
                file_instance = ProjectFile(
                    project_submission=project,
                    file=f,
                    file_name=f.name,
                    file_type=f.content_type,
                    uploaded_by=request.user
                )
                file_instance.save()
            
            # Create notification for superusers
            superusers = User.objects.filter(is_superuser=True)
            for superuser in superusers:
                Notification.objects.create(
                    user=superuser,
                    project_submission=project,
                    notification_type='approval_required',
                    title=f'New Project Submission: {project.tracking_id}',
                    message=f'A new project "{project.project_name}" has been submitted and requires review.'
                )
            
            messages.success(request, f'Project submitted successfully! Tracking ID: {project.tracking_id}')
            return redirect('user_dashboard')
    else:
        form = ProjectSubmissionForm()
        file_form = ProjectFileForm()
    
    return render(request, 'budget/submit_project.html', {
        'form': form,
        'file_form': file_form
    })


@login_required
def project_detail(request, tracking_id):
    """View for users to see project details"""
    project = get_object_or_404(ProjectSubmission, tracking_id=tracking_id)
    
    # Check if user is the owner or a superuser
    if project.submitted_by != request.user and not request.user.is_superuser:
        messages.error(request, "You don't have permission to view this project.")
        return redirect('user_dashboard')
    
    files = project.files.all()
    comments = project.comments.all()
    
    return render(request, 'budget/project_detail.html', {
        'project': project,
        'files': files,
        'comments': comments
    })


@login_required
@user_passes_test(is_superuser)
def admin_dashboard(request):
    """Enhanced dashboard for superusers to review projects"""
    # Get filter parameters
    status_filter = request.GET.get('status', '')
    domain_filter = request.GET.get('domain', '')
    priority_filter = request.GET.get('priority', '')
    
    # Base queryset
    projects = ProjectSubmission.objects.all().order_by('-created_at')
    
    # Apply filters
    if status_filter:
        projects = projects.filter(status=status_filter)
    if domain_filter:
        projects = projects.filter(domain=domain_filter)
    if priority_filter:
        projects = projects.filter(priority=priority_filter)
    
    # Statistics
    total_projects = ProjectSubmission.objects.count()
    pending_projects = ProjectSubmission.objects.filter(status='pending').count()
    approved_projects = ProjectSubmission.objects.filter(status='approved').count()
    rejected_projects = ProjectSubmission.objects.filter(status='rejected').count()
    under_review = ProjectSubmission.objects.filter(status='under_review').count()
    
    # Domain statistics
    domain_stats = ProjectSubmission.objects.values('domain').annotate(count=Count('domain'))
    
    # Priority statistics
    priority_stats = ProjectSubmission.objects.values('priority').annotate(count=Count('priority'))
    
    # Cost statistics
    total_approved_cost = ProjectSubmission.objects.filter(status='approved').aggregate(Sum('total_cost'))['total_cost__sum'] or 0
    
    context = {
        'projects': projects[:20],  # Show latest 20
        'total_projects': total_projects,
        'pending_projects': pending_projects,
        'approved_projects': approved_projects,
        'rejected_projects': rejected_projects,
        'under_review': under_review,
        'domain_stats': domain_stats,
        'priority_stats': priority_stats,
        'total_approved_cost': total_approved_cost,
        'status_filter': status_filter,
        'domain_filter': domain_filter,
        'priority_filter': priority_filter,
    }
    
    return render(request, 'budget/admin_dashboard.html', context)


@login_required
@user_passes_test(is_superuser)
def review_project(request, tracking_id):
    """View for superusers to review and approve/reject projects"""
    project = get_object_or_404(ProjectSubmission, tracking_id=tracking_id)
    files = project.files.all()
    comments = project.comments.all()
    
    if request.method == 'POST':
        form = ProjectReviewForm(request.POST, instance=project)
        comment_form = ReviewCommentForm(request.POST)
        
        if form.is_valid():
            old_status = project.status
            updated_project = form.save(commit=False)
            updated_project.reviewed_by = request.user
            updated_project.review_date = timezone.now()
            updated_project.save()
            
            # Create comment if provided
            if comment_form.is_valid() and comment_form.cleaned_data.get('comment'):
                comment = comment_form.save(commit=False)
                comment.project_submission = project
                comment.reviewer = request.user
                comment.save()
            
            # Create notification for the project submitter
            Notification.objects.create(
                user=project.submitted_by,
                project_submission=project,
                notification_type='status_change',
                title=f'Project Status Updated: {project.tracking_id}',
                message=f'Your project "{project.project_name}" status has been changed to {project.get_status_display()}.'
            )
            
            status_messages = {
                'approved': 'Project approved successfully!',
                'rejected': 'Project rejected.',
                'modification_requested': 'Project sent back for modification.',
                'under_review': 'Project marked as under review.',
            }
            
            messages.success(request, status_messages.get(updated_project.status, 'Project updated successfully!'))
            return redirect('admin_dashboard')
    else:
        form = ProjectReviewForm(instance=project)
        comment_form = ReviewCommentForm()
    
    return render(request, 'budget/review_project.html', {
        'project': project,
        'form': form,
        'comment_form': comment_form,
        'files': files,
        'comments': comments
    })


@login_required
def notifications(request):
    """View to show all notifications for a user"""
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
    
    # Mark all notifications as read
    Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
    
    return render(request, 'budget/notifications.html', {
        'notifications': notifications
    })


@login_required
def mark_notification_read(request, notification_id):
    """Mark a specific notification as read"""
    notification = get_object_or_404(Notification, id=notification_id, user=request.user)
    notification.is_read = True
    notification.save()
    
    return JsonResponse({'status': 'success'})


@login_required
def project_tracking(request):
    """View for users to track their project status"""
    tracking_id = request.GET.get('tracking_id', '')
    project = None
    
    if tracking_id:
        try:
            project = ProjectSubmission.objects.get(tracking_id=tracking_id)
            # Check if user is the owner or a superuser
            if project.submitted_by != request.user and not request.user.is_superuser:
                project = None
                messages.error(request, "You don't have permission to view this project.")
        except ProjectSubmission.DoesNotExist:
            messages.error(request, "Project not found with the given tracking ID.")
    
    return render(request, 'budget/project_tracking.html', {
        'project': project,
        'tracking_id': tracking_id
    })

# Add the export_csv view
@login_required
def export_csv(request, budget_id):
    """Export budget data to CSV format"""
    budget = get_object_or_404(Budget, pk=budget_id, user=request.user)
    
    # Create CSV response
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="budget_{budget.name}_{budget_id}.csv"'
    
    writer = csv.writer(response)
    
    # Write budget header
    writer.writerow(['Budget Information'])
    writer.writerow(['Name', budget.name])
    writer.writerow(['Description', budget.description])
    writer.writerow(['Created', budget.created_at])
    writer.writerow([])
    
    # Write expenses
    writer.writerow(['Expenses'])
    writer.writerow(['Description', 'Amount', 'Date', 'Category'])
    for expense in budget.expenses.all():
        writer.writerow([expense.description, expense.amount, expense.date, expense.category])
    
    writer.writerow([])
    
    # Write incomes
    writer.writerow(['Incomes'])
    writer.writerow(['Description', 'Amount', 'Date', 'Source'])
    for income in budget.incomes.all():
        writer.writerow([income.description, income.amount, income.date, income.source])
    
    return response

# Add the register view
def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user) # Log the user in immediately after registration
            messages.success(request, 'Registration successful!')
            return redirect('home') # Redirect to your home page or dashboard