import random
import pendulum
from unidecode import unidecode
from django.db.models import Q, Case, When, Value, IntegerField, Sum
from django.conf import settings
from rest_framework import serializers
from news.models import (Category, News, Country,
                         Source, CategoryNote, Reaction,
                         BlappNote, SubcategoryBlappNote
                         )
from profiles.models import (LikedNews,
                             SavedLater,
                             BlappedNews,
                             SharedNews,
                             UserReaction)
from users.models import BlappUser

# NOW = pendulum.now()


class ReactionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Reaction
        fields = ['id', 'name', 'icon', 'icon_selected']


class CategoryNoteSerializer(serializers.ModelSerializer):

    class Meta:
        model = CategoryNote
        fields = ['id', 'name']


class SourceSeriaLizer(serializers.ModelSerializer):

    class Meta:
        model = Source
        fields = ['id', 'name', 'icon', 'selected_icon']


class CategorySerializer(serializers.ModelSerializer):
    category_type = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'name', 'icon', 'selected_icon', 'category_type']

    def get_category_type(self, obj):
        return 'Category'

class CategoryNotesSerializer(serializers.ModelSerializer):
    notes = serializers.SerializerMethodField()

    class Meta:
        model = CategoryNote
        fields = ['id', 'name', 'icon', 'notes']

    def get_notes(self, obj):
        notes = SubcategoryBlappNote.objects.filter(category=obj.id)
        serialized_blappnotes = BlappNoteSerializer(notes, many=True)
        return serialized_blappnotes.data

class GetProfileCountrySerializer(serializers.ModelSerializer):
    name = serializers.ReadOnlyField(source='country.name')
    icon = serializers.SerializerMethodField()
    category_type = serializers.SerializerMethodField()
    id = serializers.ReadOnlyField(source='country_id')

    class Meta:
        model = ProfileCountry
        fields = ['id', 'name', 'icon', 'category_type']

    def get_icon(self, obj):
        return ''

    def get_category_type(self, obj):
        return 'country'

