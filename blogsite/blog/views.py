from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth import authenticate, logout
from rest_framework_simplejwt.tokens import RefreshToken
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import get_user_model
import json
from django.shortcuts import render
from django.views.generic import ListView, DetailView
from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Post
from .forms import CommentForm
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.http import JsonResponse
from .models import Post


def index(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'index.html')

@csrf_exempt
def register_user(request):
    if request.method == "POST":
        data = json.loads(request.body)
        username = data.get("username")
        password = data.get("password")
        User = get_user_model()
        if User.objects.filter(username=username).exists():
            return JsonResponse({"error": "Username already exists"}, status=400)

        user = User.objects.create_user(username=username, password=password)
        return JsonResponse({"message": "User registered successfully"}, status=201)

@csrf_exempt
def login_user(request):
    if request.method == "POST":
        data = json.loads(request.body)
        username = data.get("username")
        password = data.get("password")
        next_url = request.GET.get('next', '/dashboard/')

        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            refresh = RefreshToken.for_user(user)
            login(request, user) 
            return JsonResponse({
                "refresh": str(refresh),
                "access": str(refresh.access_token),
                "next": next_url,
            }, status=200)
        else:
            return JsonResponse({"error": "Invalid credentials"}, status=400)

    elif request.method == "GET":
        return JsonResponse({"error": "POST method required for login"}, status=405)
    return JsonResponse({"error": "Method not allowed"}, status=405)

@csrf_exempt
def logout_user(request):
    if request.method == 'POST':
        logout(request) 
        return JsonResponse({'message': 'Logout successful'}, status=200)
    return JsonResponse({'error': 'POST method required for logout'}, status=405)

    
def dashboard(request):
    if not request.user.is_authenticated:
        return redirect('/') 
    return render(request, 'dashboard.html')


class PostListView(ListView):
    model = Post
    template_name = 'api/posts_list.html'
    context_object_name = 'posts'
    queryset = Post.objects.all().order_by('-created_at')

    def render_to_response(self, context, **response_kwargs):
        return JsonResponse({
            'posts': list(context['posts'].values())
        })


class PostCreateView(APIView):
    permission_classes = [IsAuthenticated] 

    def post(self, request, *args, **kwargs):
        try:
          
            auth = JWTAuthentication()
            user, _ = auth.authenticate(request) 
            request.user = user  
        except AuthenticationFailed:
            return redirect('/')

        title = request.data.get('title')
        content = request.data.get('content')
        post = Post.objects.create(
            title=title,
            content=content,
            author=request.user  
        )
        return JsonResponse({'message': 'Post created successfully'}, status=201)

        
class PostDetailView(DetailView):
    model = Post
    template_name = 'post_detail.html'
    context_object_name = 'post'
    
@login_required
def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    comments = post.comments.all()

    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.author = request.user
            comment.post = post
            comment.save()
            return redirect('post_detail', post_id=post.id)
    else:
        form = CommentForm()

    return render(request, 'post_detail.html', {
        'post': post,
        'comments': comments,
        'form': form,
    })

@login_required
def delete_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if post.author == request.user:
        post.delete()
    return redirect('dashboard')

@login_required
def edit_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if post.author != request.user:
        return redirect('dashboard')

    if request.method == "POST":
        title = request.POST.get('title')
        content = request.POST.get('content')
        if title and content:
            post.title = title
            post.content = content
            post.save()
            return redirect('post_detail', post_id=post.id)

    return render(request, 'edit_post.html', {'post': post})