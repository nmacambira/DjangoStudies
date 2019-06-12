from django.db import models
from django.contrib.auth.models import AbstractUser, Group
from django.utils import timezone
from django.core.exceptions import ValidationError


from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token

from .utils import create_hash

# Create your models here.


class Employee(AbstractUser):
    ADMIN = 'Admin'
    MANAGER = 'Manager'
    EMPLOYEE = 'Employee'
    CATEGORY_CHOICES = (
        (ADMIN, 'Diretor'),
        (MANAGER, 'Gerente'),
        (EMPLOYEE, 'Funcionário'),
    )
    username = models.CharField(max_length=255, blank=True, null=True)
    email = models.CharField(max_length=255, unique=True, verbose_name='E-mail')
    phone_number = models.CharField(max_length=100, blank=True, null=True, verbose_name='Telefone')
    salary = models.DecimalField(decimal_places=2, max_digits=10, blank=True, null=True, verbose_name='Salário')
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default=EMPLOYEE, verbose_name='Categoria')
    manager = models.ForeignKey('self', blank=True, null=True, on_delete=models.CASCADE, verbose_name='Gerente')
    job = models.ForeignKey('Job', blank=True, null=True, on_delete=models.CASCADE, related_name='employees',
                            verbose_name='Cargo')
    department = models.ForeignKey('Departament', blank=True, null=True, on_delete=models.CASCADE,
                                    related_name='employees',
                                    verbose_name='Departamento')
    device_token = models.CharField(max_length=255, blank=True, null=True, verbose_name='Device Token')
    profile_photo = models.ImageField(blank=True, null=True, upload_to='profile_photos/%Y/%m/%d/',
                                      verbose_name='Foto do usuário')
    # ImageField stores a specif type of file: images (.png, .gif, .jpg)
    # Requires Pillow: pip install Pillow

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        # return "%i " % self.id
        return self.first_name + " " + self.last_name

    def is_manager(self):
        return self.manager is None

    class Meta:
        verbose_name = "Funcionário"
    #     verbose_name_plural = "Funcionários"
        ordering = ['first_name']

    # This code is triggered whenever a new user has been created and saved to the database
    @receiver(post_save, sender=settings.AUTH_USER_MODEL)
    def create_auth_token(sender, instance=None, created=False, **kwargs):
        if created:
            Token.objects.create(user=instance)


class Job(models.Model):
    title = models.CharField(max_length=255, verbose_name='Cargo')
    department = models.ForeignKey('Departament', on_delete=models.CASCADE,
                                    related_name='jobs',
                                    verbose_name='Departamento')
    min_salary = models.DecimalField(decimal_places=2, max_digits=10, blank=True, null=True,
                                     verbose_name='Salário mínimo')
    max_salary = models.DecimalField(decimal_places=2, max_digits=10, blank=True, null=True,
                                     verbose_name='Salário máximo')

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Cargo"
        unique_together = (('title', 'department'),)  # Sets of field names that, taken together, must be unique
        ordering = ['title']


class Departament(models.Model):
    title = models.CharField(max_length=255, unique=True, verbose_name='Departamento')

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Departamento"
        ordering = ['title']


class Project(models.Model):
    IN_PROGRESS = 'in_progress'
    LATE = 'late'
    FINISHED = 'finished'
    SUSPENDED = 'suspended'
    CANCELED = 'canceled'
    STATUS_CHOICES = (
        (IN_PROGRESS, 'Em andamento'),
        (LATE, 'Atrasado'),
        (FINISHED, 'Finalizado'),
        (SUSPENDED, 'Suspenso'),
        (CANCELED, 'Cancelado'),
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=IN_PROGRESS, verbose_name='Situação')
    title = models.CharField(max_length=255, verbose_name='Projeto', unique_for_year='start_date')
    detail = models.TextField(blank=True, null=True, verbose_name='Detalhes')
    file = models.FileField(blank=True, null=True, upload_to='files/%Y/%m/%d/', verbose_name='Arquivo')
    client = models.ForeignKey('Client', on_delete=models.CASCADE, related_name='projects', verbose_name='Cliente')
    department = models.ForeignKey('Departament', on_delete=models.CASCADE, related_name='projects',
                                    verbose_name='Departamento')
    team = models.ManyToManyField('Employee', related_name='projects', verbose_name='Equipe')
    start_date = models.DateField(default=timezone.now, verbose_name='Data de início',
                                  help_text="Por favor, use o seguinte formato: <em>DD/MM/YYYY</em>.")
    end_date = models.DateField(default=timezone.now, verbose_name='Data de término',
                                help_text="Por favor, use o seguinte formato: <em>DD/MM/YYYY</em>.")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Criado em')

    def __str__(self):
        return self.title

    # def clean(self):
    #     if self.start_date > self.end_date:
    #         raise ValidationError('A data de término deve ser maior que a data de início.')
            # raise ValidationError(
            #     _('end_date( %(end_date)s ) must be greater than star_date( %(start_date)s )'),
            #     params={'start_date': self.start_date, 'end_date': self.end_date},
            # )

    class Meta:
        verbose_name = "Projeto"
        # unique_together = (('title', 'client'),)  # Sets of field names that, taken together, must be unique
        ordering = ['title']


class Task(models.Model):
    project = models.ForeignKey('Project', on_delete=models.CASCADE, related_name='tasks', verbose_name='Projeto')
    employee = models.ForeignKey('Employee', on_delete=models.CASCADE, related_name='tasks', verbose_name='Funcionário')
    title = models.CharField(max_length=255, verbose_name='Tarefa')
    detail = models.TextField(blank=True, null=True, verbose_name='Detalhes')
    file = models.FileField(blank=True, null=True, upload_to='files/%Y/%m/%d/', verbose_name='Arquivo')
    URGENT = 0
    HIGH = 1
    NORMAL = 2
    LOW = 3
    PRIORITY_CHOICES = (
        (URGENT, 'Urgente'),
        (HIGH, 'Alta'),
        (NORMAL, 'Normal'),
        (LOW, 'Baixa'),
    )
    priority = models.IntegerField(choices=PRIORITY_CHOICES, default=NORMAL, verbose_name='Prioridade')
    due_date = models.DateField(default=timezone.now, verbose_name='Data limite de conclusão',
                                help_text="Por favor, use o seguinte formato: <em>DD/MM/YYYY</em>")
    CREATED = 'created'
    IN_PROGRESS = 'in_progress'
    ON_HOLD = 'on_hold'
    COMPLETED = 'completed'
    CANCELED = 'canceled'
    STATUS_CHOICES = (
        (CREATED, 'Criada'),
        (IN_PROGRESS, 'Em andamento'),
        (ON_HOLD, 'Com impedimento'),
        (COMPLETED, 'Concluída'),
        (CANCELED, 'Cancelada'),
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=CREATED, verbose_name='Status')
    working_hours = models.DecimalField(decimal_places=2, max_digits=4, blank=True, null=True,
                                        verbose_name='Horas trabalhadas')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Criada em')

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Tarefa"
        ordering = ['priority']


class Client(models.Model):
    name = models.CharField(max_length=255, verbose_name='Cliente')
    email = models.CharField(max_length=255, unique=True, verbose_name='E-mail')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Cliente"
        ordering = ['name']


class LostPassword(models.Model):
    hash = models.CharField(max_length=30, default=create_hash)
    user = models.ForeignKey(Employee, on_delete=models.CASCADE)
    solicitation_date = models.DateTimeField(auto_now_add=True)
    expired = models.BooleanField(default=False)

    def __str__(self):
        return self.user.email