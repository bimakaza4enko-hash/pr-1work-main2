from django.urls import path, re_path, include
from . import views
from .views import AllBorrowedBooksListView

urlpatterns = [
    path('', views.index, name='index'),
    path('books/', views.BookListView.as_view(), name='books'),
    re_path(r'^book/(?P<pk>\d+)$', views.BookDetailView.as_view(), name='book-detail'),
    path('authors', views.AuthorListView.as_view(), name='authors'),
    path('author/<pk>', views.AuthorDetailView.as_view(), name='author-detail'),
    path('borrowed/', AllBorrowedBooksListView.as_view(), name='all-borrowed'),
    # Перемещено из старого второго списка
    path('book/create/', views.create_book, name='create_book'),
    path('author/create/', views.create_author, name='create_author'),
]


urlpatterns += [
    re_path(r'^mybooks/$', views.LoanedBooksByUserListView.as_view(), name='my-borrowed'), # Это имя теперь снова доступно
]

urlpatterns += [
    path('book/<uuid:pk>/renew/', views.renew_book_librarian, name='renew-book-librarian'),
]

urlpatterns += [
    re_path(r'^author/create/$', views.AuthorCreate.as_view(), name='author_create'), # Возможно, дублируется, см. выше
    re_path(r'^author/(?P<pk>\d+)/update/$', views.AuthorUpdate.as_view(), name='author_update'),
    re_path(r'^author/(?P<pk>\d+)/delete/$', views.AuthorDelete.as_view(), name='author_delete'),
    re_path(r'^allborrowed/$', views.AllBorrowedBooksListView.as_view(), name='all-borrowed'),
]

urlpatterns += [
    path('book/create/', views.BookCreate.as_view(), name='book_create'), # Возможно, дублируется, см. выше
    path('book/<int:pk>/update/', views.BookUpdate.as_view(), name='book_update'),
    path('book/<int:pk>/delete/', views.BookDelete.as_view(), name='book_delete'),
]
