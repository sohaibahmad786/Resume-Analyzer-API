from django.shortcuts import render
import jwt
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
from .models import Resume
from .serializer import Resume_serielizer
    
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

# Create your views here.





