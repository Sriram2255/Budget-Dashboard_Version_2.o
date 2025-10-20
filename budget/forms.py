from django import forms
from .models import (
    Budget, Expense, Income, ProjectCosting,
    CostingJustificationFile, CostingRevision,
    ProjectSubmission, ProjectFile, ReviewComment
)

class BudgetForm(forms.ModelForm):
    class Meta:
        model = Budget
        fields = ['name', 'amount', 'start_date', 'end_date']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
        }

class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = ['budget', 'category', 'amount', 'date', 'description']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
        }

class IncomeForm(forms.ModelForm):
    class Meta:
        model = Income
        fields = ['source', 'amount', 'date', 'description']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
        }

class ProjectCostingForm(forms.ModelForm):
    class Meta:
        model = ProjectCosting
        fields = [
            'project_name', 'domain', 'description', 'manpower_count',
            'manpower_cost', 'material_description', 'material_cost',
            'other_costs', 'other_costs_description', 'justification'
        ]

class JustificationFileForm(forms.ModelForm):
    class Meta:
        model = CostingJustificationFile
        fields = ['file', 'file_name', 'file_type'] # file_name and file_type might be auto-populated in view

class CostingReviewForm(forms.ModelForm):
    class Meta:
        model = ProjectCosting
        fields = ['status', 'review_comments']

class CostingRevisionForm(forms.ModelForm):
    class Meta:
        model = CostingRevision
        fields = [
            'revision_number', 'manpower_count', 'manpower_cost',
            'material_description', 'material_cost', 'other_costs',
            'other_costs_description', 'justification', 'revision_comments'
        ]


# Enhanced Forms for New System
class ProjectSubmissionForm(forms.ModelForm):
    class Meta:
        model = ProjectSubmission
        fields = [
            'project_name', 'project_description', 'domain', 'priority',
            'estimated_budget', 'manpower_count', 'manpower_cost',
            'material_cost', 'equipment_cost', 'other_costs',
            'start_date', 'end_date', 'department', 'contact_email',
            'contact_phone', 'justification', 'risk_assessment', 'expected_outcome'
        ]
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'end_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'project_description': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
            'justification': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
            'risk_assessment': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'expected_outcome': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'project_name': forms.TextInput(attrs={'class': 'form-control'}),
            'department': forms.TextInput(attrs={'class': 'form-control'}),
            'contact_email': forms.EmailInput(attrs={'class': 'form-control'}),
            'contact_phone': forms.TextInput(attrs={'class': 'form-control'}),
            'estimated_budget': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'manpower_count': forms.NumberInput(attrs={'class': 'form-control'}),
            'manpower_cost': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'material_cost': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'equipment_cost': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'other_costs': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'domain': forms.Select(attrs={'class': 'form-control'}),
            'priority': forms.Select(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add Bootstrap classes to all fields
        for field_name, field in self.fields.items():
            if field.widget.attrs.get('class'):
                field.widget.attrs['class'] += ' form-control'
            else:
                field.widget.attrs['class'] = 'form-control'


class ProjectFileForm(forms.ModelForm):
    class Meta:
        model = ProjectFile
        fields = ['file', 'description']
        widgets = {
            'file': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
        }


class ReviewCommentForm(forms.ModelForm):
    class Meta:
        model = ReviewComment
        fields = ['comment', 'comment_type']
        widgets = {
            'comment': forms.Textarea(attrs={'rows': 4, 'class': 'form-control', 'placeholder': 'Enter your review comments...'}),
            'comment_type': forms.Select(attrs={'class': 'form-control'}),
        }


class ProjectReviewForm(forms.ModelForm):
    class Meta:
        model = ProjectSubmission
        fields = ['status', 'review_comments']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-control'}),
            'review_comments': forms.Textarea(attrs={'rows': 4, 'class': 'form-control', 'placeholder': 'Enter review comments...'}),
        }