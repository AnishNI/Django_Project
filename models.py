from django.db import models
from django.contrib.auth.models import User

class SeekerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=255)
    course = models.CharField(max_length=255, blank=True, null=True)
    graduation = models.CharField(max_length=255, blank=True, null=True)
    skills = models.TextField(blank=True, null=True)
    contact_info = models.CharField(max_length=255, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    photo = models.ImageField(upload_to='photos/', blank=True, null=True)
    resume = models.FileField(upload_to='resumes/', blank=True, null=True)

    def __str__(self):
        return self.full_name

class Project(models.Model):
    candidate = models.ForeignKey(User, on_delete=models.CASCADE, related_name='projects')
    title = models.CharField(max_length=255)
    description = models.TextField()
    code_file = models.FileField(upload_to='project_code_files/', blank=True, null=True)
    image = models.ImageField(upload_to='project_images/', blank=True, null=True)
    video_link = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class RecruiterProfile(models.Model):
    recuiter_user = models.OneToOneField(User, on_delete=models.CASCADE)
    recuiter_company_name = models.CharField(max_length=255)
    recuiter_contact_info = models.CharField(max_length=255, blank=True, null=True)
    recuiter_Location= models.CharField(max_length=255,blank=True,null=True)
    recuiter_Address=models.CharField(max_length=255,blank=True,null=True)
    recuiter_email = models.EmailField(max_length=255, unique=True)

    def __str__(self):
        return self.recuiter_company_name

from django.utils.timesince import timesince
from django.utils import timezone

class Job(models.Model):
    recruiter = models.ForeignKey(User, on_delete=models.CASCADE, related_name='jobs')
    title = models.CharField(max_length=255)
    company = models.CharField(max_length=255)
    location = models.CharField(max_length=255, blank=True, null=True)
    experience = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    responsibilities = models.TextField(blank=True, null=True)
    requirements = models.TextField(blank=True, null=True)
    expiry_days = models.PositiveIntegerField(default=30)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} at {self.company}"

    @property
    def relative_time(self):
        now = timezone.now()
        return timesince(self.created_at, now) + " ago"

class Application(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
    ]

    candidate = models.ForeignKey(SeekerProfile, on_delete=models.CASCADE)
    job = models.ForeignKey(Job, on_delete=models.CASCADE)
    applied_at = models.DateTimeField(auto_now_add=True)
    date_applied = models.DateField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Pending')

    class Meta:
        unique_together = ('candidate', 'job')  # Prevent double applications
