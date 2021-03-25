from django.urls import path
from . import views


urlpatterns = [
    path('', views.get_products_list, name='shop_index'),
    path('product/<int:product_id>', views.product, name='product_by_id'),
    path('<int:review_id>', views.review_comment, name='reviewComment'),
    path('login', views.log_in, name='login'),
    path('signup', views.sign_up, name='signup'),
    path('logout', views.log_out, name='logout'),
    path('addProductToCart/<int:product_id>', views.addProductToCart, name='addProductToCart'),
]
