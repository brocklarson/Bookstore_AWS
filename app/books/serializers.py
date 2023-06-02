from rest_framework import serializers
from books.models import Book, Author

class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = ('id', 'name')
        
class BookSerializer(serializers.ModelSerializer):
    authors = AuthorSerializer(read_only=True, many=True)
    class Meta:
        model = Book
        fields = ('id', 'title', 'price', 'paperback', 'available', 'authors')




