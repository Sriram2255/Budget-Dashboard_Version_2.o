from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import uuid
import string
import random

# New Budget Model
class Budget(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='budgets')
    name = models.CharField(max_length=200)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    start_date = models.DateField()
    end_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} for {self.user.username}"

# New Expense Model
class Expense(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='expenses')
    budget = models.ForeignKey(Budget, on_delete=models.SET_NULL, null=True, blank=True, related_name='expenses')
    category = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    date = models.DateField(default=timezone.now)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.category} - {self.amount} on {self.date}"

# New Income Model
class Income(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='incomes')
    source = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    date = models.DateField(default=timezone.now)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.source} - {self.amount} on {self.date}"

class ProjectCosting(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('modification_requested', 'Modification Requested'),
    )
    
    DOMAIN_CHOICES = (
        ('civil', 'Civil'),
        ('mechanical', 'Mechanical'),
        ('both', 'Both Civil & Mechanical'),
    )
    
    project_name = models.CharField(max_length=200)
    domain = models.CharField(max_length=20, choices=DOMAIN_CHOICES, default='both')
    description = models.TextField()
    
    # Employee who submitted the costing
    submitted_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='submitted_costings')
    
    # Manpower requirements
    manpower_count = models.IntegerField(default=0)
    manpower_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    # Material requirements
    material_description = models.TextField(blank=True)
    material_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    # Other costs
    other_costs = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    other_costs_description = models.TextField(blank=True)
    
    # Total cost (calculated field)
    total_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    # Justification text
    justification = models.TextField()
    
    # Status tracking
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='pending')
    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='reviewed_costings')
    review_comments = models.TextField(blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.project_name} - {self.get_status_display()}"
    
    def save(self, *args, **kwargs):
        # Calculate total cost
        self.total_cost = self.manpower_cost + self.material_cost + self.other_costs
        super().save(*args, **kwargs)


class CostingJustificationFile(models.Model):
    project_costing = models.ForeignKey(ProjectCosting, on_delete=models.CASCADE, related_name='justification_files')
    file = models.FileField(upload_to='justification_files/')
    file_name = models.CharField(max_length=255)
    file_type = models.CharField(max_length=50)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Justification for {self.project_costing.project_name} - {self.file_name}"


class CostingRevision(models.Model):
    original_costing = models.ForeignKey(ProjectCosting, on_delete=models.CASCADE, related_name='revisions')
    revision_number = models.IntegerField()
    
    # Copied fields from original costing for version tracking
    manpower_count = models.IntegerField(default=0)
    manpower_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    material_description = models.TextField(blank=True)
    material_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    other_costs = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    other_costs_description = models.TextField(blank=True)
    total_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    justification = models.TextField()
    
    # Revision metadata
    revised_by = models.ForeignKey(User, on_delete=models.CASCADE)
    revised_at = models.DateTimeField(default=timezone.now)
    revision_comments = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.original_costing.project_name} - Revision {self.revision_number}"


# Enhanced Project Submission Model with Tracking
class ProjectSubmission(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('modification_requested', 'Modification Requested'),
        ('under_review', 'Under Review'),
    )
    
    DOMAIN_CHOICES = (
        ('civil', 'Civil Engineering'),
        ('mechanical', 'Mechanical Engineering'),
        ('electrical', 'Electrical Engineering'),
        ('both', 'Multi-Domain'),
    )
    
    PRIORITY_CHOICES = (
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    )
    
    # Tracking Information
    tracking_id = models.CharField(max_length=20, unique=True, blank=True)
    
    # Project Information
    project_name = models.CharField(max_length=200)
    project_description = models.TextField()
    domain = models.CharField(max_length=20, choices=DOMAIN_CHOICES)
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    
    # Financial Information
    estimated_budget = models.DecimalField(max_digits=15, decimal_places=2)
    manpower_count = models.IntegerField(default=0)
    manpower_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    material_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    equipment_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    other_costs = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_cost = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    
    # Timeline
    start_date = models.DateField()
    end_date = models.DateField()
    estimated_duration_days = models.IntegerField(default=0)
    
    # User Information
    submitted_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='submitted_projects')
    department = models.CharField(max_length=100, blank=True)
    contact_email = models.EmailField(blank=True)
    contact_phone = models.CharField(max_length=20, blank=True)
    
    # Review Information
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='pending')
    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='reviewed_projects')
    review_comments = models.TextField(blank=True)
    review_date = models.DateTimeField(null=True, blank=True)
    
    # Additional Information
    justification = models.TextField()
    risk_assessment = models.TextField(blank=True)
    expected_outcome = models.TextField(blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.tracking_id} - {self.project_name}"
    
    def save(self, *args, **kwargs):
        if not self.tracking_id:
            self.tracking_id = self.generate_tracking_id()
        
        # Calculate total cost
        self.total_cost = self.manpower_cost + self.material_cost + self.equipment_cost + self.other_costs
        
        # Calculate duration
        if self.start_date and self.end_date:
            delta = self.end_date - self.start_date
            self.estimated_duration_days = delta.days
        
        super().save(*args, **kwargs)
    
    def generate_tracking_id(self):
        """Generate a unique tracking ID"""
        prefix = "PRJ"
        timestamp = timezone.now().strftime("%y%m%d")
        random_suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
        return f"{prefix}{timestamp}{random_suffix}"
    
    def get_status_color(self):
        """Return color for status display"""
        colors = {
            'pending': 'warning',
            'approved': 'success',
            'rejected': 'danger',
            'modification_requested': 'info',
            'under_review': 'primary',
        }
        return colors.get(self.status, 'secondary')


# Notification System
class Notification(models.Model):
    NOTIFICATION_TYPES = (
        ('status_change', 'Status Change'),
        ('review_assigned', 'Review Assigned'),
        ('comment_added', 'Comment Added'),
        ('deadline_reminder', 'Deadline Reminder'),
        ('approval_required', 'Approval Required'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    project_submission = models.ForeignKey(ProjectSubmission, on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    title = models.CharField(max_length=200)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.title}"


# Project Files/Attachments
class ProjectFile(models.Model):
    project_submission = models.ForeignKey(ProjectSubmission, on_delete=models.CASCADE, related_name='files')
    file = models.FileField(upload_to='project_files/%Y/%m/%d/')
    file_name = models.CharField(max_length=255)
    file_type = models.CharField(max_length=50)
    file_size = models.BigIntegerField(default=0)
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    description = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.project_submission.tracking_id} - {self.file_name}"
    
    def save(self, *args, **kwargs):
        if self.file:
            self.file_size = self.file.size
        super().save(*args, **kwargs)


# (Add below your existing models — around line ~120–150 depending on your file length)

class ProjectItem(models.Model):
    project = models.ForeignKey('ProjectSubmission', on_delete=models.CASCADE, related_name='items')
    description = models.TextField()
    units_qty = models.CharField(max_length=100, null=True, blank=True)
    nos = models.IntegerField(null=True, blank=True)
    unit_price_total_mt = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    amount_inr = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return f"{self.description[:50]}..." if self.description else "Unnamed Item"



# Review Comments/Feedback
class ReviewComment(models.Model):
    project_submission = models.ForeignKey(ProjectSubmission, on_delete=models.CASCADE, related_name='comments')
    reviewer = models.ForeignKey(User, on_delete=models.CASCADE)
    comment = models.TextField()
    comment_type = models.CharField(max_length=20, choices=[
        ('general', 'General Comment'),
        ('approval', 'Approval Comment'),
        ('rejection', 'Rejection Comment'),
        ('modification', 'Modification Request'),
    ], default='general')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.project_submission.tracking_id} - Comment by {self.reviewer.username}"