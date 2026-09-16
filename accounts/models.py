from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver


# =========================
# CUSTOM USER
# =========================

class CustomUser(AbstractUser):

    ROLE_CHOICES = (
        ('client', 'Client'),
        ('freelancer', 'Freelancer'),
    )

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='freelancer'
    )

    def is_client(self):
        return self.role == 'client'

    def is_freelancer(self):
        return self.role == 'freelancer'

    def save(self, *args, **kwargs):
        if self.pk:
            old_role = CustomUser.objects.filter(pk=self.pk).values_list('role', flat=True).first()
            if old_role and old_role != self.role:
                raise ValueError("Role cannot be changed after account creation.")
        super().save(*args, **kwargs)

    def __str__(self):
        return self.username


# =========================
# PROFILE
# =========================

class Profile(models.Model):

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='profile'
    )

    bio = models.TextField(blank=True)

    skills = models.CharField(
        max_length=500,
        blank=True
    )

    location = models.CharField(
        max_length=200,
        blank=True
    )

    education = models.CharField(
        max_length=200,
        blank=True
    )

    grad_year = models.PositiveIntegerField(
        null=True,
        blank=True
    )

    institution = models.CharField(
        max_length=200,
        blank=True
    )

    # Escrow / wallet points
    points = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0.00
    )

    def __str__(self):
        return f"{self.user.username}'s Profile"


@receiver(post_save, sender=CustomUser)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


# =========================
# JOB POST
# =========================

class JobPost(models.Model):

    STATUS_CHOICES = (
        ('open', 'Open'),
        ('in_progress', 'In Progress'),
        ('submitted', 'Submitted'),
        ('completed', 'Completed'),
    )

    client = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='posted_jobs'
    )

    freelancer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_jobs'
    )

    title = models.CharField(
        max_length=255
    )

    description = models.TextField()

    budget = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    location = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )

    deadline = models.DateField(
        blank=True,
        null=True
    )

    # Optional project links
    repo_url = models.URLField(
        blank=True,
        null=True
    )

    attachments_url = models.URLField(
        blank=True,
        null=True
    )

    # Freelancer submission
    submission_url = models.URLField(
        blank=True,
        null=True
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='open'
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    is_active = models.BooleanField(
        default=True
    )

    def __str__(self):
        return self.title


# =========================
# JOB APPLICATION
# =========================

class JobApplication(models.Model):

    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
    )

    applicant = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='applications'
    )

    job = models.ForeignKey(
        JobPost,
        on_delete=models.CASCADE,
        related_name='applications'
    )

    proposal = models.TextField(
        blank=True
    )

    bid_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )

    applied_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['applicant', 'job'],
                name='unique_job_application'
            )
        ]

    def __str__(self):
        return f"{self.applicant.username} - {self.job.title}"


# =========================
# PROJECT
# =========================

class Project(models.Model):

    client = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='client_projects'
    )

    freelancer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='freelancer_projects',
        null=True,
        blank=True
    )

    title = models.CharField(
        max_length=200
    )

    description = models.TextField()

    budget = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.title
# models.py — add this new model

class Message(models.Model):

    job = models.ForeignKey(
        JobPost,
        on_delete=models.CASCADE,
        related_name='messages'
    )

    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='sent_messages'
    )

    content = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)

    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"{self.sender.username}: {self.content[:30]}"
    