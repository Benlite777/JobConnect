from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.http import Http404, HttpResponseRedirect, JsonResponse
from django.core.serializers import serialize
from django.views.decorators.cache import cache_page
from django.core.cache import cache

from account.models import User
from jobapp.forms import *
from jobapp.models import *
from jobapp.permission import *
from django.shortcuts import get_object_or_404, render
from django.contrib.auth.models import User
from .models import Applicant 

from django.http import HttpResponse

User = get_user_model()

def home_view(request):
    published_jobs = Job.objects.filter(is_published=True).order_by('-timestamp')
    jobs = published_jobs.filter(is_closed=False)
    total_candidates = User.objects.filter(role='employee').count()
    total_companies = User.objects.filter(role='employer').count()
    paginator = Paginator(jobs, 3)
    page_number = request.GET.get('page', None)
    page_obj = paginator.get_page(page_number)

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        job_lists = list(page_obj.object_list.values())

        next_page_number = None
        if page_obj.has_next():
            next_page_number = page_obj.next_page_number()

        prev_page_number = None
        if page_obj.has_previous():
            prev_page_number = page_obj.previous_page_number()

        data = {
            'job_lists': job_lists,
            'current_page_no': page_obj.number,
            'next_page_number': next_page_number,
            'no_of_page': paginator.num_pages,
            'prev_page_number': prev_page_number
        }
        return JsonResponse(data)

    context = {
        'total_candidates': total_candidates,
        'total_companies': total_companies,
        'total_jobs': len(jobs),
        'total_completed_jobs': len(published_jobs.filter(is_closed=True)),
        'page_obj': page_obj
    }
    return render(request, 'jobapp/index.html', context)

@cache_page(60 * 15)
def job_list_view(request):
    """
    Display a list of jobs.
    """

    job_list = Job.objects.filter(is_published=True, is_closed=False).order_by('-timestamp')
    paginator = Paginator(job_list, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
    }
    return render(request, 'jobapp/job-list.html', context)



@cache_page(60 * 15)
def job_list_view(request):
    """
    """

    job_list = Job.objects.filter(is_published=True, is_closed=False).order_by('-timestamp')
    paginator = Paginator(job_list, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {

        'page_obj': page_obj,

    }
    return render(request, 'jobapp/job-list.html', context)


@login_required(login_url=reverse_lazy('account:login'))
@user_is_employer
def create_job_view(request):
    """
    Provide the ability to create job post
    """
    form = JobForm(request.POST or None)

    user = get_object_or_404(User, id=request.user.id)
   

    if request.method == 'POST':

        if form.is_valid():

            instance = form.save(commit=False)
            instance.user = user
            instance.save()
            # for save tags
            form.save_m2m()
            messages.success(
                request, 'You are successfully posted your job! Please wait for review.')
            return redirect(reverse("jobapp:single-job", kwargs={
                'id': instance.id
            }))

    context = {
        'form': form,
     
    }
    return render(request, 'jobapp/post-job.html', context)


from django.shortcuts import get_object_or_404, render
from django.core.cache import cache
from django.core.paginator import Paginator
from .models import Job

def single_job_view(request, id):
    """
    Provide the ability to view job details
    """
    if cache.get(id):
        job = cache.get(id)
    else:
        job = get_object_or_404(Job, id=id)
        cache.set(id, job, 60 * 15)
    related_job_list = job.tags.similar_objects()

    paginator = Paginator(related_job_list, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'job': job,
        'page_obj': page_obj,
        'total': len(related_job_list)

    }
    return render(request, 'jobapp/job-single.html', context)



def search_result_view(request):
    """
        User can search job with multiple fields

    """

    job_list = Job.objects.order_by('-timestamp')

    # Keywords
    if 'job_title_or_company_name' in request.GET:
        job_title_or_company_name = request.GET['job_title_or_company_name']

        if job_title_or_company_name:
            job_list = job_list.filter(title__icontains=job_title_or_company_name) | job_list.filter(
                company_name__icontains=job_title_or_company_name)

    # location
    if 'location' in request.GET:
        location = request.GET['location']
        if location:
            job_list = job_list.filter(location__icontains=location)

    # Job Type
    if 'job_type' in request.GET:
        job_type = request.GET['job_type']
        if job_type:
            job_list = job_list.filter(job_type__iexact=job_type)

    paginator = Paginator(job_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {

        'page_obj': page_obj,

    }
    return render(request, 'jobapp/result.html', context)


@login_required(login_url=reverse_lazy('account:login'))
@user_is_employee
def apply_job_view(request, id):
    # Fetch the job object
    job = get_object_or_404(Job, id=id)

    # Check if the user has already applied for this job
    if Applicant.objects.filter(user=request.user, job=job).exists():
        messages.error(request, 'You have already applied for this job!')
        return redirect(reverse("jobapp:single-job", kwargs={'id': id}))

    if request.method == 'POST':
        form = JobApplyForm(request.POST, request.FILES)
        if form.is_valid():
            # Save the form data
            applicant = form.save(commit=False)
            applicant.user = request.user
            applicant.job = job
            applicant.save()

            messages.success(request, 'You have successfully applied for this job!')
            return redirect(reverse("jobapp:single-job", kwargs={'id': id}))
    else:
        form = JobApplyForm()

    return render(request, 'jobapp/apply_job.html', {'form': form, 'job': job})


@login_required(login_url=reverse_lazy('account:login'))
def dashboard_view(request):
    """
    """
    jobs = []
    savedjobs = []
    appliedjobs = []
    total_applicants = {}
    if request.user.role == 'employer':

        jobs = Job.objects.filter(user=request.user.id)
        for job in jobs:
            count = Applicant.objects.filter(job=job.id).count()
            total_applicants[job.id] = count

    if request.user.role == 'employee':
        savedjobs = BookmarkJob.objects.filter(user=request.user.id)
        appliedjobs = Applicant.objects.filter(user=request.user.id)
    context = {

        'jobs': jobs,
        'savedjobs': savedjobs,
        'appliedjobs': appliedjobs,
        'total_applicants': total_applicants
    }

    return render(request, 'jobapp/dashboard.html', context)


@login_required(login_url=reverse_lazy('account:login'))
@user_is_employer
def delete_job_view(request, id):

    job = get_object_or_404(Job, id=id, user=request.user.id)

    if job:

        job.delete()
        messages.success(request, 'Your Job Post was successfully deleted!')

    return redirect('jobapp:dashboard')


@login_required(login_url=reverse_lazy('account:login'))
@user_is_employer
def make_complete_job_view(request, id):
    job = get_object_or_404(Job, id=id, user=request.user.id)

    if job:
        try:
            job.is_closed = True
            job.save()
            messages.success(request, 'Your Job was marked closed!')
        except:
            messages.success(request, 'Something went wrong !')

    return redirect('jobapp:dashboard')


@login_required(login_url=reverse_lazy('account:login'))
@user_is_employer
def all_applicants_view(request, id):

    all_applicants = Applicant.objects.filter(job=id)

    context = {

        'all_applicants': all_applicants
    }

    return render(request, 'jobapp/all-applicants.html', context)


@login_required(login_url=reverse_lazy('account:login'))
@user_is_employee
def delete_bookmark_view(request, id):

    job = get_object_or_404(BookmarkJob, id=id, user=request.user.id)

    if job:

        job.delete()
        messages.success(request, 'Saved Job was successfully deleted!')

    return redirect('jobapp:dashboard')


@login_required(login_url=reverse_lazy('account:login'))
@user_is_employer

def applicant_details_view(request, id):

    applicant = get_object_or_404(User, id=id)

    context = {

        'applicant': applicant
    }

    return render(request, 'jobapp/applicant-details.html', context)



@login_required(login_url=reverse_lazy('account:login'))
@user_is_employee
def job_bookmark_view(request, id):

    form = JobBookmarkForm(request.POST or None)

    user = get_object_or_404(User, id=request.user.id)
    applicant = BookmarkJob.objects.filter(user=request.user.id, job=id)

    if not applicant:
        if request.method == 'POST':

            if form.is_valid():
                instance = form.save(commit=False)
                instance.user = user
                instance.save()

                messages.success(
                    request, 'You have successfully save this job!')
                return redirect(reverse("jobapp:single-job", kwargs={
                    'id': id
                }))

        else:
            return redirect(reverse("jobapp:single-job", kwargs={
                'id': id
            }))

    else:
        messages.error(request, 'You already saved this Job!')

        return redirect(reverse("jobapp:single-job", kwargs={
            'id': id
        }))


@login_required(login_url=reverse_lazy('account:login'))
@user_is_employer
def job_edit_view(request, id):
    """
    Handle Job Update
    """

    job = get_object_or_404(Job, id=id, user=request.user.id)
    categories = Category.objects.all()
    form = JobEditForm(request.POST or None, instance=job)
    if form.is_valid():
        instance = form.save(commit=False)
        instance.save()
        messages.success(request, 'Your Job Post Was Successfully Updated!')
        return redirect(reverse("jobapp:single-job", kwargs={'id': instance.id}))
    context = {

        'form': form,
        'categories': categories
    }

    return render(request, 'jobapp/job-edit.html', context)

def about(request):
    return render(request, 'about.html')





from django.shortcuts import render

@login_required
def salary_insights(request):
    if request.method == 'POST':
        industry = request.POST.get('industry')
        location = request.POST.get('location')
        experience_level = request.POST.get('experience_level')

        # Updated salary ranges for different industries from 2021 to 2024 (realistic for India)
        salary_ranges = {
            'Tech': {
                '2021': {
                    'Entry Level': (400000, 600000),
                    'Mid Level': (700000, 900000),
                    'Senior Level': (1000000, 1200000)
                },
                '2022': {
                    'Entry Level': (450000, 650000),
                    'Mid Level': (750000, 950000),
                    'Senior Level': (1050000, 1250000)
                },
                '2023': {
                    'Entry Level': (500000, 700000),
                    'Mid Level': (800000, 1000000),
                    'Senior Level': (1100000, 1300000)
                },
                '2024': {
                    'Entry Level': (550000, 750000),
                    'Mid Level': (850000, 1050000),
                    'Senior Level': (1150000, 1350000)
                }
            },
            'Finance': {
                '2021': {
                    'Entry Level': (350000, 550000),
                    'Mid Level': (600000, 750000),
                    'Senior Level': (850000, 1000000)
                },
                '2022': {
                    'Entry Level': (400000, 600000),
                    'Mid Level': (650000, 800000),
                    'Senior Level': (900000, 1050000)
                },
                '2023': {
                    'Entry Level': (450000, 650000),
                    'Mid Level': (700000, 850000),
                    'Senior Level': (950000, 1100000)
                },
                '2024': {
                    'Entry Level': (500000, 700000),
                    'Mid Level': (750000, 900000),
                    'Senior Level': (1000000, 1150000)
                }
            },
            'Healthcare': {
                '2021': {
                    'Entry Level': (300000, 500000),
                    'Mid Level': (550000, 700000),
                    'Senior Level': (750000, 900000)
                },
                '2022': {
                    'Entry Level': (350000, 550000),
                    'Mid Level': (600000, 750000),
                    'Senior Level': (800000, 950000)
                },
                '2023': {
                    'Entry Level': (400000, 600000),
                    'Mid Level': (650000, 800000),
                    'Senior Level': (850000, 1000000)
                },
                '2024': {
                    'Entry Level': (450000, 650000),
                    'Mid Level': (700000, 850000),
                    'Senior Level': (900000, 1050000)
                }
            },
            'Marketing': {
                '2021': {
                    'Entry Level': (250000, 450000),
                    'Mid Level': (500000, 650000),
                    'Senior Level': (700000, 850000)
                },
                '2022': {
                    'Entry Level': (300000, 500000),
                    'Mid Level': (550000, 700000),
                    'Senior Level': (750000, 900000)
                },
                '2023': {
                    'Entry Level': (350000, 550000),
                    'Mid Level': (600000, 750000),
                    'Senior Level': (800000, 950000)
                },
                '2024': {
                    'Entry Level': (400000, 600000),
                    'Mid Level': (650000, 800000),
                    'Senior Level': (850000, 1000000)
                }
            },
            'Education': {
                '2021': {
                    'Entry Level': (200000, 400000),
                    'Mid Level': (450000, 600000),
                    'Senior Level': (650000, 800000)
                },
                '2022': {
                    'Entry Level': (250000, 450000),
                    'Mid Level': (500000, 650000),
                    'Senior Level': (700000, 850000)
                },
                '2023': {
                    'Entry Level': (300000, 500000),
                    'Mid Level': (550000, 700000),
                    'Senior Level': (750000, 900000)
                },
                '2024': {
                    'Entry Level': (350000, 550000),
                    'Mid Level': (600000, 750000),
                    'Senior Level': (800000, 950000)
                }
            }
        }

        year_data = {
            '2021': salary_ranges[industry]['2021'][experience_level][0],
            '2022': salary_ranges[industry]['2022'][experience_level][0],
            '2023': salary_ranges[industry]['2023'][experience_level][0],
            '2024': salary_ranges[industry]['2024'][experience_level][0]
        }

        previous_year_min = salary_ranges[industry]['2021'][experience_level][0]
        previous_year_max = salary_ranges[industry]['2021'][experience_level][1]

        context = {
            'industry': industry,
            'location': location,
            'experience_level': experience_level,
            'salary_min': salary_ranges[industry]['2024'][experience_level][0],
            'salary_max': salary_ranges[industry]['2024'][experience_level][1],
            'previous_year_min': previous_year_min,
            'previous_year_max': previous_year_max,
            'year_data': year_data
        }

        return render(request, 'jobapp/insights.html', context)
    else:
        return render(request, 'jobapp/insights_form.html')






def salary_negotiation_tips(request):
    # Dummy data for negotiation tips
    tips = [
        "Research salary ranges for your position and location.",
        "Highlight your achievements and skills during negotiations.",
        "Be prepared to discuss benefits and perks as part of your negotiation.",
        "Consider timing and approach when negotiating salary.",
    ]
    
    context = {
        'tips': tips
    }
    
    return render(request, 'jobapp/negotiation_tips.html', context)



# views.py
from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse
from django.conf import settings
import os

from .models import Applicant

@login_required
def download_resume(request, applicant_id):
    applicant = get_object_or_404(Applicant, id=applicant_id)
    
    # Perform some logic to download the resume
    # For demonstration purposes, assume we're returning a direct download response
    response = HttpResponse(applicant.resume, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{applicant.resume.name}"'
    
    # Update the status to "Resume Downloaded"
    applicant.status = "Resume Downloaded"
    applicant.save()
    
    return response
    
from django.shortcuts import render, get_object_or_404, redirect
from .models import Job, Applicant, BookmarkJob
from django.contrib.auth.decorators import login_required

@login_required
def dashboard(request):
    if request.user.role == 'employer':
        jobs = Job.objects.filter(user=request.user)
        applicants = Applicant.objects.filter(job__in=jobs)
        return render(request, 'dashboard.html', {'jobs': jobs, 'applicants': applicants})
    elif request.user.role == 'employee':
        savedjobs = BookmarkJob.objects.filter(user=request.user)
        appliedjobs = Applicant.objects.filter(user=request.user)
        return render(request, 'dashboard.html', {'savedjobs': savedjobs, 'appliedjobs': appliedjobs})
    else:
        return redirect('jobapp:home')

@login_required
def apply_for_job(request, job_id):
    job = get_object_or_404(Job, id=job_id)
    if request.method == 'POST':
        form = ApplicationForm(request.POST, request.FILES)
        if form.is_valid():
            application = form.save(commit=False)
            application.user = request.user
            application.job = job
            application.save()
            return redirect('application_status')
    else:
        form = ApplicationForm()
    return render(request, 'apply_for_job.html', {'form': form, 'job': job})

@login_required
def application_status(request):
    applications = Applicant.objects.filter(user=request.user)
    return render(request, 'application_status.html', {'applications': applications})


def job_detail(request, job_id):
    job = get_object_or_404(Job, id=job_id)
    applicants = Applicant.objects.filter(job=job)
    context = {
        'job': job,
        'applicants': applicants,
    }
    return render(request, 'jobapp/job_detail.html', context)

def select_applicant(request, applicant_id):
    applicant = get_object_or_404(Applicant, id=applicant_id)
    applicant.status = 'selected'
    applicant.save()
    # Optionally, add a success message or redirect to job detail page
    return redirect('jobapp:job-detail', job_id=applicant.job.id)

def reject_applicant(request, applicant_id):
    applicant = get_object_or_404(Applicant, id=applicant_id)
    applicant.status = 'not_selected'
    applicant.save()
    # Optionally, add a success message or redirect to job detail page
    return redirect('jobapp:job-detail', job_id=applicant.job.id)

def job_detail(request, job_id):
    job = get_object_or_404(Job, id=job_id)
    applicants = Applicant.objects.filter(job=job)

    if request.method == 'POST':
        applicant_id = request.POST.get('applicant_id')
        action = request.POST.get('action')

        if action == 'select':
            applicant = get_object_or_404(Applicant, id=applicant_id)
            applicant.status = 'selected'
            applicant.save()
            messages.success(request, f'{applicant.user.username} has been selected.')
            return redirect('jobapp:job-detail', job_id=job.id)

        elif action == 'reject':
            applicant = get_object_or_404(Applicant, id=applicant_id)
            applicant.status = 'not_selected'
            applicant.save()
            messages.success(request, f'{applicant.user.username} has been rejected.')
            return redirect('jobapp:job-detail', job_id=job.id)

    context = {
        'job': job,
        'applicants': applicants,
    }
    return render(request, 'jobapp/job_detail.html', context)
def resume_feedback(request):
    feedback = None
    if request.method == 'POST':
        form = ResumeUploadForm(request.POST, request.FILES)
        if form.is_valid():
            resume = form.save()
            feedback = generate_feedback(resume.resume_file)
    else:
        form = ResumeUploadForm()
    return render(request, 'resume_feedback.html', {'form': form, 'feedback': feedback})

def generate_feedback(resume_file):
    # Implement your feedback generation logic here
    return "This is a placeholder for resume quality feedback."
