from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseForbidden
from .models import Application, SeekerProfile, Job, Project
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.models import User, Group
from django.utils import timezone
from datetime import timedelta
import os
import json
from django.conf import settings
from django.core.files.base import ContentFile
import uuid

def admin_panel(request):
    if not request.user.is_authenticated:
        return redirect('login_recruiter')

    error = None
    success = None

    if request.method == 'POST':
        title = request.POST.get('title')
        company = request.POST.get('company')
        location = request.POST.get('location')
        experience = request.POST.get('experience')
        expiry_days = request.POST.get('expiry_days')

        if not title or not company:
            error = "Job title and company are required."
        else:
            try:
                expiry_days_int = int(expiry_days)
            except (TypeError, ValueError):
                expiry_days_int = 30

            Job.objects.create(
                recruiter=request.user,
                title=title,
                company=company,
                location=location,
                experience=experience,
                expiry_days=expiry_days_int
            )
            success = "Job posted successfully."

    return render(request, 'admin_panel.html', {'error': error, 'success': success})

def index(request):
    full_name = None
    photo_url = None
    now = timezone.now()
    all_jobs = Job.objects.all().order_by('-created_at')
    jobs = [job for job in all_jobs if job.created_at + timedelta(days=job.expiry_days) >= now]
    if request.user.is_authenticated:
        try:
            profile = SeekerProfile.objects.get(user=request.user)
            full_name = profile.full_name
            if profile.photo:
                photo_url = profile.photo.url
        except SeekerProfile.DoesNotExist:
            pass
    return render(request, 'index.html', {'full_name': full_name, 'photo_url': photo_url, 'jobs': jobs})

from django.http import JsonResponse
from django.views.decorators.http import require_GET
from django.db.models import Q

@require_GET
def search_jobs(request):
    query = request.GET.get('q', '').strip()
    now = timezone.now()
    if query:
        filtered_jobs = Job.objects.filter(
            Q(title__icontains=query) | Q(company__icontains=query),
            created_at__lte=now,
            created_at__gte=now - timedelta(days=365*10)  # Assuming jobs not older than 10 years
        ).order_by('-created_at')
        jobs = [job for job in filtered_jobs if job.created_at + timedelta(days=job.expiry_days) >= now]
    else:
        all_jobs = Job.objects.all().order_by('-created_at')
        jobs = [job for job in all_jobs if job.created_at + timedelta(days=job.expiry_days) >= now]

    results = []
    for job in jobs:
        results.append({
            'id': job.id,
            'title': job.title,
            'company': job.company,
            'location': job.location,
            'experience': job.experience,
        })
    return JsonResponse({'results': results})

def profile_edit(request):
    if not request.user.is_authenticated:
        return redirect('login')
    try:
        profile = SeekerProfile.objects.get(user=request.user)
    except SeekerProfile.DoesNotExist:
        profile = None

    if request.method == 'POST':
        full_name = request.POST.get('full_name')
        course = request.POST.get('course')
        graduation = request.POST.get('graduation')
        skills = request.POST.get('skills')
        contact_info = request.POST.get('contact_info')
        address = request.POST.get('address')
        photo = request.FILES.get('photo')
        resume = request.FILES.get('resume')

        if profile is None:
            profile = SeekerProfile(user=request.user)

        profile.full_name = full_name
        profile.course = course
        profile.graduation = graduation
        profile.skills = skills
        profile.contact_info = contact_info
        profile.address = address

        if photo:
            ext = os.path.splitext(photo.name)[1]
            unique_name = f"{uuid.uuid4().hex}{ext}"
            profile.photo.save(unique_name, ContentFile(photo.read()), save=False)
        if resume:
            ext = os.path.splitext(resume.name)[1]
            unique_name = f"{uuid.uuid4().hex}{ext}"
            profile.resume.save(unique_name, ContentFile(resume.read()), save=False)

        profile.save()
        messages.success(request, "Profile updated successfully.")
        resume_exists = False
        if profile and profile.resume:
            if profile.resume.storage.exists(profile.resume.name):
                resume_exists = True
        return render(request, 'profile_edit.html', {'profile': profile, 'resume_exists': resume_exists})

    resume_exists = False
    if profile and profile.resume:
        if profile.resume.storage.exists(profile.resume.name):
            resume_exists = True
    return render(request, 'profile_edit.html', {'profile': profile, 'resume_exists': resume_exists})

def profile_view(request):
    return render(request, 'profile_view.html')

def logout(request):
    auth_logout(request)
    storage = messages.get_messages(request)
    for _ in storage:
        pass  # iterate to clear messages

def logout(request):
    auth_logout(request)
    storage = messages.get_messages(request)
    for _ in storage:
        pass  # iterate to clear messages
    return redirect('index')

from django.utils import timezone
from datetime import timedelta

def index(request):
    full_name = None
    photo_url = None
    now = timezone.now()
    all_jobs = Job.objects.all().order_by('-created_at')
    jobs = [job for job in all_jobs if job.created_at + timedelta(days=job.expiry_days) >= now]
    if request.user.is_authenticated:
        try:
            profile = SeekerProfile.objects.get(user=request.user)
            full_name = profile.full_name
            if profile.photo:
                photo_url = profile.photo.url
        except SeekerProfile.DoesNotExist:
            pass
    return render(request, 'index.html', {'full_name': full_name, 'photo_url': photo_url, 'jobs': jobs})

from django.contrib.auth.models import User, Group
from django.contrib.auth import authenticate, login as auth_login
from django.contrib import messages
from django.shortcuts import render, redirect

def signup_seeker(request):
    if request.method == 'POST':
        full_name = request.POST.get('full_name')
        course = request.POST.get('course')
        graduation = request.POST.get('graduation')
        skills = request.POST.get('skills')
        contact_info = request.POST.get('contact_info')
        address = request.POST.get('address')
        photo = request.FILES.get('photo')
        resume = request.FILES.get('resume')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password_confirm = request.POST.get('password_confirm')

        if password != password_confirm:
            messages.error(request, "Passwords do not match.")
            return render(request, 'signup_page_sekkers.html')

        if User.objects.filter(username=email).exists():
            messages.error(request, "Email is already registered.")
            return render(request, 'signup_page_sekkers.html')

        user = User.objects.create_user(username=email, email=email, password=password)
        seeker_profile = SeekerProfile.objects.create(
            user=user,
            full_name=full_name,
            course=course,
            graduation=graduation,
            skills=skills,
            contact_info=contact_info,
            address=address,
            photo=photo,
            resume=resume
        )
        messages.success(request, "Signup successful. Please login.")
        return redirect('login')
    else:
        return render(request, 'signup_page_sekkers.html')

def login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(request, username=email, password=password)
        if user is not None:
            auth_login(request, user)
            return redirect('index')
        else:
            messages.error(request, "Invalid email or password.")
            return render(request, 'login_page.html')
    else:
        return render(request, 'login_page.html')

def signup_recruiter(request):
    return render(request, 'signup_page_recruiter.html')

def candidate_login(request):
    return render(request, 'login_page.html')

def candidate_signup(request):
    return render(request, 'signup_page_sekkers.html')

def new_login_recruiter(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        recuiter_user = authenticate(request, username=email, password=password)
        if recuiter_user is not None:
            auth_login(request, recuiter_user)
            return redirect('recuiter_dashboard')
        else:
            messages.error(request, "Invalid email or password.")
            return render(request, 'login_recruiter.html')
    else:
        return render(request, 'login_recruiter.html')

import json
import os
from django.conf import settings

import logging

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(levelname)s %(message)s')

def new_signup_recruiter(request):
    if request.method == 'POST':
        recuiter_email = request.POST.get('recuiter_email').lower()
        recuiter_password = request.POST.get('recuiter_password')
        recuiter_password_confirm = request.POST.get('recuiter_password_confirm')
        recuiter_company_name = request.POST.get('recuiter_company_name')
        recuiter_contact_info= request.POST.get('recuiter_contact_info')
        recuiter_Location = request.POST.get('recuiter_Location')
        recuiter_Address = request.POST.get('recuiter_Address')

        if recuiter_password != recuiter_password_confirm:
            messages.error(request, "Passwords do not match.")
            return render(request, 'signup_page_recruiter.html')

        if User.objects.filter(username=recuiter_email).exists():
            messages.error(request, "Email is already registered.")
            return render(request, 'signup_page_recruiter.html')

        user = User.objects.create_user(username=recuiter_email, email=recuiter_email, password=recuiter_password)
        user.save()

        try:
            recruiters_group = Group.objects.get(name='Recruiters')
        except Group.DoesNotExist:
            recruiters_group = Group.objects.create(name='Recruiters')
        user.groups.add(recruiters_group)

        json_dir = os.path.join(settings.BASE_DIR, 'media')
        json_file_path = os.path.join(json_dir, 'recruiters.json')

        logging.debug(f"New Recruiter signup: JSON file path: {json_file_path}")

        if not os.path.exists(json_dir):
            try:
                os.makedirs(json_dir)
                logging.debug(f"Created media directory at {json_dir}")
            except Exception as e:
                logging.error(f"Failed to create media directory: {e}")
                messages.error(request, "Internal server error. Please try again later.")
                return render(request, 'signup_page_recruiter.html')

        if os.path.exists(json_file_path):
            with open(json_file_path, 'r') as f:
                try:
                    recruiters = json.load(f)
                    logging.debug(f"Loaded existing recruiters data: {len(recruiters)} entries")
                except json.JSONDecodeError:
                    logging.warning("Recruiters JSON file is empty or corrupted, starting fresh")
                    recruiters = []
        else:
            recruiters = []
            logging.debug("Recruiters JSON file does not exist, starting fresh")

        new_recruiter = {
            'recuiter_email': recuiter_email,
            'recuiter_password': recuiter_password,
            'recuiter_company_name': recuiter_company_name,
            'recuiter_contact_info': recuiter_contact_info,
            'recuiter_Location': recuiter_Location,
            'recuiter_Address': recuiter_Address
        }
        recruiters.append(new_recruiter)

        try:
            with open(json_file_path, 'w') as f:
                json.dump(recruiters, f, indent=4)
            logging.debug("Successfully wrote recruiters.json")
        except Exception as e:
            logging.error(f"Failed to write recruiters.json: {e}")
            messages.error(request, "Internal server error. Please try again later.")
            return render(request, 'signup_page_recruiter.html')

        messages.success(request, "Successfully registered.")
        return redirect('login_recruiter')
    else:
        return render(request, 'signup_page_recruiter.html')

from django.db.models import Count

@login_required(login_url='login_recruiter')
def recuiter_dashboard(request):
    jobs = Job.objects.filter(recruiter=request.user).order_by('-created_at')
    job_data = []
    for job in jobs:
        applications = Application.objects.filter(job=job).select_related('candidate__user')
        applications_count = applications.count()
        application_details = []
        for app in applications:
            candidate = app.candidate
            user = candidate.user
            application_details.append({
                'candidate_name': candidate.full_name,
                'candidate_contact': candidate.contact_info,
                'candidate_email': user.email,
                'applied_at': app.applied_at,
            })
        job_data.append({
            'job': job,
            'applications_count': applications_count,
            'applications': application_details,
        })
    return render(request, 'recruiter_dashboard.html', {'job_data': job_data})

def job_analysis(request):
    return render(request, 'job_analysis.html')

from django.utils import timezone
from datetime import timedelta

from django.http import HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404

from django.shortcuts import render, get_object_or_404

def job_listings(request):
    now = timezone.now()
    all_jobs = Job.objects.all().order_by('-created_at')
    jobs = [job for job in all_jobs if job.created_at + timedelta(days=job.expiry_days) >= now]
    return render(request, 'job_listings.html', {'jobs': jobs})

def description_about_job(request, job_id):
    job = get_object_or_404(Job, id=job_id)
    return render(request, 'description_about_job.html', {'job': job})

@login_required(login_url='login_recruiter')
def delete_job(request, job_id):
    job = get_object_or_404(Job, id=job_id)
    if job.recruiter != request.user:
        return HttpResponseForbidden("You are not allowed to delete this job.")
    if request.method == 'POST':
        job.delete()
        messages.success(request, "Job deleted successfully.")
        return redirect('admin_panel')
    return render(request, 'confirm_delete.html', {'job': job})

def candidates(request):
    # Placeholder view for candidates
    return render(request, 'candidates.html')

def settings_view(request):
    # Placeholder view for settings
    return render(request, 'settings.html')

@login_required(login_url='login')
def candidates_project_dashboard(request):
    full_name = None
    projects = []
    if request.user.is_authenticated:
        try:
            profile = SeekerProfile.objects.get(user=request.user)
            full_name = profile.full_name
            projects = Project.objects.filter(candidate=request.user).order_by('-created_at')
        except SeekerProfile.DoesNotExist:
            pass
    return render(request, 'candidates_project_dashboard.html', {'full_name': full_name, 'projects': projects})

import json
import os
from django.conf import settings
from django.contrib import messages

@login_required(login_url='login')
def candidates_projects(request):
    if request.method == 'POST':
        title = request.POST.get('project_title')
        description = request.POST.get('description')
        image = request.FILES.get('image_upload')
        github_link = request.POST.get('github_link')

        if not title or not description or not github_link or not image:
            error = 'All fields are required.'
            return render(request, 'candidates_project.html', {'error': error})

        project = Project(
            candidate=request.user,
            title=title,
            description=description,
            image=image,
            video_link=github_link
        )
        project.save()
        messages.success(request, 'Project posted successfully.')
        return render(request, 'candidates_project.html', {'success': 'Project posted successfully.'})
    else:
        return render(request, 'candidates_project.html')


@login_required(login_url='login')
def candidates_project_dashboard(request):
    full_name = None
    projects = []
    if request.user.is_authenticated:
        try:
            profile = SeekerProfile.objects.get(user=request.user)
            full_name = profile.full_name
            projects = Project.objects.filter(candidate=request.user).order_by('-created_at')
        except SeekerProfile.DoesNotExist:
            pass
    return render(request, 'candidates_project_dashboard.html', {'full_name': full_name, 'projects': projects})

def company(request):
    return render(request, 'company.html')

def support(request):
    return render(request, 'support.html')

def Legal(request):
    return render(request, 'Legal_page.html')

from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.contrib import messages

def help_centre(request):
    return render(request, 'help_centre.html')

def open_roles(request):
    return render(request, 'open_roles.html')

def press(request):
    return render(request, 'press.html')

def blog(request):
    return render(request, 'blog.html')

def candidates_projects(request):
    return render(request, 'candidates_project.html')

from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import redirect, render, get_object_or_404
from .models import Application, SeekerProfile

@login_required(login_url='login')
def application(request):
    try:
        candidate = SeekerProfile.objects.get(user=request.user)
    except SeekerProfile.DoesNotExist:
        messages.error(request, "Candidate profile not found. Please complete your profile.")
        return redirect('index')

    applications = Application.objects.filter(candidate=candidate).select_related('job').order_by('-applied_at')

    return render(request, 'application.html', {'applications': applications})

def five_ways(request):
    return render(request, 'five_ways.html')

def behind_the_scenes(request):
    return render(request, 'behind_the_scenes.html')


def help_centre(request):
    return render(request, 'help_centre.html')


def articles(request):
    return render(request, 'articles.html')

def Terms_of_service(request):
    return render(request, 'Terms_of_service.html')


def Privacy_policy(request):
    return render(request, 'Privacy_policy.html')

def Trust_Safety(request):
    return render(request, 'Trust_Safety.html')

def License_Agreement(request):
    return render(request, 'License_Agreement.html')

import json
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.conf import settings
import pandas as pd
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from nltk.tokenize import word_tokenize
import os
import datetime
import PyPDF2
import docx
import threading

chat_history_lock = threading.Lock()
chat_history_ids = None
last_parsed_resume_text = ""

# Load DialoGPT model and tokenizer once
model_name = "microsoft/DialoGPT-medium"
tokenizer = AutoTokenizer.from_pretrained(model_name, padding_side='left')
model = AutoModelForCausalLM.from_pretrained(model_name)

# Load dataset
from pathlib import Path

dataset_path = os.path.join(str(settings.MEDIA_ROOT), 'datasets', 'kaggle_jobs.csv')
import logging

if os.path.exists(dataset_path):
    logging.info(f"Loading dataset from {dataset_path}")
    kaggle_df = pd.read_csv(dataset_path)
    logging.info(f"Dataset loaded with {len(kaggle_df)} rows")
else:
    logging.warning(f"Dataset file not found at {dataset_path}")
    kaggle_df = pd.DataFrame(columns=["Job Title", "Company", "Skills", "Location", "Job Type", "Salary", "Experience", "Company Size"])

def extract_text_from_pdf(file_obj):
    reader = PyPDF2.PdfReader(file_obj)
    return "".join(page.extract_text() for page in reader.pages if page.extract_text())

def extract_text_from_docx(file_obj):
    doc = docx.Document(file_obj)
    return "\n".join(para.text for para in doc.paragraphs if para.text.strip())

def extract_keywords(text):
    words = word_tokenize(text.lower())
    tech_skills = ["python", "java", "c++", "sql", "javascript", "react", "node", "ml", "ai", "aws"]
    common_titles = ["developer", "engineer", "designer", "manager", "analyst"]
    return list(set(word for word in words if word in tech_skills or word in common_titles))

def find_jobs_from_dataset(keywords, location=None, job_type=None, min_salary=0, experience=None, company_size=None):
    if kaggle_df.empty:
        return ["❌ Job dataset not found or is empty."]
    filtered = kaggle_df.copy()

    if location:
        filtered = filtered[filtered["Location"].str.lower().str.contains(location.lower(), na=False)]
    if job_type:
        filtered = filtered[filtered["Job Type"].str.lower().str.contains(job_type.lower(), na=False)]
    if experience:
        filtered = filtered[filtered["Experience"].str.lower().str.contains(experience.lower(), na=False)]
    if company_size:
        filtered = filtered[filtered["Company Size"].str.lower().str.contains(company_size.lower(), na=False)]
    if min_salary:
        try:
            filtered["Salary"] = filtered["Salary"].astype(str).str.replace(",", "").str.extract('(\d+)').fillna(0).astype(int)
            filtered = filtered[filtered["Salary"] >= int(min_salary)]
        except Exception:
            pass

    matches = []
    for _, row in filtered.iterrows():
        skills = str(row.get('Skills', '')).lower()
        if any(skill in skills for skill in keywords):
            matches.append(f"🔹 {row.get('Job Title', 'Unknown')} at {row.get('Company', 'Unknown')} ({row.get('Location', 'Unknown')}, {row.get('Job Type', 'Unknown')}, ₹{row.get('Salary', 'N/A')}/yr)")
        if len(matches) >= 5:
            break
    return matches or ["❌ No matching jobs found."]

def parse_user_filters(text):
    words = text.lower().split()
    location = job_type = experience = company_size = None
    salary = "0"
    if "Location" in kaggle_df.columns:
        location = next((w for w in words if any(w in str(loc).lower() for loc in kaggle_df["Location"].dropna())), None)
    if "Job Type" in kaggle_df.columns:
        job_type = next((w for w in words if any(w in str(jt).lower() for jt in kaggle_df["Job Type"].dropna())), None)
    if "Experience" in kaggle_df.columns:
        experience = next((w for w in words if any(w in str(e).lower() for e in kaggle_df["Experience"].dropna())), None)
    if "Company Size" in kaggle_df.columns:
        company_size = next((w for w in words if any(w in str(cs).lower() for cs in kaggle_df["Company Size"].dropna())), None)
    salary = next((w for w in words if w.isdigit()), "0")
    return location, job_type, salary, experience, company_size

@csrf_exempt
def chatbot_api(request):
    global chat_history_ids, last_parsed_resume_text

    def handle_input(user_input):
        user_input_lower = user_input.lower()

        if "how do i improve my resume" in user_input_lower or "resume tips" in user_input_lower:
            return "📄 Here are some resume tips: Keep it clear, concise, showcase achievements, use strong action words, and tailor it to each job!"
        if "tips for interviews" in user_input_lower or "interview tips" in user_input_lower:
            return "💬 Interview Tips: Research the company, practice common questions, dress professionally, and stay confident yet humble."
        if "who developed you" in user_input_lower or "where were you developed" in user_input_lower:
            return "🤖 I Was Developed By The Team At HireSense! MY PEOPLE :) "
        if "how to improve my skills" in user_input_lower or "suggest skills" in user_input_lower:
            return "🔧 To boost your career, consider learning: cloud computing, kubernetes, generative ai, devops, and more."

        if "resume" in user_input_lower and last_parsed_resume_text:
            return f"✅ Resume parsed! Keywords: {', '.join(extract_keywords(last_parsed_resume_text))}\n{suggest_skills(extract_keywords(last_parsed_resume_text))}"
        return None

    def suggest_skills(keywords):
        future_skills = ["cloud computing", "devops", "kubernetes", "docker", "blockchain", "cybersecurity", "llms", "generative ai"]
        missing = [skill for skill in future_skills if skill not in keywords]
        return f"💡 To improve your chances, consider learning: {', '.join(missing)}" if missing else "🚀 Great skillset! You're job-market ready."

    if request.method == 'POST':
        if request.content_type == 'application/json':
            data = json.loads(request.body)
            user_input = data.get('message', '')
        else:
            # Handle file upload
            resume_file = request.FILES.get('resume')
            if resume_file:
                if resume_file.name.endswith('.pdf'):
                    import io
                    file_bytes = resume_file.read()
                    text = extract_text_from_pdf(io.BytesIO(file_bytes))
                elif resume_file.name.endswith('.docx'):
                    import io
                    file_bytes = resume_file.read()
                    text = extract_text_from_docx(io.BytesIO(file_bytes))
                else:
                    return JsonResponse({'response': 'Unsupported file format.'})
                last_parsed_resume_text = text
                keywords = extract_keywords(text)
                response_text = f"✅ Resume uploaded successfully! Keywords found: {', '.join(keywords)}"
                return JsonResponse({'response': response_text})
            else:
                return JsonResponse({'response': 'No resume file uploaded.'})

        if not user_input.strip():
            return JsonResponse({'response': 'Please enter a message.'})

        # Simple keyword-based job suggestion
        if "suggest job" in user_input.lower() or "job" in user_input.lower():
            if not last_parsed_resume_text:
                return JsonResponse({'response': 'Please upload your resume first.'})
            keywords = extract_keywords(last_parsed_resume_text)
            location, job_type, salary, experience, company_size = parse_user_filters(user_input)
            jobs = find_jobs_from_dataset(keywords, location, job_type, salary, experience, company_size)
            response_text = "🔍 Jobs for you:\n" + "\n".join(jobs)
            return JsonResponse({'response': response_text})

        # Handle specific queries with predefined responses
        response_text = handle_input(user_input)
        if response_text:
            return JsonResponse({'response': response_text})

        # Default DialoGPT response
        input_ids = tokenizer.encode(user_input + tokenizer.eos_token, return_tensors='pt')
        with chat_history_lock:
            bot_input_ids = torch.cat([chat_history_ids, input_ids], dim=-1) if chat_history_ids is not None else input_ids
            chat_history_ids = model.generate(bot_input_ids, max_length=500, pad_token_id=tokenizer.eos_token_id)
        response_text = tokenizer.decode(chat_history_ids[:, input_ids.shape[-1]:][0], skip_special_tokens=True)
        return JsonResponse({'response': response_text})

def settings_view(request):
    # Placeholder view for settings page
    return render(request, 'settings.html')

from django.http import JsonResponse

def dataset_info(request):
    if kaggle_df.empty:
        return JsonResponse({'status': 'empty', 'rows': 0, 'columns': 0})
    else:
        sample = kaggle_df.head(5).to_dict(orient='records')
        return JsonResponse({'status': 'loaded', 'rows': len(kaggle_df), 'columns': len(kaggle_df.columns), 'sample': sample})
    





@login_required(login_url='login')
def apply_job(request, job_id):
    job = get_object_or_404(Job, id=job_id)
    try:
        candidate = SeekerProfile.objects.get(user=request.user)
    except SeekerProfile.DoesNotExist:
        messages.error(request, "Candidate profile not found. Please complete your profile.")
        return redirect('index')  # Change as needed

    if Application.objects.filter(candidate=candidate, job=job).exists():
        messages.warning(request, "You have already applied for this job.")
    else:
        Application.objects.create(candidate=candidate, job=job)
        messages.success(request, "You have successfully applied!")

    return redirect('application')
