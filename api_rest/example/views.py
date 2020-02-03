from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.shortcuts import render
from django.db.models import (F, Subquery, Count, IntegerField, Value, Case,
                              When, Sum)
from rest_framework import status
from django.conf import settings
from django.http import HttpResponse
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from rest_framework.permissions import AllowAny


class ValidatePhoneNumber(APIView):

    permission_classes = [AllowAny]

    def post(self, request):
        phone_number = request.data.get("phone_number")
        status_code = status.HTTP_200_OK
        data_response = {'status': 1}
        try:
            pending_guest = GuestPhone.objects.get(phone=phone_number,
                                                   status=True)
            data_response['user'] = {
                'exists': False,
                'phone': phone_number,
                'guest': True,
                'parent': pending_guest.parent_user.id
            }
            data_response['subscription'] = {
                'status': 'Inactive',
                'reasons': ['PENDING_INVITATION']
            }
        except GuestPhone.DoesNotExist:
            profile = Profile.objects.filter(phone=phone_number).first()
            data_response = get_profile_status(profile)
        return Response(data_response, status=status_code)


class AnotherView(APIView):
        def post(self, request):
        status_response = status.HTTP_200_OK
        user_id = request.user.id
        news_id = request.data.get('news_id')
        data_response = {'status': 1}
        try:
            news_later, created = SavedLater.objects.get_or_create(
                news_id=news_id, user_id=user_id)
        except Exception as e:
            data_response['message'] = "Id de noticia no válido"
        return Response(data_response, status=status_response)

    def delete(self, request):
        data_response = {'status': 1}
        status_response = status.HTTP_200_OK
        user_id = request.user.id
        news_id = request.data.get('news_id')
        try:
            deleted_news = SavedLater.objects.filter(
                news_id=news_id, user_id=user_id).delete()
        except Exception as e:
            status_response = status.HTTP_400_BAD_REQUEST
            data_response['message'] = 'Id de noticia no válido'

        return Response(data_response, status=status_response)


# Create your views here.


class CustomLoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        NOW = pendulum.now()
        code = request.data.get("verification_code")
        phone_number = request.data.get("phone_number")
        status_code = status.HTTP_200_OK
        data_response = {'status': 1}
        code_duration = VerificationCodeDuration.objects.all().first().duration
        code_life = NOW.subtract(hours=code_duration)
        valid_code = VerificationCode.objects.filter(phone_number=phone_number,
                                                     code=code,
                                                     sent_date__gte=code_life,
                                                     status=True).count()

        if valid_code > 0:
            user = BlappUser.objects.filter(
                profile__phone=phone_number,
                profile__status__in=[Profile.ACTIVE, Profile.REVOKED, Profile.CANCELLED]).first()
            if user:
                Token.objects.filter(user=user).delete()
                token = Token.objects.get_or_create(user=user)[0].key
                profile = Profile.objects.get(user=user)
                serialized_profile = ProfileSerializer(profile)
                data_response['token'] = token
                data_response['data'] = serialized_profile.data

            else:
                data_response['message'] = 'Usuario no registrado'
            return Response(data_response, status=status.HTTP_200_OK)
        else:
            data_response['status'] = 0
            data_response['message'] = 'Código no válido'

        status_code = status.HTTP_200_OK
        return Response(data_response, status=status_code)



class CustomUser(AbstractUser, SafeDeleteModel):
    MASCULINO = "MASCULINO"
    FEMENINO = "FEMENINO"

    SEX_CHOICES = [
        (MASCULINO, u'masculino'),
        (FEMENINO, u'femenino')
    ]

    phone = models.CharField(
        verbose_name=u"Teléfono/Celular",
        max_length=9,
        blank=True,
        null=True,
        validators=[phone_validator]
    )
    names = models.CharField(
        max_length=250,
        null=True,
        verbose_name="Nombres"
    )
    sex = models.CharField(verbose_name=u'Sexo',
                           max_length=30, choices=SEX_CHOICES,
                           blank=True,
                           null=True
                           )
    birth_date = models.DateField(null=True, blank=True)
    document_type = models.ForeignKey(
        DocumentType,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        verbose_name="Tipo de documento"
    )
    document_number = models.CharField(
        verbose_name=u'Número de documento',
        null=True, blank=True,
        max_length=15,
        unique=True,
    )
    segments = ArrayField(
        models.CharField(max_length=10, blank=True),
        size=20,
        null=True,
        blank=True
    )
    products = ArrayField(
        models.CharField(max_length=10, blank=True),
        size=20,
        null=True,
        blank=True
    )
    first_login = models.BooleanField(default=True)
    department = models.ForeignKey(
        "ubigeo.Ubigeo",
        verbose_name="Ubigeo",
        null=True,
        blank=True,
        on_delete=models.SET_NULL
    )
    # notifications = models.ManyToManyField(Notification)

    def get_deparment(self):
        return 15 if not self.department else self.department.pk



