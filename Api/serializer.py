from rest_framework import serializers
from django.contrib.auth.hashers import make_password, check_password
from .models import Register
from .models import Search_data
from .models import Students
from .models import Task
from .models import Booking
from .models import Message
from .models import Person
from .models import Company
from .models import Cars
from .models import Notification
from .models import Order
from .models import Payment
from .models import Resume
from .models import Images
from .models import Employee
from .models import Poll,Option,Vote
        

class Register_serializer(serializers.ModelSerializer):
    class Meta:
        model=Register
        fields=['username','Role','email','password','id']
        
    def create(self, validated_data):
        validated_data['password']=make_password(validated_data['password'])
        return super().create(validated_data)

class Search_serializer(serializers.ModelSerializer):
    class Meta:
        model=Search_data
        fields='__all__'

class Student_serializer(serializers.ModelSerializer):
    class Meta:
        model=Students
        fields='__all__'

class Task_serializer(serializers.ModelSerializer):
    class Meta:
        model=Task
        fields='__all__'

class Booking_serializer(serializers.ModelSerializer):
    class Meta:
        model=Booking
        fields='__all__'
        extra_kwargs={
           'user':{'read_only':True}
        }

class Message_serializer(serializers.ModelSerializer):
    class Meta:
        model=Message
        fields='__all__'
        extra_kwargs={
            'sender':{'read_only':True}
        }

class Person_serializer(serializers.ModelSerializer):
    class Meta:
        model=Person
        fields='__all__'



class Cars_serializer(serializers.ModelSerializer):
    class Meta:
        model=Cars
        fields='__all__'
    def validate_price(self,value):
        if value<=0:
            raise serializers.ValidationError("Price Can't be zero or less than zero")

class Company_serializer(serializers.ModelSerializer):
    cars=Cars_serializer(many=True,read_only=True)
    class Meta:
        model=Company
        fields=['id','name','cars']
    
class Notefication_serilizer(serializers.ModelSerializer):
    class Meta:
        model=Notification
        fields='__all__'

class Order_serializer(serializers.ModelSerializer):
    class Meta:
        model=Order
        fields='__all__'
        extra_kwargs={
            'user':{'read_only':True},
            'is_paid':{'read_only':True}
        }
class Payment_serializer(serializers.ModelSerializer):
    class Meta:
        model=Payment
        fields='__all__'

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

class Image_serializer(serializers.ModelSerializer):
    class Meta:
        model=Images
        fields='__all__'

class Employee_serializer(serializers.ModelSerializer):
    class Meta:
        model=Employee
        fields='__all__'

class Poll_serializer(serializers.ModelSerializer):
    class Meta:
        model=Poll
        fields='__all__'
        extra_kwargs={
           'created_by':{'read_only':True}
        }
class Option_serializer(serializers.ModelSerializer):
    class Meta:
        model=Option
        fields='__all__'
class Vote_serializer(serializers.ModelSerializer):
    class Meta:
        model=Vote
        fields='__all__'