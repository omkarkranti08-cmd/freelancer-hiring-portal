from decimal import Decimal
from django.db import transaction
from django.core.exceptions import ValidationError
from .models import JobPost, JobApplication, Profile


class EscrowService:

    @staticmethod
    @transaction.atomic
    def create_job_with_escrow(client, form_data):
        if not client.is_client():
            raise ValidationError("Only Client accounts can create job postings.")

        client_profile, _ = Profile.objects.select_for_update().get_or_create(user=client)
        budget = Decimal(str(form_data.get('budget', 0)))

        if budget <= 0:
            raise ValidationError("Job budget must be greater than zero.")

        if client_profile.points < budget:
            raise ValidationError(
                f"Insufficient escrow balance! Required: ${budget} pts. Available: ${client_profile.points} pts."
            )

        # Deduct escrow funds upfront upon job creation
        client_profile.points -= budget
        client_profile.save(update_fields=['points'])

        job = JobPost.objects.create(
            client=client,
            title=form_data['title'],
            description=form_data['description'],
            budget=budget,
            location=form_data.get('location') or 'Remote',
            deadline=form_data.get('deadline'),
            repo_url=form_data.get('repo_url'),
            attachments_url=form_data.get('attachments_url'),
            status='open'
        )
        return job

    @staticmethod
    @transaction.atomic
    def hire_freelancer(job, application):
        if job.status != 'open':
            raise ValidationError("This project is no longer open for hire.")

        if application.job != job:
            raise ValidationError("Application does not match this job post.")

        # Update contract details & status
        job.freelancer = application.applicant
        job.status = 'in_progress'
        job.save(update_fields=['freelancer', 'status'])

        # Update winning proposal
        application.status = 'accepted'
        application.save(update_fields=['status'])

        # Reject all other active applications for this job
        JobApplication.objects.filter(
            job=job,
            status='pending'
        ).exclude(id=application.id).update(status='rejected')

    @staticmethod
    @transaction.atomic
    def complete_job_and_release_escrow(job, requested_by):
        if job.client != requested_by:
            raise ValidationError("Only the hiring client can approve completion and release funds.")

        if job.status not in ['in_progress', 'submitted']:
            raise ValidationError("Only contracts in progress or submitted can be completed.")

        if not job.freelancer:
            raise ValidationError("No freelancer assigned to this contract.")

        # Lock freelancer profile row and deposit escrow release
        freelancer_profile, _ = Profile.objects.select_for_update().get_or_create(user=job.freelancer)
        freelancer_profile.points += job.budget
        freelancer_profile.save(update_fields=['points'])

        job.status = 'completed'
        job.save(update_fields=['status'])

    @staticmethod
    @transaction.atomic
    def submit_code_repository(job, freelancer, submission_url):
        if job.freelancer != freelancer:
            raise ValidationError("You are not the assigned freelancer for this project.")

        if job.status not in ['in_progress', 'submitted']:
            raise ValidationError("Cannot submit work for contracts that are completed or closed.")

        if not submission_url:
            raise ValidationError("Submission URL cannot be blank.")

        job.submission_url = submission_url
        job.status = 'submitted'
        job.save(update_fields=['submission_url', 'status'])