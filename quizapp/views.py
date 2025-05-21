from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.models import User
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .forms import CustomUserCreationForm, ForgotPasswordForm, ResetPasswordForms
from .models import Topic, QuizAttempt, Leaderboard, Question, UserResponse, Quiz ,Profile

def signup(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            verification_link = reverse('activate', kwargs={'uidb64': uid, 'token': token})
            activation_url = f"http://{get_current_site(request).domain}{verification_link}"
            message = render_to_string('email_verification.html', {'user': user, 'activation_url': activation_url})
            send_mail('Activate your account', message, settings.EMAIL_HOST_USER, [user.email], fail_silently=False)
            messages.success(request, "Signup successful! Check your email to verify your account.")
            return redirect('signin')
        for errors in form.errors.values():
            for error in errors:
                messages.error(request, error)
    else:
        form = CustomUserCreationForm()
    return render(request, 'signup.html', {'form': form})

def activate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, "Your account has been verified! You can now log in.")
        return redirect('signin')
    messages.error(request, "Activation link is invalid or has expired.")
    return redirect('signup')

def signin(request):
    if request.method == 'POST':
        username_or_email = request.POST.get('email')
        password = request.POST.get('password')
        try:
            user = User.objects.get(email=username_or_email)
            username = user.username
        except User.DoesNotExist:
            username = username_or_email
        user = authenticate(request, username=username, password=password)
        if user:
            if user.is_active:
                login(request, user)
                messages.success(request, "You have successfully logged in.")
                return redirect('dashboard')
            messages.error(request, "Your account is not verified. Check your email.")
        else:
            messages.error(request, "Invalid username or email, and/or password.")
    return render(request, 'signin.html')

def logout_view(request):
    logout(request)
    messages.success(request, "You have successfully logged out.")
    return redirect('signin')

def forgot_password(request):
    form = ForgotPasswordForm()
    if request.method == "POST":
        form = ForgotPasswordForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            try:
                user = User.objects.get(email=email)
                token = default_token_generator.make_token(user)
                uid = urlsafe_base64_encode(force_bytes(user.pk))
                message = render_to_string('reset_password_email.html', {'domain': request.get_host(), 'token': token, 'uid': uid})
                send_mail("Reset Your Password", message, 'noreply@example.com', [email])
                return render(request, "reset_password_sent.html")
            except User.DoesNotExist:
                messages.error(request, 'No user found with this email address.')
    return render(request, "forgot_password.html", {"form": form})

def reset_password(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user and default_token_generator.check_token(user, token):
        if request.method == "POST":
            form = ResetPasswordForms(request.POST)
            if form.is_valid():
                user.set_password(form.cleaned_data['new_password'])
                user.save()
                messages.success(request, "Your password has been reset successfully.")
                return redirect('signin')
            messages.error(request, "Invalid form submission.")
        else:
            form = ResetPasswordForms()
    else:
        messages.error(request, "The password reset link is invalid or expired.")
        return redirect('forgot_password')
    return render(request, 'reset_password.html', {"form": form})
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import Quiz, Leaderboard, Topic, Question

@login_required(login_url='signin')
def dashboard(request):
    quizzes = Quiz.objects.all()
    return render(request, 'dashboard.html', {'quizzes': quizzes})

@login_required
def leaderboard(request):
    leaderboard = Leaderboard.objects.select_related('user').order_by('-total_score', '-highest_score')
    return render(request, 'leaderboard.html', {'leaderboard': leaderboard})

@login_required(login_url='signin')
def submit_quiz(request, topic_id):
    if request.method == 'POST':
        user = request.user
        topic = get_object_or_404(Topic, pk=topic_id)
        user_answers = {}
        
        for key, value in request.POST.items():
            if key.startswith("answer_"):
                question_id = key.split('_')[1]
                user_answers[question_id] = value
        
        score, total_questions = calculate_user_score(topic, user_answers)
        
        leaderboard_entry, _ = Leaderboard.objects.get_or_create(user=user)
        leaderboard_entry.total_score += score
        leaderboard_entry.highest_score = max(leaderboard_entry.highest_score, score)
        leaderboard_entry.total_attempted_questions += total_questions
        leaderboard_entry.save()
        
        context = {
            'score': score,
            'total_questions': total_questions,
            'total_score': leaderboard_entry.total_score,
            'highest_score': leaderboard_entry.highest_score
        }
        return render(request, 'result.html', context)
    
    return redirect('dashboard')

# Remove the @login_required decorator from this helper function
def calculate_user_score(topic, user_answers):
    total_score = 0
    questions = Question.objects.filter(topic=topic)
    total_questions = questions.count()
    
    for question in questions:
        question_id = str(question.question_id)
        if user_answers.get(question_id) == question.correct_answer:
            total_score += 1
    
    return total_score, total_questions

    return JsonResponse({'error': 'Invalid request!'}, status=400)
@login_required(login_url='signin')
def quiz_view(request, quiz_id):
    quiz = get_object_or_404(Quiz, pk=quiz_id)
    topics = Question.objects.filter(topic=quiz.topic).values_list('topic', flat=True).distinct()
    
    questions_data = [
        {
            'id': q.question_id,  # Include question ID
            'question_text': q.question_text,
            'options': [q.option_a, q.option_b, q.option_c, q.option_d],
            'correct_answer': q.correct_answer
        }
        for t in topics for q in Question.objects.filter(topic=t).order_by('?')[:10]
    ]
    
    return render(request, 'quiz.html', {'quiz': quiz, 'questions': questions_data})

@login_required(login_url='signin')
def result(request):
    # quiz_result = request.session.get('quiz_result', None)
    # print("quiz_result",quiz_result)
    # if not quiz_result:
    #     return redirect('dashboard')
    return render(request, 'result.html')
@login_required(login_url='signin')
def profile(request):
    email = request.user.email
    profile = Profile.objects.filter(user=request.user)
    print(profile)
    user = request.user
    return render(request,'profile.html',{'email':email,'username':user})