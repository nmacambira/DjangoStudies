from rest_framework import permissions, viewsets, views, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from django.shortcuts import render
from django.core.mail import send_mail
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.models import Group
from django.db.models import Q
from django.db import transaction

from .models import Employee, Task, Project, Departament, Job, Client, LostPassword
from .serializers import SessionUserSerializer, EmployeeSerializer, TaskSerializer, ProjectSerializer, DepartmentSerializer, JobSerializer,\
    ClientSerializer, EditEmployeeSerializer, ChangePasswordSerializer, ContactSerializer, DeviceTokenSerializer
from .permissions import IsTaskOwnerOrReadOnly, IsStaffOrReadOnly


# CustomObtainAuthToken (Login authentication)
class CustomObtainAuthToken(ObtainAuthToken):
    """
    An endpoint for authenticate user.
    """
    def post(self, request, *args, **kwargs):
        response = super(CustomObtainAuthToken, self).post(request, *args, **kwargs)
        token = Token.objects.get(key=response.data['token'])
        user = Employee.objects.get(id=token.user_id)
        user_data = SessionUserSerializer(user).data

        # if token:
        #     token.delete()
        # token, create = Token.objects.get_or_create(user=user)
        return Response({
            'token': 'Token ' + token.key,
            'user': user_data
        })


# ModelViewSet
class EmployeeViewSet(viewsets.ReadOnlyModelViewSet):
    """
    This viewset (ReadOnlyModelViewSet) automatically provides 'list' and 'retrieve' actions.
    """
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer

    def get_queryset(self):
        """
        Optionally restricts the returned employees of a given manager,
        by filtering against the `manager_id` query parameter in the URL.
        """
        queryset = Employee.objects.all()
        manager_id = self.request.query_params.get('manager_id', None)
        print(manager_id)
        if manager_id is not None:
            queryset = queryset.filter(manager__id=manager_id)
        else:
            queryset = queryset.filter(id=self.request.user.id)
        return queryset


class ProjectViewSet(viewsets.ModelViewSet):
    """
    This viewset (ModelViewSet) automatically provides 'list', 'create', 'retrieve', 'update' and 'destroy' actions.
    """
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = (permissions.IsAuthenticated, IsStaffOrReadOnly)

    def get_queryset(self):
        """
        Restricts the returned projects,
        by filtering against the user.
        """
        queryset = Project.objects.all()
        if self.request.user.is_staff:
            # SELECT * from project WHERE tem__id = request.user.id OR team__manager = request.user
            return queryset.filter(Q(team__id=self.request.user.id) | Q(team__manager=self.request.user)).distinct()
            # return queryset.filter(team__manager=self.request.user).distinct()

        return queryset.filter(team__id=self.request.user.id)

    def perform_create(self, serializer):
        if self.request.user.is_staff:
            team = serializer.validated_data['team']
            user = self.request.user
            if user not in team:
                team.append(user)
            serializer.save(department=self.request.user.department, team=team)
        else:
            serializer.save()


class TaskViewSet(viewsets.ModelViewSet):
    """
    This viewset (ModelViewSet) automatically provides 'list', 'create', 'retrieve', 'update' and 'destroy' actions.
    """
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = (permissions.IsAuthenticated, IsTaskOwnerOrReadOnly,)

    def get_queryset(self):
        """
        Optionally restricts the returned tasks of a given project,
        by filtering against the 'project_id' query parameter in the URL.
        """
        queryset = Task.objects.all()
        # project_id = self.request.query_params.get('project_id', None)
        # if project_id is not None:
        #     queryset = queryset.filter(project_id=project_id)
        #     if self.request.user.is_staff:
        #         # SELECT * from task WHERE employee = request.user OR employee__manager = request.user
        #         return queryset.filter(Q(employee=self.request.user) | Q(employee__manager=self.request.user))

        if self.request.user.is_staff:
            # SELECT * from task WHERE employee = request.user OR employee__manager = request.user
            return queryset.filter(Q(employee=self.request.user) | Q(employee__manager=self.request.user))

        return queryset.filter(employee=self.request.user)

    def perform_create(self, serializer):
        if self.request.user.category == 'Employee':
            serializer.save(employee=self.request.user)
        else:
            serializer.save()


class DepartmentViewSet(viewsets.ReadOnlyModelViewSet):
    """
       This viewset (ReadOnlyModelViewSet) automatically provides 'list' and 'retrieve' actions.
       """
    queryset = Departament.objects.all()
    serializer_class = DepartmentSerializer


class JobViewSet(viewsets.ReadOnlyModelViewSet):
    """
       This viewset (ReadOnlyModelViewSet) automatically provides 'list' and 'retrieve' actions.
       """
    queryset = Job.objects.all()
    serializer_class = JobSerializer


class ClientViewSet(viewsets.ReadOnlyModelViewSet):
    """
       This viewset (ReadOnlyModelViewSet) automatically provides 'list' and 'retrieve' actions.
       """
    queryset = Client.objects.all()
    serializer_class = ClientSerializer


class EmployeeListView(views.APIView):
    """
    List all user's from a manager, or create a new user.
    """
    serializer_class = EmployeeSerializer
    model = Employee

    def get(self, request, format=None):
        employees = Employee.objects.all()
        manager_id = request.user.id
        # SELECT * from employee WHERE id = request.user.id OR manager = request.user
        # employees = employees.filter(Q(id=request.user.id) | Q(manager__id=manager_id))
        employees = employees.filter(manager__id=manager_id)
        serializer = EmployeeSerializer(employees, many=True)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        if request.user.category == 'Employee':
            return Response({'detail': 'Você não tem permissão para executar essa ação.'}, status.HTTP_401_UNAUTHORIZED)

        serializer = EmployeeSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            manager_id = serializer.data['manager_id']
            job_id = serializer.data['job_id']

            user = Employee(email=serializer.data['email'], first_name=serializer.data['first_name'],
                            last_name=serializer.data['last_name'], phone_number=serializer.data['phone_number'],
                            profile_photo=serializer.data['profile_photo'], category='Employee')

            try:
                manager = Employee.objects.get(id=manager_id)
                user.manager = manager
                user.department = manager.department

            except Employee.DoesNotExist:
                return Response(
                    {'detail': 'Gerente com id "{}" não encontrado.'.format(manager_id)}, status.HTTP_400_BAD_REQUEST)

            try:
                job = Job.objects.get(id=job_id)
                user.job = job

            except Job.DoesNotExist:
                return Response(
                    {'detail': 'Cargo com id "{}" não encontrado.'.format(job_id)}, status.HTTP_400_BAD_REQUEST)

            user.set_password(request.data['password'])
            user.save()

            group = Group.objects.get(name='Funcionários')
            user.groups.add(group)

            # return Response(serializer.data, status.HTTP_201_CREATED)
            user_data = EmployeeSerializer(user).data
            return Response(user_data, status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)


class EmployeeDetailView(views.APIView):
    """
    Retrieve or update a user instance.
    """
    serializer_class = EmployeeSerializer
    model = Employee

    def get_object(self, pk):
        try:
            return Employee.objects.get(pk=pk)
        except Employee.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def get(self, request, pk, format=None):
        employee = self.get_object(pk)

        if employee == request.user or employee.manager == request.user:
            serializer = EmployeeSerializer(employee)
            return Response(serializer.data)

        return Response({'detail': 'Você não tem permissão para executar essa ação.'}, status.HTTP_401_UNAUTHORIZED)

    def patch(self, request, pk, format=None):
        employee = self.get_object(pk)

        if employee != request.user:
            return Response({'detail': 'Você não tem permissão para executar essa ação.'}, status.HTTP_401_UNAUTHORIZED)

        if not employee.email == request.data.get('email') and Employee.objects.filter(email=request.data.get('email')):
            return Response({'detail': 'E-mail já cadastrado no sistema.'}, status.HTTP_400_BAD_REQUEST)

        serializer = EditEmployeeSerializer(employee, data=request.data, partial=True)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data)
            # employee_data = EmployeeSerializer(employee).data
            # return Response(employee_data)
        return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)


# Change password
class ChangePasswordView(views.APIView):
    """
    An endpoint for changing user's password.
    """
    serializer_class = ChangePasswordSerializer
    model = Employee

    def get_object(self, queryset=None):
        return self.request.user

    def put(self, request, *args, **kwargs):
        self.object = self.get_object()
        serializer = ChangePasswordSerializer(data=request.data)

        if serializer.is_valid(raise_exception=True):
            # Check old password
            old_password = serializer.data.get("old_password")
            if not self.object.check_password(old_password):
                return Response({"old_password": ["Senha incorreta."]}, status.HTTP_400_BAD_REQUEST)
            # set_password also hashes the password that the user will get
            new_password = serializer.data.get("new_password")
            self.object.set_password(new_password)
            self.object.save()

            return Response({"Success": True}, status.HTTP_200_OK)

        return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)


# Recover password
class RecoverPasswordView(views.APIView):
    """
    An endpoint for recover user's password.
    """
    permission_classes = (permissions.AllowAny, )

    def post(self, request, *args, **kwargs):
        app_name = 'Empresa Top 10 - Tasks'
        app_server_email = 'naoresponda@empresatop10.com.br'
        email = request.data.get('email', '').lower()

        try:
            user = Employee.objects.get(email=email)
        except Employee.DoesNotExist:
            return Response({'detail': 'Usuário com email "{}" não encontrado.'.format(email)},
                            status.HTTP_400_BAD_REQUEST)

        with transaction.atomic():
            lost_password = LostPassword.objects.create(user=user)

            body_mail = '''
                        <h2>{app_name}</h2>
                        <div>Uma alteração de senha para o email {email} foi solicitada. 
                            Clique no link pra alterar a senha: <a href="{link}">{link}</a>
                        </div><br>
                        <a href="https://empresatop10.com.br/">Empresa Top 10</a>
                        '''.format(app_name=app_name,
                                   email=user.email,
                                   link='http://localhost:8000/api/v1/reset-password/' + lost_password.hash)
                                   # link='https://empresatop10.com.br/api/v1/reset-password/' + lost_password.hash)
            try:
                send_mail(
                    '{app_name} - Solicitação de alteração de senha'.format(app_name=app_name),
                    '',
                    '{app_server_email}'.format(app_server_email=app_server_email),
                    [user.email],
                    fail_silently=False,
                    html_message=body_mail,
                )

            except Exception as e:
                return Response({"email_sent": False, "message:": repr(e)},
                                status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({'detail': 'Verifique seu e-mail.'}, status.HTTP_200_OK)


# Reset password
@api_view(['GET', 'POST'])
@permission_classes([permissions.AllowAny])
def reset_password(request, hash, *args, **kwargs):
    lost_password = LostPassword.objects.get(hash=hash)
    error_message = None
    success = None

    if request.method == 'POST':
        if lost_password:
            new_password = request.data.get('new_password')
            confirm_new_password = request.data.get('confirm_new_password')
            if new_password and (new_password == confirm_new_password):
                if len(new_password) >= 8:
                    try:
                        lost_password.user.set_password(new_password)
                        lost_password.user.save()
                        update_session_auth_hash(request, lost_password.user)
                        success = True
                    except Employee.DoesNotExist:
                        error_message ='Usuário não encontrado.'
                        success = False
                else:
                    error_message = 'A senha deve ter no mínimo 8 caracteres'
                    success = False
            else:
                error_message = 'As senhas devem ser iguais'
                success = False
        else:
            error_message = 'Identificador inexistente'
            success = False

    context = {
        'lost_password': lost_password,
        'error_message': error_message,
        'success': success,
    }

    return render(request, 'manager/reset_password.html', context)


# Device token
class PushNotificationDeviceTokenView(views.APIView):
    """
    An endpoint for save user's device token.
    """
    serializer_class = DeviceTokenSerializer
    model = Employee

    def get_object(self, queryset=None):
        return self.request.user

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        serializer = DeviceTokenSerializer(data=request.data)

        if serializer.is_valid(raise_exception=True):
            device_token = serializer.data.get('token')
            self.object.device_token = device_token
            self.object.save()

            return Response({'detail': 'Token enviado com sucesso'}, status.HTTP_200_OK)

        return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)


# Contact
class ContactView(views.APIView):
    """
    An endpoint for sending contact message.
    """

    def post(self, request, *args, **kwargs):
        serializer = ContactSerializer(data=request.data)
        app_name = 'Empresa Top 10 - Tasks'
        app_server_email = 'naoresponda@empresatop10.com.br'
        app_contact_email = 'contato@empresatop10.com.br'

        if serializer.is_valid(raise_exception=True):
            name = request.data.get('name')
            subject = request.data.get('subject')
            message = request.data.get('message')
            sender_email = request.data.get('sender_email')

            user = Employee.objects.get(email=sender_email)

            body_mail = '''<h2>{app_name}</h2>
                            <h4>Segue abaixo a mensagem do usuário</h4>
                            <div>
                            <p><b>Nome:</b> {name} ({sender_email})</p>                            
                            <p><b>Assunto:</b> {subject}</p>
                            <p><b>Mensagem:</b> {message}</p>
                            </div>                    
                            '''.format(app_name=app_name,
                                       name=name,
                                       sender_email=user.email,
                                       subject=subject,
                                       message=message)
            try:
                send_mail(
                    '{app_name} - Mensagem do usuário'.format(app_name=app_name),
                    '',
                    '{app_server_email}'.format(app_server_email=app_server_email),
                    ['{app_contact_email}'.format(app_contact_email=app_contact_email)],
                    fail_silently=False,
                    html_message=body_mail,
                )

            except Exception as e:
                return Response({"email_sent": False, "message:": repr(e)}, status.HTTP_500_INTERNAL_SERVER_ERROR)

            return Response({'detail': 'Mensagem enviada com sucesso'}, status.HTTP_200_OK)

        return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)
