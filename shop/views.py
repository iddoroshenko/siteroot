from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.contrib.auth import login, logout, authenticate
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

from .models import Product, Review, ReviewComment, ShopCart, Sentiment
from .forms import LoginForm, RegistrationForm, RatingForm, MainPageSortForm


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
                form.add_error('username', 'Invalid credentials!')
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
                cart = ShopCart.objects.create(author=user, products=[])
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
    if request.method == 'GET':
        products = Product.objects.order_by('title')
    else:
        search_line = ''
        if 'search_line' in request.POST:
            search_line = request.POST['search_line']
        sortForm = MainPageSortForm(request.POST)
        sort = 0
        if sortForm.is_valid():
            sort = sortForm.cleaned_data['choices']
        if not search_line or search_line.isspace():
            products = Product.objects.order_by('title')
        else:
            products = Product.objects.filter(title__contains=search_line).order_by('title')
        if int(sort) == 2:
            products = products.order_by('-averageRating')

    sortForm = MainPageSortForm()
    context = {'products': products,
               'username': name,
               'sortForm': sortForm,
               }
    return render(request, 'shop/index.html', context)


def get_cart_list(request):
    if request.user.is_authenticated:
        name = request.user.username
        cart = ShopCart.objects.filter(author=request.user)[0]

        products = Product.objects.order_by('title')
        productsInCart = []
        for product in products:
            if product.id in cart.products:
                productsInCart.append(product)

        context = {'products': productsInCart,
                   'username': name,
                   }
    else:
        context = {}
    return render(request, 'shop/cart.html', context)


def delete_from_cart(request, product_id):
    cart = ShopCart.objects.filter(author=request.user)[0]
    cart.products.remove(product_id)
    cart.save()
    return get_cart_list(request)


def product(request, product_id):
    if request.method == 'POST':
        return create_review(request, product_id)
    else:
        return render_product(request, product_id)


def render_product(request, product_id, additional_context={}):
    product = get_object_or_404(Product, id=product_id)
    ratingForm = RatingForm()
    context = {'product': product,
               'ratingForm': ratingForm,
               'reviews': product.review_set.order_by('-created_at'),
               'reviewComments': product.reviewcomment_set.order_by('created_at'),
               **additional_context
               }

    return render(request, 'shop/product.html', context)


def change_review(request, review_id):
    if request.method == 'GET':
        review = get_object_or_404(Review, id=review_id)
        city = review.city
        textPositive = review.textPositive
        textNegative = review.textNegative
        textSummary = review.textSummary
        rating = review.rating
        ratingForm = RatingForm()
        context = {'ratingForm': ratingForm,
                   'city': city,
                   'textPositive': textPositive,
                   'textNegative': textNegative,
                   'textSummary': textSummary,
                   'rating': rating,
                   'review': review,
                   }
        return render(request, 'shop/review_change.html', context)
    else:
        review = get_object_or_404(Review, id=review_id)
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

        ratingForm = RatingForm(request.POST)
        rating = 0
        if ratingForm.is_valid():
            rating = ratingForm.cleaned_data['rating']

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
            return render(request, 'shop/review_change.html', error_context)
        else:
            review.city = city
            review.textSummary = textSummary
            review.textNegative = textNegative
            review.textPositive = textPositive
            review.rating = rating
            review.save()
            updateAverageRating(review.product.id)
            return HttpResponseRedirect(reverse('product_by_id', kwargs={'product_id': review.product.id}))


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

    ratingForm = RatingForm(request.POST)
    rating = 0
    if ratingForm.is_valid():
        rating = ratingForm.cleaned_data['rating']

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
        Review(product_id=product.id, author=request.user, textPositive=textPositive,
               textNegative=textNegative, textSummary=textSummary, username=username,
               city=city, rating=rating, reviewLikes=0, reviewDislikes=0).save()
        updateAverageRating(product_id)
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
        ReviewComment(review_id=review.id, author=request.user, product_id=review.product.id, text=text, username=username).save()
        return HttpResponseRedirect(reverse('product_by_id', kwargs={'product_id': review.product.id}))


def addProductToCart(request, product_id):
    cart = ShopCart.objects.filter(author=request.user)[0]

    if product_id not in cart.products:
        cart.products.append(product_id)
        cart.save()
    return HttpResponseRedirect(reverse('product_by_id', kwargs={'product_id': product_id}))


def remove_review(request, review_id):
    review = get_object_or_404(Review, id=review_id)
    product_id = review.product.id
    review = Review.objects.get(id=review_id)
    review.delete()
    updateAverageRating(product_id)
    return HttpResponseRedirect(reverse('product_by_id', kwargs={'product_id': product_id}))


def remove_comment(request, comment_id):
    comment = get_object_or_404(ReviewComment, id=comment_id)
    product_id = comment.product.id
    comment = ReviewComment.objects.get(id=comment_id)
    comment.delete()
    return HttpResponseRedirect(reverse('product_by_id', kwargs={'product_id': product_id}))


def updateAverageRating(product_id):
    product = get_object_or_404(Product, id=product_id)
    reviews = Review.objects.filter(product=product)
    sum = 0
    for review in reviews:
        sum += int(review.rating)
    if len(reviews) == 0:
        product.averageRating = -1
    else:
        product.averageRating = round(sum / len(reviews), 2)
    product.save()


def like(request, review_id):
    review = get_object_or_404(Review, id=review_id)
    new_like, created = Sentiment.objects.get_or_create(author=request.user, review_id=review_id)
    if created:
        review.reviewLikes += 1
        review.save()
        new_like.vote = 1
        new_like.save()
    else:
        if new_like.vote == -1:
            review.reviewDislikes -= 1
            review.reviewLikes += 1
            review.save()
            new_like.vote = 1
            new_like.save()
        elif new_like.vote == 1:
            review.reviewLikes -= 1
            review.save()
            new_like.delete()

    return HttpResponseRedirect(reverse('product_by_id', kwargs={'product_id': review.product.id}))


def dislike(request, review_id):
    review = get_object_or_404(Review, id=review_id)
    new_dislike, created = Sentiment.objects.get_or_create(author=request.user, review_id=review_id)
    if created:
        review.reviewDislikes += 1
        review.save()
        new_dislike.vote = -1
        new_dislike.save()
    else:
        if new_dislike.vote == 1:
            review.reviewLikes -= 1
            review.reviewDislikes += 1
            new_dislike.vote = -1
            new_dislike.save()
            review.save()
        elif new_dislike.vote == -1:
            review.reviewDislikes -= 1
            new_dislike.delete()
            review.save()
    return HttpResponseRedirect(reverse('product_by_id', kwargs={'product_id': review.product.id}))