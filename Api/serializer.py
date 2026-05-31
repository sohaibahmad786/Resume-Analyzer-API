from rest_framework import serializers
from django.contrib.auth.hashers import make_password, check_password
from .models import Register
from .models import Resume


class Register_serializer(serializers.ModelSerializer):
    class Meta:
        model=Register
        fields=['username','Role','email','password','id']
        
    def create(self, validated_data):
        validated_data['password']=make_password(validated_data['password'])
        return super().create(validated_data)


class Resume_serielizer(serializers.ModelSerializer):
    class Meta:
        model=Resume
        fields='__all__'

        def validate_file(self,value):
            if not value:
                raise serializers.ValidationError("Please Enter Resume")
            if not value.name.endswith('.pdf'):
                raise serializers.ValidationError('pdf file only allowed')
            if value.size > 5 * 1024 *1024:
                raise serializers.ValidationError('file size must be less than 5MB')
            
            return value
