from django.urls import path
from . import views


urlpatterns = [
    path('', views.get_products_list, name='shop_index'),
    path('product/<int:product_id>', views.product, name='product_by_id'),
    path('<int:review_id>', views.review_comment, name='reviewComment'),
    path('remove_comment/<int:comment_id>', views.remove_comment, name='remove_comment'),
    path('login', views.log_in, name='login'),
    path('signup', views.sign_up, name='signup'),
    path('logout', views.log_out, name='logout'),
    path('cart', views.get_cart_list, name='cart'),
    path('addProductToCart/<int:product_id>', views.addProductToCart, name='addProductToCart'),
    path('cart/<int:product_id>', views.delete_from_cart, name='delete_from_cart'),
    path('change_review/<int:review_id>', views.change_review, name='change_review'),
    path('remove_review/<int:review_id>', views.remove_review, name='remove_review'),
    path('likes/<int:review_id>', views.like, name='like'),
    path('dislike/<int:review_id>', views.dislike, name='dislike'),
]
