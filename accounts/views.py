from django.contrib.auth import get_user_model, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.exceptions import ValidationError

from .forms import RegisterForm, JobPostForm, ProfileForm
from .models import JobPost, JobApplication, Profile, Project, Message
from .services import EscrowService

User = get_user_model()

def home(request):
    jobs = JobPost.objects.filter(status='open', is_active=True).order_by('-created_at')
    return render(request, 'home.html', {'jobs': jobs})

def browse_jobs(request):
    jobs = JobPost.objects.filter(is_active=True).order_by('-created_at')
    return render(request, 'browse_jobs.html', {'jobs': jobs})

def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Account created successfully!")
            return redirect('client_dashboard' if user.is_client() else 'freelancer_dashboard')
    else:
        form = RegisterForm()
    return render(request, 'register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('client_dashboard' if user.is_client() else 'freelancer_dashboard')
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})

@login_required
def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect('home')

def profile_view(request, username):
    profile_user = get_object_or_404(User, username=username)
    profile, _ = Profile.objects.get_or_create(user=profile_user)
    return render(request, 'profile.html', {'profile_user': profile_user, 'profile': profile})

@login_required
def edit_profile(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully!")
            return redirect('profile', username=request.user.username)
    else:
        form = ProfileForm(instance=profile)
    return render(request, 'edit_profile.html', {'form': form})

@login_required
def project_workspace_view(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    return render(request, 'workspace.html', {'project': project})

@login_required
def create_job_view(request):
    if not request.user.is_client():
        messages.error(request, "Only clients can create jobs.")
        return redirect('freelancer_dashboard')

    if request.method == 'POST':
        form = JobPostForm(request.POST)
        if form.is_valid():
            try:
                EscrowService.create_job_with_escrow(request.user, form.cleaned_data)
                messages.success(request, "Project posted successfully!")
                return redirect('client_dashboard')
            except ValidationError as e:
                messages.error(request, str(e))
    else:
        form = JobPostForm()

    return render(request, 'create_job.html', {'form': form})

def job_detail_view(request, job_id):
    job = get_object_or_404(JobPost, id=job_id)
    has_applied = False
    if request.user.is_authenticated:
        has_applied = JobApplication.objects.filter(job=job, applicant=request.user).exists()
    return render(request, 'job_detail.html', {'job': job, 'has_applied': has_applied})

@login_required
def apply_to_job(request, job_id):
    job = get_object_or_404(JobPost, id=job_id, status='open', is_active=True)

    if not request.user.is_freelancer():
        messages.error(request, "Only freelancers can apply for jobs.")
        return redirect('browse_jobs')

    if request.method == 'POST':
        proposal = request.POST.get('proposal', '').strip()
        bid_amount = request.POST.get('bid_amount') or job.budget

        try:
            application, created = JobApplication.objects.get_or_create(
                job=job,
                applicant=request.user,
                defaults={'proposal': proposal, 'bid_amount': bid_amount}
            )
            if created:
                messages.success(request, "Proposal submitted successfully!")
            else:
                messages.info(request, "You have already applied for this job.")
        except Exception as e:
            messages.error(request, f"Unable to submit proposal: {e}")

    return redirect('job_detail', job_id=job.id)



@login_required
def accept_proposal(request, application_id):
    application = get_object_or_404(JobApplication, id=application_id)
    if application.job.client != request.user:
        messages.error(request, "You are not allowed to accept this proposal.")
        return redirect('client_dashboard')

    try:
        EscrowService.hire_freelancer(application.job, application)
        messages.success(request, f"Proposal accepted! Assigned to {application.applicant.username}.")
    except ValidationError as e:
        messages.error(request, str(e))

    return redirect('client_dashboard')

@login_required
def reject_proposal(request, application_id):
    application = get_object_or_404(JobApplication, id=application_id)
    if application.job.client != request.user:
        messages.error(request, "You are not allowed to reject this proposal.")
        return redirect('client_dashboard')

    application.status = 'rejected'
    application.save(update_fields=['status'])
    messages.info(request, "Proposal rejected.")
    return redirect('client_dashboard')

@login_required
def submit_project_work(request, job_id):
    job = get_object_or_404(JobPost, id=job_id, freelancer=request.user)

    if request.method == 'POST':
        submission_url = request.POST.get('submission_url', '').strip()
        try:
            EscrowService.submit_code_repository(job, request.user, submission_url)
            messages.success(request, "Project deliverable submitted to client for approval!")
        except ValidationError as e:
            messages.error(request, str(e))

    return redirect('freelancer_dashboard')

@login_required
def approve_and_payout(request, job_id):
    job = get_object_or_404(JobPost, id=job_id, client=request.user)
    try:
        EscrowService.complete_job_and_release_escrow(job, request.user)
        messages.success(request, f"Project approved! {job.budget} points disbursed to {job.freelancer.username}.")
    except ValidationError as e:
        messages.error(request, str(e))

    return redirect('client_dashboard')

@login_required
def freelancer_dashboard(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)
    my_applications = JobApplication.objects.filter(applicant=request.user).order_by('-applied_at')
    assigned_jobs = JobPost.objects.filter(freelancer=request.user).exclude(status='completed').order_by('-created_at')
    completed_projects = JobPost.objects.filter(freelancer=request.user, status='completed').order_by('-created_at')

    context = {
        'profile': profile,
        'profile_user': request.user,
        'applications': my_applications,
        'assigned_jobs': assigned_jobs,
        'completed_projects': completed_projects,
        'applications_sent_count': my_applications.count(),
        'active_jobs_count': assigned_jobs.count(),
    }
    return render(request, 'freelancer_dashboard.html', context)

@login_required
def client_dashboard(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)
    all_client_jobs = JobPost.objects.filter(client=request.user)

    posted_jobs = all_client_jobs.filter(status='open').order_by('-created_at')
    assigned_projects = all_client_jobs.exclude(status='open').order_by('-created_at')
    applications = JobApplication.objects.filter(job__client=request.user).select_related('job', 'applicant').order_by('-applied_at')

    context = {
        'profile': profile,
        'profile_user': request.user,
        'assigned_projects': assigned_projects,
        'posted_jobs': posted_jobs,
        'applications': applications,
        'total_posted_count': all_client_jobs.count(),
        'open_count': all_client_jobs.filter(status='open').count(),
        'progress_count': all_client_jobs.filter(status__in=['in_progress', 'submitted']).count(),
        'completed_count': all_client_jobs.filter(status='completed').count(),
    }
    return render(request, 'client_dashboard.html', context)

@login_required
def inbox_view(request):
    # Jobs where the user is either the client or the assigned freelancer, and a freelancer exists
    if request.user.is_client():
        jobs = JobPost.objects.filter(client=request.user, freelancer__isnull=False)
    else:
        jobs = JobPost.objects.filter(freelancer=request.user)

    threads = []
    for job in jobs:
        last_message = job.messages.last()
        other_user = job.freelancer if request.user.is_client() else job.client
        unread_count = job.messages.filter(is_read=False).exclude(sender=request.user).count()
        threads.append({
            'job': job,
            'other_user': other_user,
            'last_message': last_message,
            'unread_count': unread_count,
        })

    return render(request, 'inbox.html', {'threads': threads})


@login_required
def chat_thread_view(request, job_id):
    job = get_object_or_404(JobPost, id=job_id)

    # Only the client or the assigned freelancer on this job can access the chat
    if request.user != job.client and request.user != job.freelancer:
        messages.error(request, "You don't have access to this conversation.")
        return redirect('inbox')

    if request.method == 'POST':
        content = request.POST.get('content', '').strip()
        if content:
            Message.objects.create(job=job, sender=request.user, content=content)
        return redirect('chat_thread', job_id=job.id)

    # Mark messages from the other person as read
    job.messages.exclude(sender=request.user).update(is_read=True)

    other_user = job.freelancer if request.user == job.client else job.client
    thread_messages = job.messages.all()

    return render(request, 'chat_thread.html', {
        'job': job,
        'other_user': other_user,
        'thread_messages': thread_messages,
    })