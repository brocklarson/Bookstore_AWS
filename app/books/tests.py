from django.test import TestCase
from django.urls import reverse
from books.models import Book, Author
import pytest
# Create your tests here.
def test_homepage_access():
    url = reverse('home')
    assert url == "/"

@pytest.fixture
def new_book(db):
    book = Book.objects.create(
        title = 'The Way of Kings',
        price = 19.99,
        paperback = False,
        available = True
    )
    return book

@pytest.fixture
def another_book(db):
    book = Book.objects.create(
        title = 'The Alloy of Law',
        price = 9.99,
        paperback = True,
        available = True
    )
    return book

def test_search_book(new_book):
    assert Book.objects.filter(title='The Way of Kings').exists()

def test_cant_find_book(new_book):
    assert Book.objects.filter(title='The Rhythm of War').exists() == False

def test_update_book(new_book):
    new_book.title = 'Oathbringer'
    new_book.save()
    assert Book.objects.filter(title='Oathbringer').exists()

def test_compare_books(new_book, another_book):
    assert new_book.pk != another_book.pk

@pytest.fixture
def new_author(db):
    author = Author.objects.create(
        name = 'Brandon Sanderson'
    )
    return author

@pytest.fixture
def another_author(db):
    author = Author.objects.create(
        name = 'J.R.R. Tolkien'
    )
    return author

def test_search_author(new_author):
    assert Author.objects.filter(name='Brandon Sanderson').exists()

def test_cant_find_author(new_author):
    assert Author.objects.filter(name='Brock Larson').exists() == False

def test_update_author(new_author):
    new_author.name = 'George R.R. Martin'
    new_author.save()
    assert Author.objects.filter(name='George R.R. Martin').exists()

def test_compare_authorss(new_author, another_author):
    assert new_author.pk != another_author.pk