from django.shortcuts import render
from django.http.response import JsonResponse
from django.db.models.functions import Lower
from rest_framework.parsers import JSONParser
from rest_framework import status
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.response import Response
from rest_framework.views import APIView

from books.models import Book, Author
from books.serializers import BookSerializer, AuthorSerializer
from rest_framework.decorators import api_view

def index(request):
    context = {
        'books': Book.objects.filter(available="Available").order_by(Lower('title'))
    } 
    return render(request, "books/index.html", context)

class index(APIView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'books/index.html'

    def get(self, request):
        queryset = Book.objects.filter(available="Available").order_by(Lower('title'))
        return Response({'books': queryset})


class list_all_books(APIView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'book_list.html'

    def get(self, request):
        queryset = Book.objects.all()
        return Response({'books': queryset})


# Create your views here.
@api_view(['GET', 'POST', 'DELETE'])
def book_list(request):
    if request.method == 'GET':
        books = Book.objects.all().order_by(Lower('title'))

        title = request.GET.get('title', None)
        if title is not None:
            books = books.filter(title__icontains=title)

        books_serializer = BookSerializer(books, many=True)
        return JsonResponse(books_serializer.data, safe=False)

    elif request.method == 'POST':
        book_data = JSONParser().parse(request)
        #Validate "available" field
        if book_data['available'].lower() not in ['available', 'unavailable', 'purchased']:
            return JsonResponse(
            {
                'message':
                'Available field must be Available, Unavailable, or Purchased'
            },
            status=status.HTTP_400_BAD_REQUEST)
        #Forces "authors" field to be included in request
        if 'authors' not in book_data:
            return JsonResponse(
            {
                'message':
                'authors field required'
            },
            status=status.HTTP_400_BAD_REQUEST)
        
        # Add author
        author_ids = []
        for author in book_data["authors"]:
            try:
                #If author already in database, just append id to author_ids
                id = Author.objects.filter(name=author).values().first()["id"]
                author_ids.append(id)
            except:
                #If not, create new author 
                author_data = {"name": author}
                author_serializer = AuthorSerializer(data=author_data)
                if author_serializer.is_valid():
                    author_serializer.save()
                    author_ids.append(author_serializer.data['id'])
                else:
                    return JsonResponse(author_serializer.errors,
                                    status=status.HTTP_400_BAD_REQUEST)

        # Add book
        book_serializer = BookSerializer(data=book_data)
        if book_serializer.is_valid():
            book_serializer.save()
        else:
            return JsonResponse(book_serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)
        
        # Add correlation between book and author to book_author table
        book_id = book_serializer.data["id"]
        try:
            book = Book.objects.get(pk=book_id)
        except: 
            return JsonResponse({'message': 'Could not get book'},
                            status=status.HTTP_404_NOT_FOUND)
        for author_id in author_ids:
            try:
                author = Author.objects.get(pk=author_id)
            except: 
                return JsonResponse({'message': 'Could not get author'},
                            status=status.HTTP_404_NOT_FOUND)
            
            author.books.add(book)
            author.save()
    
        #Return created book
        book_serializer = BookSerializer(book)
        return JsonResponse(book_serializer.data,
                                status=status.HTTP_201_CREATED)

    elif request.method == 'DELETE':
        count = Book.objects.all().delete()
        return JsonResponse(
            {
                'message':
                '{} Books were deleted successfully!'.format(count[0])
            },
            status=status.HTTP_204_NO_CONTENT)

@api_view(['GET', 'PUT', 'DELETE'])
def book_detail(request, pk):
    try:
        book = Book.objects.get(pk=pk)
    except Book.DoesNotExist:
        return JsonResponse({'message': 'The book does not exist'},
                            status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        book_serializer = BookSerializer(book)
        return JsonResponse(book_serializer.data)

    elif request.method == 'PUT':
        book_data = JSONParser().parse(request)
        #Validate "available" field
        if book_data['available'].lower() not in ['available', 'unavailable', 'purchased']:
            return JsonResponse(
            {
                'message':
                'Available field must be Available, Unavailable, or Purchased'
            },
            status=status.HTTP_400_BAD_REQUEST)
        # Remove correlations between book and author
        entries = Author.books.through.objects.filter(book_id=pk)
        for entry in entries:
            entry.delete()

        # Update author
        author_ids = []
        for author in book_data["authors"]:
            try:
                #If author already in database, just append id to author_ids
                id = Author.objects.filter(name=author).values().first()["id"]
                author_ids.append(id)
            except:
                #If not, create new author 
                author_data = {"name": author}
                author_serializer = AuthorSerializer(data=author_data)
                if author_serializer.is_valid():
                    author_serializer.save()
                    author_ids.append(author_serializer.data['id'])
                else:
                    return JsonResponse(author_serializer.errors,
                                    status=status.HTTP_400_BAD_REQUEST)

                    

        # Update book
        book_serializer = BookSerializer(book, data=book_data)
        if book_serializer.is_valid():
            book_serializer.save()
        else:
            return JsonResponse(book_serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)        
        
        # Add correlation between book and author to book_author table
        for author_id in author_ids:
            try:
                author = Author.objects.get(pk=author_id)
            except: 
                return JsonResponse({'message': 'Could not get author'},
                            status=status.HTTP_404_NOT_FOUND)
            
            author.books.add(book)
            author.save()
    
        #Return created book
        book_serializer = BookSerializer(book)
        return JsonResponse(book_serializer.data,
                                status=status.HTTP_201_CREATED)
    

    elif request.method == 'DELETE':
        book.delete()
        return JsonResponse({'message': 'Book was deleted successfully!'},
                            status=status.HTTP_204_NO_CONTENT)


@api_view(['GET'])
def book_list_available(request):
    books = Book.objects.filter(available='Available').order_by(Lower('title'))

    if request.method == 'GET':
        books_serializer = BookSerializer(books, many=True)
        return JsonResponse(books_serializer.data, safe=False)

@api_view(['GET'])
def book_list_unavailable(request):
    books = Book.objects.filter(available='Unavailable').order_by(Lower('title'))

    if request.method == 'GET':
        books_serializer = BookSerializer(books, many=True)
        return JsonResponse(books_serializer.data, safe=False)

@api_view(['GET'])
def book_list_purchased(request):
    books = Book.objects.filter(available='Purchased').order_by(Lower('title'))

    if request.method == 'GET':
        books_serializer = BookSerializer(books, many=True)
        return JsonResponse(books_serializer.data, safe=False)

@api_view(['PUT'])
def book_list_purchase(request, pk):
    try:
        book = Book.objects.get(pk=pk)
    except Book.DoesNotExist:
        return JsonResponse({'message': 'The book does not exist'},
                            status=status.HTTP_404_NOT_FOUND)
    
    if request.method == 'PUT':
        book_data = {"available": "Purchased"}
        book_serializer = BookSerializer(book, data=book_data)
        if book_serializer.is_valid():
            book_serializer.save()
        else:
            return JsonResponse(book_serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)
        
        return JsonResponse(book_serializer.data,
                                status=status.HTTP_201_CREATED) 

@api_view(['GET', 'POST', 'DELETE'])
def author_list(request):
    if request.method == 'GET':
        authors = Author.objects.all()

        name = request.GET.get('name', None)
        if name is not None:
            authors = authors.filter(name__icontains=name)

        authors_serializer = AuthorSerializer(authors, many=True)
        return JsonResponse(authors_serializer.data, safe=False)
        # 'safe=False' for objects serialization

    elif request.method == 'POST':
        author_data = JSONParser().parse(request)
        author_serializer = AuthorSerializer(data=author_data)
        if author_serializer.is_valid():
            author_serializer.save()
            return JsonResponse(author_serializer.data,
                                status=status.HTTP_201_CREATED)
        return JsonResponse(author_serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        count = Author.objects.all().delete()
        return JsonResponse(
            {
                'message':
                '{} Authors were deleted successfully!'.format(count[0])
            },
            status=status.HTTP_204_NO_CONTENT)

@api_view(['GET', 'PUT', 'DELETE'])
def author_detail(request, pk):
    try:
        author = Author.objects.get(pk=pk)
    except Author.DoesNotExist:
        return JsonResponse({'message': 'The author does not exist'},
                            status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        author_serializer = AuthorSerializer(author)
        return JsonResponse(author_serializer.data)

    elif request.method == 'PUT':
        author_data = JSONParser().parse(request)
        author_serializer = AuthorSerializer(author, data=author_data)
        if author_serializer.is_valid():
            author_serializer.save()
            return JsonResponse(author_serializer.data)
        return JsonResponse(author_serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        author.delete()
        return JsonResponse({'message': 'Author was deleted successfully!'},
                            status=status.HTTP_204_NO_CONTENT)

@api_view(['GET','POST'])
def correlate_book_author(request):
    data = JSONParser().parse(request)
    try:
        author = Author.objects.get(pk=data['author_id'])
    except Author.DoesNotExist:
        return JsonResponse({'message': 'The author does not exist'},
                            status=status.HTTP_404_NOT_FOUND)
    
    try:
        book = Book.objects.get(pk=data['book_id'])
    except Book.DoesNotExist:
        return JsonResponse({'message': 'The book does not exist'},
                            status=status.HTTP_404_NOT_FOUND)
    
    if request.method == 'POST':
        author.books.add(book)
        author.save()
        return JsonResponse({'message': 'Author added to book'},
                            status=status.HTTP_201_CREATED)