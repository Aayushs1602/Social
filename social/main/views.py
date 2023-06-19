from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.models import User, auth
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Profile, Post, likePost, FollwersCount
from itertools import chain
import random

# Create your views here.

@login_required(login_url='login')
def index(request):
    user = User.objects.get(username=request.user.username)
    user_profile = Profile.objects.get(user=user)

    user_following_list = []
    feed = []

    user_following = FollwersCount.objects.filter(follower=request.user.username)
    for users in user_following:
        user_following_list.append(users.user)

    for username in user_following_list:
        feed_lists = Post.objects.filter(user=username)
        feed.append(feed_lists)

    feed_list = list(chain(*feed))

    # user suggestions
    all_user = User.objects.all()
    user_following_all = []

    for user in user_following:
        user_list = User.objects.get(username=user.user)
        user_following_all.append(user_list)

    new_suggestions_list = [x for x in list(all_user) if x not in list(user_following_all)]
    current_user = User.objects.filter(username=request.user.username)
    final_suggestions_list = [x for x in list(new_suggestions_list) if x not in list(current_user)]
    random.shuffle(final_suggestions_list)
    
    username_profile = []
    username_profile_list = []

    for user in final_suggestions_list:
        username_profile.append(user.id)

    for ids in username_profile:
        profile_lists = Profile.objects.filter(id_user=ids)
        username_profile_list.append(profile_lists)

    suggestions_username_profile_list = list(chain(*username_profile_list))

    context = {'user': user_profile,
               'posts': feed_list,
               'suggestions_username_profile_list': suggestions_username_profile_list[:4]}
    return render(request, 'index.html',context
                  )

def signup(request):

    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        password2 = request.POST['password2']
        email = request.POST['email']

        if password == password2:
            if User.objects.filter(username=username).exists():
                messages.info(request, 'Username already exists')
                return render(request,'signup.html', {'error': 'Username already exists'})
            if User.objects.filter(email=email).exists():
                messages.info(request, 'Email invalid')
                return render(request,'signup.html', {'error': 'Email already exists'})
            user = User.objects.create_user(username=username, password=password, email=email)
            auth.login(request, user)

            user_login = auth.authenticate(username=username, password=password,)
            auth.login(request, user_login)


            user_model = User.objects.get(username=username)
            new_profile = Profile.objects.create(user=user_model, id_user=user_model.id)
            new_profile.save()
            return redirect('settings')
        else:
            messages.info(request, 'Passwords do not match')
            return render(request,'signup.html')

    return render(request,'signup.html')

def login(request):

    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = auth.authenticate(username=username, password=password)

        if user is not None:
            auth.login(request, user)
            return redirect('/')
        
        messages.info(request, 'Credentials do not match')
        return render(request, 'signin.html')
    return render(request,'signin.html')

def logout(request):
    auth.logout(request)
    return redirect('login')

@login_required(login_url='login')
def settings(request):
    user_profile = Profile.objects.get(user = request.user)

    if request.method == 'POST':
        if request.FILES.get('image') ==None:
            image = user_profile.profileimg
            bio = request.POST.get('bio')
            location = request.POST.get('location')

            user_profile.profileimg = image
            user_profile.bio = bio
            user_profile.location = location
            user_profile.save()
        
        if request.FILES.get('image') != None:
        
            image = request.FILES.get('image')
            bio = request.POST.get('bio')
            location = request.POST.get('location')

            user_profile.profileimg = image
            user_profile.bio = bio
            user_profile.location = location 
            user_profile.save()

        return redirect('settings')

    return render(request,'setting.html', {'user': user_profile})

@login_required(login_url="login")
def upload(request):
    if request.method == 'POST':
        user = request.user.username        
        image = request.FILES.get('image_upload')
        caption = request.POST.get('caption')

        new_post = Post.objects.create(user=user, image=image, caption=caption,)
        return redirect('/')
    

    return redirect('/')

@login_required(login_url="login")
def like_post(request):
    username = request.user.username
    post_id = request.GET.get('post_id')

    post = Post.objects.get(id=post_id)

    like_filter = likePost.objects.filter(post_id=post_id, username=username).first()
    print(like_filter)
    if like_filter == None:
        new_like = likePost.objects.create(post_id=post_id, username=username)
        new_like.save()
        post.no_of_likes += 1
        post.save()
        return redirect('/')
    else:
        like_filter.delete()
        post.no_of_likes -= 1
        post.save()
        return redirect('/')

@login_required(login_url="login")
def profile(request, pk):
    user_object = User.objects.get(username=pk)
    user_profile = Profile.objects.get(user=user_object)
    user_post = Post.objects.filter(user=pk)
    user_post_length = len(user_post)

    follower = request.user.username
    user = pk

    if FollwersCount.objects.filter(follower=follower, user=user).first():
        button_text = 'Unfollow'
    else:
        button_text = "Follow"
    user_followers = len(FollwersCount.objects.filter(user=pk))
    user_following = len(FollwersCount.objects.filter(follower=pk))

    context ={
        'user_object': user_object,
        'user_profile': user_profile,
        'user_post': user_post,
        'user_post_length': user_post_length,
        'button_text': button_text,
        'user_followers': user_followers,
        'user_following': user_following,
    }
    return render(request, 'profile.html', context)

@login_required(login_url="login")
def follow(request):

    if request.method == 'POST':
        follower = request.POST.get('follower')
        user = request.POST.get('user')

        if FollwersCount.objects.filter(follower=follower, user=user).first():
            delete_follower = FollwersCount.objects.get(user=user, follower= follower)
            delete_follower.delete()
            return redirect('profile/'+user)
        
        new_follower = FollwersCount.objects.create(follower=follower, user=user)
        new_follower.save()
        return redirect('profile/'+user)
    
    return redirect('/')

@login_required(login_url="login")
def search(request):
    user_object = User.objects.get(username=request.user.username)
    user_profile = Profile.objects.get(user=user_object)
     
    if request.method == 'POST':
        username = request.POST.get('username')
        username_object = User.objects.filter(username__icontains=username)

        username_profile = []
        username_profile_list = []
        for users in username_object:
            username_profile.append(users.id)

        for ids in username_profile:
            profile_lists = Profile.objects.filter(id_user=ids)
            username_profile_list.append(profile_lists)

        username_profile_list = list(chain(*username_profile_list))

    return render(request, 'search.html', {'user_profile': user_profile, 'usernames': username_profile_list})