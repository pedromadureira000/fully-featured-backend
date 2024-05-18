from django.db import models
from django.utils import timezone
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from rest_framework.authtoken.models import Token

subscription_status = (
    (1, "trial"),
    (2, "trial_ended"),
    (3, "subscription_paid"),
    (4, "subscription_unpaid"),
    (5, "subscription_cancelled"),
)

class UserBase(models.Model):
    created_at = models.DateTimeField("Criado em", default=timezone.now)
    updated_at = models.DateTimeField("Alterado em", auto_now=True)

    class Meta:
        abstract = True


class UserManager(BaseUserManager):
    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError("The given email must be set")
        #  if not email_is_valid(email): # TODO
            #  raise ValueError("The given email must be valid")
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        Token.objects.create(user=user)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_superuser", False)
        extra_fields.setdefault("is_staff", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_staff", True)
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")
        return self._create_user(email, password, **extra_fields)


class UserModel(UserBase, AbstractBaseUser, PermissionsMixin):
    name = models.CharField("User's name", max_length=100)
    email = models.EmailField(max_length=254, unique=True)
    whatsapp = models.CharField("Whatsapp", max_length=20, blank=True, null=True)
    is_staff = models.BooleanField(
        "staff status",
        default=False,
        help_text="Designates whether the user can log into this admin site.",
    )
    is_active = models.BooleanField(
        "active",
        default=False,
        help_text="Designates whether this user should be treated as active. Unselect this instead of deleting accounts.",
    )
    subscription_status = models.IntegerField(choices=subscription_status, default=1)
    customer_stripe_id = models.CharField(max_length=30, blank=True, null=True)
    subscription_started_at = models.DateTimeField(blank=True, null=True)
    subscription_canceled_at = models.DateTimeField(blank=True, null=True)
    subscription_failed_at = models.DateTimeField(blank=True, null=True)
    lang_for_communication = models.CharField(max_length=5, default="en")

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return f"User: {self.name} "
