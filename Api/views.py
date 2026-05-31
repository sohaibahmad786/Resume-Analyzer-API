from django.shortcuts import render
import jwt
import stripe
from django.views.decorators.csrf import csrf_exempt
import json
from django.http import HttpResponse
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import ListCreateAPIView
from rest_framework.generics import RetrieveUpdateDestroyAPIView
from rest_framework.authentication import TokenAuthentication,SessionAuthentication
from rest_framework import permissions
from rest_framework import generics,filters
from rest_framework.permissions import IsAuthenticated,AllowAny
from rest_framework.filters import SearchFilter
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter
from datetime import datetime, timedelta
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.db.models import Q
from rest_framework .viewsets import ModelViewSet
import PyPDF2


from .models import Register
from .serializer import Register_serializer
from .models import Search_data
from .serializer import Search_serializer
from .models import Students
from .serializer import Student_serializer
from .models import Task
from .serializer import Task_serializer
from .models import Booking
from .serializer import Booking_serializer
from .models import Message
from .serializer import Message_serializer
from .models import Person
from .serializer import Person_serializer
from .models import Company
from .serializer import Company_serializer
from .models import Cars
from .serializer import Cars_serializer
from .models import Notification
from .serializer import Notefication_serilizer
from .models import Order, Payment
from .serializer import Order_serializer,Payment_serializer
from .models import Resume
from .serializer import Resume_serielizer
from .models import Images
from .serializer import Image_serializer
from .models import Employee
from .serializer import Employee_serializer
from .models import Poll,Option,Vote
from .serializer import Poll_serializer,Option_serializer,Vote_serializer

    
class Register_view(generics.ListCreateAPIView):
    serializer_class=Register_serializer
    permission_classes=[AllowAny]
    def get_queryset(self):
        login_user=self.request.user

        if not login_user.is_authenticated:
            return Register.objects.none()

        if login_user.Role=='admin':
            return Register.objects.all()
        else:
            return Register.objects.filter(id=login_user.id)
    
class Register_detail(generics.RetrieveUpdateDestroyAPIView):
    queryset=Register.objects.all()
    serializer_class=Register_serializer
    authentication_classes=[JWTAuthentication,SessionAuthentication]
    permission_classes=[IsAuthenticated]

class Search_view(generics.ListCreateAPIView):
    queryset=Search_data.objects.all()
    serializer_class=Search_serializer
    filter_backends=[filters.SearchFilter]
    search_fields=['Name','About']
class Studentlist(generics.ListCreateAPIView):
    queryset=Students.objects.all()
    serializer_class=Student_serializer
class Studentdetail(generics.RetrieveUpdateDestroyAPIView):
    queryset=Students.objects.all()
    serializer_class=Student_serializer

class Task_listview(generics.ListCreateAPIView):
    queryset=Task.objects.all()
    serializer_class=Task_serializer
class Task_detailview(generics.RetrieveUpdateDestroyAPIView):
    queryset=Task.objects.all()
    serializer_class=Task_serializer

class Bookinglistview(generics.ListCreateAPIView):
    serializer_class=Booking_serializer
    permission_classes=[IsAuthenticated]

    def get_queryset(self):
        return Booking.objects.filter(user=self.request.user)
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class AvailableSlotView(APIView):
    def get(self,request):
        date=request.GET.get('date')
        booked_times=Booking.objects.filter(date=date).values_list('time',flat=True)
        all_slots=['7:00:00','9:00:00','10:00:00','11:00:00','12:00:00','1:00:00','2:00:00','3:00:00']
        available=[slot for slot in all_slots if slot not in booked_times]
        
        return Response({
            'available_slot':available
        })
     
class MessagelistView(ListCreateAPIView):
    serializer_class=Message_serializer
    permission_classes=[IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(sender=self.request.user)  

class Chatlistview(APIView):
    permission_classes=[IsAuthenticated]
    
    def get(self,request):
        user=request.user
        reciever_id=request.GET.get('reciever')
        messages=Message.objects.filter(
            Q(sender=user,reciever_id=reciever_id) | Q(sender_id=reciever_id,reciever=user)
        ).order_by('created_at')
        serializer=Message_serializer(messages, many=True)
        return Response(serializer.data)


class PersonViewSet(ModelViewSet):
    queryset=Person.objects.all()
    serializer_class=Person_serializer

class CompanyView(ModelViewSet):
    queryset=Company.objects.all()
    serializer_class=Company_serializer

class CarView(ModelViewSet):
    queryset=Cars.objects.all()
    serializer_class=Cars_serializer
    permission_classes=[IsAuthenticated]

    filter_backends=[DjangoFilterBackend,SearchFilter,OrderingFilter]
    search_fields=['name','company__name']
    filterset_fields=['fuel_type','color','company']
    ordering_fields=['price','model']

class NotificationView(ModelViewSet):
    queryset=Notification.objects.all()
    serializer_class=Notefication_serilizer
    permission_classes=[IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user)

stripe.api_key=settings.STRIPE_SECRET_KEY

class OrderCreateView(APIView):
    permission_classes=[IsAuthenticated]
    def post(self,request):
        amount=request.data.get('amount')
        order=Order.objects.create(
            user=request.user,
            amount=amount
        )
        return self.response({
            'order_id':order.id,
            'amount':order.amount
        })
class PaymentCreateView(APIView):
    permission_classes=[IsAuthenticated]
    def post(self,request):
        order_id=request.data.get('order_id')
        order=Order.objects.get(id=order_id)

        intent=stripe.PaymentIntent.create(
            amount=int(order.amount)*100,
            currency='usd'
        )
        Payment.objects.create(
            order=order,
            stripe_payment_intent=intent['id'],
            status='created'
        )
        return Response({
            'client_secret':intent('client_secret')
        })

@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    event = json.loads(payload)

    if event['type'] == 'payment_intent.succeeded':
        intent = event['data']['object']
        payment_intent_id = intent['id']

        payment = Payment.objects.get(stripe_payment_intent=payment_intent_id)
        payment.status = 'succeeded'
        payment.save()

        payment.order.is_paid = True
        payment.order.save()

    return HttpResponse(status=200)

class ResumeView(APIView):
    def get(self,request):

        resumes=Resume.objects.all()
        serializer=Resume_serielizer(resumes,many=True)
        return Response(serializer.data)
    
    def post(self,request):
        serializer=Resume_serielizer(data=request.data)
        serializer.is_valid()
        serializer.save()

        resume=serializer.instance
        open_pdf=open(resume.file.path,'rb')
        reader=PyPDF2.PdfReader(open_pdf)

        text=''
        for page in reader.pages:
            text+=page.extract_text()
        skill=[]
        skill_list=['javascript','react.js','python','django','DRF','djangorestframework']

        for skills in skill_list:
            skill.append(skills)
        
        return Response({
            'message':"Your Resume successfuly uploaded",
            'text':text,
            'skills':skill,
        })
        
        return Response(serializer.errors)
    
class image_View(ListCreateAPIView):
    queryset=Images.objects.all()
    serializer_class=Image_serializer

# Custom Crude Operations

class EmployeeView(APIView):

    def post(self,request):
        serializer=Employee_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors)
    
    def get(self,request):
        Data=Employee.objects.all()
        serializer=Employee_serializer(Data,many=True)
        return Response(serializer.data)
    
class EmployeeDetail(APIView):
    def put(self,request,pk):
        Data=Employee.objects.get(id=pk)
        serializer=Employee_serializer(Data,data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors)
    
    def delete(self,request,pk):
        Data=Employee.objects.get(id=pk)
        Data.delete()
        return Response({"message":"Data deleted"})

class PollView(ModelViewSet):
    queryset=Poll.objects.all()
    serializer_class=Poll_serializer
    permission_classes=[IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

class OptionView(ModelViewSet):
    queryset=Option.objects.all()
    serializer_class=Option_serializer
    permission_classes=[IsAuthenticated]

class VoteView(ModelViewSet):
    queryset=Vote.objects.all()
    serializer_class=Vote_serializer
    permission_classes=[IsAuthenticated]

    def create(self, request, *args, **kwargs):
        user=request.user
        poll_id=Poll.objects.get('poll')
        option_id=Option.objects.get('option')

        already_created=Vote.objects.filter(
            user=user,
            poll_id=poll_id
        ).exists()

        if already_created:
            return Response({'message':'you already voted'})
        
        option=Option.objects.get(id=option_id)
        option.votes+=1
        option.save()

        Vote.objects.create(
            user=user,
            poll_id=poll_id,
            option=option
        )

        return Response({
            'message':'Vote Submitted Successfully'
        })

# Create your views here.





