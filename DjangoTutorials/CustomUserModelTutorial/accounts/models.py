from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager


# Create your models here.

# Para full_name não ser mais um campo obrigatório,
# 1) coloque full_name=None, nas chamados dos metodos
# 2) retire a mensagem de erro
# 3) Nos methods create_staffuser e create_superuser
# faça  full_name=full_name,
# 4) Remova full_name de REQUIRED_FIELDS


class UserManager(BaseUserManager):
    def create_user(self, email, full_name, password=None, is_active=True, is_staff=False, is_admin=False ):
        """
        Creates and saves a User with the given email and password.
        """
        if not email:
            raise ValueError('Users must have an email address')

        if not password:
            raise ValueError('User must have a password')

        if not full_name:
            raise ValueError("Users must have fullname")

        user_obj = self.model(
            email=self.normalize_email(email),
            full_name=full_name,
        )
        user_obj.set_password(password)  # change user password
        user_obj.staff = is_staff
        user_obj.admin = is_admin
        user_obj.active = is_active
        user_obj.save(using=self._db)
        return user_obj

    def create_staffuser(self, email, full_name, password):
        """
        Creates and saves a staff user with the given email and password.
        """
        user = self.create_user(
            email,
            full_name,
            password=password,
            is_staff=True,
        )
        return user

    def create_superuser(self, email, full_name, password):
        """
        Creates and saves a superuser with the given email and password.
        """
        user = self.create_user(
            email,
            full_name,
            password=password,
            is_staff=True,
            is_admin=True,
        )
        return user


class User(AbstractBaseUser):
    email = models.EmailField(
        verbose_name='email address',
        max_length=255,
        unique=True,
    )
    full_name = models.CharField(max_length=255, blank=True, null=True)
    active = models.BooleanField(default=True)  # can log in
    staff = models.BooleanField(default=False)  # a admin user; non super-user
    admin = models.BooleanField(default=False)  # a superuser
    timestamp = models.DateTimeField(auto_now_add=True)
    # notice the absence of a "Password field", that's built in.

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['full_name']  # ['full_name']
    #  Email & Password are required by default.
    # This REQUIRED_FIELDS are only used when you type 'python manage.py createsuperuser

    objects = UserManager() # hook in the New Manager to our Model

    def __str__(self):  # __unicode__ on Python 2
        return self.email

    def get_full_name(self):
        # The user is identified by their email address
        if self.full_name:
            return self.full_name

        return self.email

    def get_short_name(self):
        # The user is identified by their email address
        return self.email

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return True

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True

    @property
    def is_staff(self):
        "Is the user a member of staff?"
        return self.staff

    @property
    def is_admin(self):
        "Is the user a admin member?"
        return self.admin

    @property
    def is_active(self):
        "Is the user active?"
        return self.active


# class Profile(models.Model):
    # extends extra data
#     user = models.OneToOneField(User, blank=True, null=True, on_delete=models.CASCADE, related_name='profile')
#     user = models.OneToOneField(User, blank=True, null=True)
#     full_name = models.CharField(max_length=255, blank=True, null=True)
#
#     def __str__(self):
#         return 'Profile of user: {}'.format(self.user.email)



    # Using related_name you can access a user's profile easily,
    # for example: request.user
    #
    # request.user.profile.full_name
    # request.user.profile.gender