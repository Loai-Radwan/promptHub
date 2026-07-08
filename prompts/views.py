from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.urls import reverse
from django import forms
from django.core.paginator import Paginator
from django.views.decorators.cache import cache_page
from django.core.cache import cache
import re
import os
import markdown2
from django.db.models import F, Sum
from django.contrib import messages
from .models import User, Prompt, Category
from PIL import Image


class PromptForm(forms.ModelForm):
    class Meta:
        model = Prompt
        fields = [
            "title",
            "description",
            "content",
            "category",
            "visibility",
        ]

        widgets = {
            "title": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Example: Senior Django Code Reviewer"
            }),
            "description": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 3,
                "placeholder": "Short description of what this prompt does"
            }),
            "content": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 10,
                "placeholder": "Write the full prompt here..."
            }),
            "category": forms.Select(attrs={
                "class": "form-select"
            }),
            "visibility": forms.Select(attrs={
                "class": "form-select"
            }),
        }


class EditProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["first_name", "last_name", "email", "bio", "avatar"]

        widgets = {
            "first_name": forms.TextInput(attrs={"class": "form-control"}),
            "last_name": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
            "bio": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 4,
                "placeholder": "Write something about yourself..."
            }),
            "avatar": forms.FileInput(attrs={"class": "form-control"}),
        }

# Create your views here.
CACHE_TIME = 3000

@cache_page(CACHE_TIME)
def index(request):
    total_user = User.objects.count()
    total_prompts = Prompt.objects.count()
    total_copies = (Prompt.objects.aggregate(
        Sum("copies")
    )["copies__sum"] or 0
    )
    return render(request, "prompts/index.html", {
        "total_user": total_user,
        "total_prompts": total_prompts,
        "total_copies": total_copies


    })


@login_required
def dashboard(request):

    request.user.total_views = (
        request.user.prompts.aggregate(
            Sum("views")
        )["views__sum"] or 0
    )
    request.user.total_copies = (
        request.user.prompts.aggregate(
            Sum("copies")
        )["copies__sum"] or 0
    )
    return render(request, "prompts/dashboard.html")


@login_required
def create_prompt(request):
    if request.method == "POST":
        form = PromptForm(request.POST)

        if form.is_valid():
            prompt = form.save(commit=False)
            prompt.author = request.user
            prompt.save()
            messages.success(request, "Prompt was created successfully")
            return redirect(reverse('dashboard'))
    else:
        form = PromptForm()
    return render(request, "prompts/create_prompt.html", {
        "form": form
    })


def browse(request):
    categories = cache.get("all_categories")

    if categories is None:
        categories = list(Category.objects.all())
        cache.set("all_categories", categories, CACHE_TIME)

    prompts = cache.get("all_prompts")

    if prompts is None:
        prompts = Prompt.objects.filter(visibility='public')
        cache.set("all_prompts", prompts, CACHE_TIME)


    q = request.GET.get("q")
    if q:
        prompts = prompts.filter(title__icontains=q)

    category = request.GET.get("category")
    if category:
        prompts = prompts.filter(category__slug=category)

    paginator = Paginator(prompts, 9)
    page_obj = paginator.get_page(request.GET.get("page"))

    return render(request, "prompts/browse.html", {
        "categories": categories,
        "page_obj": page_obj
    })


def prompt(request, id):
    if not request.user.is_authenticated:
        messages.warning(
            request, "You have to be logged in in oreder to see a prompt")
        return redirect(reverse('login'))

    if request.method == "PUT":
        updated = Prompt.objects.filter(pk=id).update(
            copies=F("copies") + 1
        )

        if updated == 0:
            return HttpResponse(status=404)

        return HttpResponse(status=204)

    try:
        prompt = Prompt.objects.get(pk=id)
    except Prompt.DoesNotExist:
        return render(request, "prompts/404.html", {
            "message": "Prompt was not fount"
        })
    if prompt.visibility == 'private' and prompt.author != request.user:
        return render(request, "prompts/403.html", {
            "message": "This prompt is private"
        })

    Prompt.objects.filter(pk=id).update(
        views=F("views") + 1
    )
    prompt.refresh_from_db()
    return render(request, "prompts/prompt.html", {
        "prompt": prompt,
        "content": markdown2.markdown(prompt.content)
    })

@login_required
def edit_prompt(request, id):
    try:
        prompt = Prompt.objects.get(pk=id)
    except Prompt.DoesNotExist:
        return render(request, "prompts/404.html", {
            "message": "Prompt was not fount"
        })
    if prompt.author != request.user:
        return render(request, "prompts/403.html", {
            "message": "You don't have permission to edit this prompt"
        })

    if request.method == "POST":
        form = PromptForm(request.POST, instance=prompt)
        if form.is_valid():
            prompt = form.save(commit=False)
            prompt.author = request.user
            prompt.save()
            messages.success(request, "Prompt  updated successfully.")
            return redirect(reverse('prompt', kwargs={
                "id": prompt.id
            }))
    else:
        form = PromptForm(instance=prompt)

    return render(request, "prompts/edit_prompt.html", {
        "prompt": prompt,
        "form": form
    })

@cache_page(CACHE_TIME)
def categories(request):
    categories = Category.objects.all()
    for category in categories:
        category.prompts_count = category.prompts.filter(
            visibility='public').count()

    return render(request, "prompts/categories.html", {
        "categories": categories,
    })

@cache_page(CACHE_TIME)
def category(request, name):
    try:
        category = Category.objects.get(slug=name)
    except Category.DoesNotExist:
        return render(request, "prompts/404.html", {
            "message": f"{name} categroy was not found"
        })

    prompts = category.prompts.filter(visibility='public')
    paginator = Paginator(prompts, 9)
    page_obj = paginator.get_page(request.GET.get("page"))

    return render(request, "prompts/category.html", {
        "category": category,
        "page_obj": page_obj
    })


def user(request, username):
    try:
        profile_user = User.objects.get(username=username)
    except User.DoesNotExist:
        return render(request, "prompts/404.html", {
            "message": "User don't exists"
        })

    if request.user == profile_user:
        prompts = request.user.prompts.all()
    else:
        prompts = profile_user.prompts.filter(visibility="public")
        profile_user.total_views = (
            profile_user.prompts.aggregate(
                Sum("views")
            )["views__sum"] or 0
        )
        profile_user.total_copies = (
            profile_user.prompts.aggregate(
                Sum("copies")
            )["copies__sum"] or 0
        )

    return render(request, "prompts/user.html", {
        "profile_user": profile_user,
        "prompts": prompts

    })


def edit_profile(request):
    if request.method == "POST":
        form = EditProfileForm(
            request.POST,
            request.FILES,
            instance=request.user
        )

        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully.")
            return redirect(reverse("user", kwargs={
                "username": request.user.username
            }))
    else:
        form = EditProfileForm(instance=request.user)

    return render(request, "prompts/edit_profile.html", {
        "form": form
    })


@login_required
def upload_profile_picture(request):
    if request.method == "POST":
        # Get image
        file = request.FILES.get("profile_picture")

        if not file:
            messages.error(request, "No image selected.")
            return redirect(reverse("user", kwargs={
                "username": request.user.username
            }))

        # check if what user uploaded is an image
        try:
            Image.open(file).verify()
            file.seek(0)
        except Exception:
            messages.error(request, "Invalid image file.")
            return redirect(reverse('user', kwargs={
                "username": request.user.username
            }))

        user = request.user

        # Delete old image if it is not the default image
        if user.avatar and user.avatar.name != "avatars/default.png":
            old_image_path = user.avatar.path

            if os.path.exists(old_image_path):
                os.remove(old_image_path)

        file.name = f"{user.username}.{file.name.rsplit('.', 1)[-1].lower()}"
        user.avatar = file
        user.save()
        messages.success(request, "Profile picture updated successfully.")

        return redirect(reverse('user', kwargs={
            "username": user.username
        }))

    return redirect(reverse("user", kwargs={
        "username": request.user.username
    }))


def login_view(request):
    if request.method == "POST":
        username = request.POST["username"].strip()
        password = request.POST["password"].strip()
        form = {
            "username": username,
            "password": password
        }
        if not username:
            messages.error(request, "Username or Email is required")
            return render(request, "prompts/login.html", {
                "form_content": form
            })

        if not password:
            messages.error(request, "Password is required")
            return render(request, "prompts/login.html", {
                "form_content": form
            })

        if is_email(username):
            user = authenticateWithEmail(email=username, password=password)
            if not user:
                messages.error(request, "Invalid email or password")
                return render(request, "prompts/login.html", {
                    "form_content": form
                })

        elif not is_email(username):
            user = authenticate(request, username=username, password=password)
            if not user:
                messages.error(request, "Invalid username or password")
                return render(request, "prompts/login.html", {
                    "form_content": form
                })

        messages.success(request, "You were logged in successfully")
        login(request, user)
        # cache.clear()
        return redirect(reverse('dashboard'))
    return render(request, "prompts/login.html")


def register(request):
    if request.method == "POST":
        username = request.POST["username"].strip()
        email = request.POST["email"].strip()
        password = request.POST["password"].strip()
        cpassword = request.POST["cpassword"].strip()

        form = {
            "username": username,
            "email": email,
            "password": password,
            "cpassword": cpassword,
        }

        if not username:
            messages.error(request, "Username is required")
            return render(request, "prompts/register.html", {
                "form_content": form
            })

        if not email:
            messages.error(request, "Email is required")
            return render(request, "prompts/register.html", {
                "form_content": form
            })

        if not password:
            messages.error(request, "Password is required")
            return render(request, "prompts/register.html", {
                "form_content": form
            })

        if not cpassword:
            messages.error(request, "Confirm Password is required")
            return render(request, "prompts/register.html", {
                "form_content": form
            })

        if password != cpassword:
            messages.error(request, "Passwords must match")
            return render(request, "prompts/register.html", {
                "form_content": form
            })

        if not is_email(email):
            messages.error(request, "Invalid Email")
            return render(request, "prompts/register.html", {
                "form_content": form
            })

        if not check_username(username):
            messages.error(request,  "Username already taken ")
            return render(request, "prompts/register.html", {
                "form_content": form
            })

        if not check_email(email):
            messages.error(request, "Email already exists try to log in ")
            return render(request, "prompts/register.html", {
                "form_content": form
            })

        user = User.objects.create_user(username, email, password)
        user.save()

        messages.success(request, "You were registered successfully")
        login(request, user)
        # cache.clear()

        return redirect(reverse('dashboard'))

    return render(request, "prompts/register.html")


def logout_view(request):
    logout(request)
    # cache.clear()
    return redirect(reverse("index"))


def check_username(username):
    """Check if a username is availabel """
    return not User.objects.filter(username=username).exists()


def check_email(email):
    """Check if a email is availabel """
    return not User.objects.filter(email=email).exists()


def is_email(email):
    return re.search(r'^[\w\.-]+@[\w\.-]+\.\w+$', email)


def authenticateWithEmail(email, password):

    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return None

    if user.check_password(password):
        return user

    return None
