from django.urls import path, include
from . import views


urlpatterns = [

    # path(
    #     'add/', views.CartMethodViewsetes.as_view({'post': 'create'}), name='add-favorite'),
    # path('add-list/',
    #      views.CartMethodViewsetes.as_view({'post': 'create_list'}), name='add-favorites'),

    # path('<int:pk>/delete/',
    #      views.CartMethodViewsetes.as_view({'delete': 'destroy'}), name='delete-favorite'),
    # path('delete-all/',
    #      views.CartMethodViewsetes.as_view({'post': 'destroy_list'}), name='delete_all-favorite'),
    # path('delete-list/', views.CartMethodViewsetes.as_view({'post': 'destroy_list'}),
    #      name='delete_list-cart'),
    # path('<int:pk>/update-count/',
    #      views.CartMethodViewsetes.as_view({'post': 'create'}), name='update-favorite'),



    path('', views.FavoriteView.as_view({'get': 'list'})),

    path('create/', views.FavoriteView.as_view({'post': 'create'})),

    path('<prop_id>/delete/',
         views.FavoriteView.as_view({'delete': 'destroy'})),
    path('delete-all/',
         views.FavoriteView.as_view({'post': 'destroy_list'}), name='delete_all_favorite'),
    path('delete-list/', views.FavoriteView.as_view({'post': 'destroy_list'}),
         name='delete_list_favorite'),

    #     path('review/create/',
    #          views.CreateReviewView.as_view({'post': 'create'})),
    #     path('reviewlike/create/',
    #          views.CreateReviewLikeView.as_view({'post': 'create'})),



    #     path('<pk>/', views.ProductView.as_view({'get': 'retrieve'})),

    # path('products/create/', views.ProductView.as_view({'post': 'create'})),

]
