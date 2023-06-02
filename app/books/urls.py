from django.urls import path
from books import views as books_views
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('', books_views.index.as_view(), name='home'),
    path('api/books/', books_views.book_list),
    path('api/books/<int:pk>/', books_views.book_detail),
    path('api/books/available/', books_views.book_list_available),
    path('api/books/unavailable/', books_views.book_list_unavailable),
    path('api/books/purchased/', books_views.book_list_purchased),
    path('api/books/purchase/<int:pk>/', books_views.book_list_purchase),
    path('api/authors/', books_views.author_list),
    path('api/authors/<int:pk>/', books_views.author_detail),
    path('api/book_author/', books_views.correlate_book_author),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)