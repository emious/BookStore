from rest_framework import serializers

from books import models


class BookSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source='author.name')

    class Meta:
        model = models.Book
        fields = '__all__'


class AddBookSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Book
        fields = '__all__'
