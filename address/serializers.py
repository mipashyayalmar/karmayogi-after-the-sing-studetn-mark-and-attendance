from rest_framework import serializers
from .models import District, Upazilla, Union

class DistrictSerializer(serializers.ModelSerializer):
    class Meta:
        model = District
        fields = ['id', 'name', 'date']

class UpazillaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Upazilla
        fields = ['id', 'district', 'name', 'date']

class UnionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Union
        fields = ['id', 'district', 'upazilla', 'name', 'date']
