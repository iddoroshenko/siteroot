from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.contrib.auth import login, logout, authenticate
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

from .models import Product, Review, ReviewComment
from .forms import LoginForm, RegistrationForm, ReviewForm


def send_review(request, product_id):
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            username = request.user.username
            rating = form.cleaned_data['rating']
            city = form.cleaned_data['city']
            textPositive = form.cleaned_data['textPositive']
            textNegative = form.cleaned_data['textNegative']
            textSummary = form.cleaned_data['textSummary']

            city_error = None
            if not city or city.isspace():
                city_error = 'Please provide city'

            textPositive_error = None
            if not textPositive or textPositive.isspace():
                textPositive_error = 'Please provide textPositive'

            textNegative_error = None
            if not textNegative or textNegative.isspace():
                textNegative_error = 'Please provide textNegative'

            textSummary_error = None
            if not textSummary or textSummary.isspace():
                textSummary_error = 'Please provide textSummary'
            if textNegative_error or textPositive_error or textSummary_error or city_error:
                form.add_error('Invalid you!')
            else:
                Review(product_id=product_id, textPositive=textPositive,
                       textNegative=textNegative, textSummary=textSummary, username=username,
                       city=city, rating=rating, reviewLikes=0, reviewDislikes=0).save()
                redirect_url = request.GET.get('next') or reverse('shop_index')
                #return redirect(redirect_url)

                return HttpResponseRedirect(reverse('product_by_id', kwargs={'product_id': product_id}))
    else:
        form = ReviewForm()
    return render(request, 'shop/send_review.html', {'form': form})


def log_in(request):
    if request.method == 'POST':
        logout(request)
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect(request.GET['next'])
            else:
                form.add_error('Invalid credentials!')
    else:
        form = LoginForm()
    return render(request, 'shop/login.html', {'form': form})


def sign_up(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            logout(request)
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            password_again = form.cleaned_data['password_again']
            if User.objects.filter(username=username).exists():
                form.add_error('username', 'User already exists!')
            elif password != password_again:
                form.add_error('password_again', 'Password mismatch!')
            else:
                user = User.objects.create_user(username, email, password)
                login(request, user)
                return get_products_list(request)
    else:
        form = RegistrationForm()
    return render(request, 'shop/signup.html', {'form': form})


def log_out(request):
    logout(request)
    redirect_url = request.GET.get('next') or reverse('shop_index')
    return redirect(redirect_url)


def get_products_list(request):

    if request.user.is_authenticated:
        name = request.user.username
    else:
        name = "stranger"

    products = Product.objects.order_by('title')
    context = {'products': products,
               'username': name,
               }
    return render(request, 'shop/index.html', context)


def product(request, product_id):
    if request.method == 'POST':
        return create_review(request, product_id)
    else:
        return render_product(request, product_id)


def render_product(request, product_id, additional_context={}):
    product = get_object_or_404(Product, id=product_id)
    context = {'product': product,
               'reviews': product.review_set.order_by('-created_at'),
               'reviewComments': product.reviewcomment_set.order_by('created_at'),
               **additional_context
               }

    return render(request, 'shop/product.html', context)


@login_required(login_url='/shop/login')
def create_review(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    username = request.user.username

    city = request.POST['city']
    city_error = None
    if not city or city.isspace():
        city_error = 'Please provide city'

    textPositive = request.POST['textPositive']
    textPositive_error = None
    if not textPositive or textPositive.isspace():
        textPositive_error = 'Please provide textPositive'

    textNegative = request.POST['textNegative']
    textNegative_error = None
    if not textNegative or textNegative.isspace():
        textNegative_error = 'Please provide textNegative'

    textSummary = request.POST['textSummary']
    textSummary_error = None
    if not textSummary or textSummary.isspace():
        textSummary_error = 'Please provide textSummary'

    rating = 3
    if textNegative_error or textPositive_error or textSummary_error or city_error:
        error_context = {
            'textPositive_error': textPositive_error,
            'textPositive': textPositive,
            'textNegative_error': textNegative_error,
            'textNegative': textNegative,
            'textSummary_error': textSummary_error,
            'textSummary': textSummary,
            'city_error': city_error,
            'city': city,
        }
        return render_product(request, product_id, error_context)
    else:
        Review(product_id=product.id, textPositive=textPositive,
               textNegative=textNegative, textSummary=textSummary, username=username,
               city=city, rating=rating, reviewLikes=0, reviewDislikes=0).save()
        return HttpResponseRedirect(reverse('product_by_id', kwargs={'product_id': product_id}))


def review_comment(request, review_id):
    if request.method == 'POST':
        return create_review_comment(request, review_id)
    else:
        return render_product(request, get_object_or_404(Review, id=review_id).product.id)


@login_required(login_url='/shop/login')
def create_review_comment(request, review_id):
    review = get_object_or_404(Review, id=review_id)

    username = request.user.username

    text = request.POST['text']
    text_error = None
    if not text or text.isspace():
        text_error = 'Please provide text'
    if text_error:
        error_context = {
            'text_error': text_error,
            'text': text,
        }
        return render_product(request, review.product.id, error_context)
    else:
        ReviewComment(review_id=review.id, product_id=review.product.id, text=text, username=username).save()
        return HttpResponseRedirect(reverse('product_by_id', kwargs={'product_id': review.product.id}))

