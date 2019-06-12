from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password

from .models import Employee, Departament, Task, Project, Job, Client


class TaskSerializer(serializers.ModelSerializer):
    project_id = serializers.PrimaryKeyRelatedField(queryset=Project.objects.all(), source='project')
    project_title = serializers.ReadOnlyField(source='project.title')
    employee_id = serializers.PrimaryKeyRelatedField(queryset=Employee.objects.all(), source='employee',)

    class Meta:
        model = Task
        fields = ('id', 'project_id', 'project_title', 'employee_id', 'title', 'detail', 'file', 'priority', 'due_date',
                  'status', 'working_hours', 'created_at',)


class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Departament
        fields = ('id', 'title')


class JobSerializer(serializers.ModelSerializer):

    class Meta:
        model = Job
        fields = ('id', 'title')


class EmployeeSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(max_length=30, allow_blank=False)
    last_name = serializers.CharField(max_length=150, allow_blank=False)
    department_title = serializers.ReadOnlyField(source='department.title')
    department_id = serializers.PrimaryKeyRelatedField(queryset=Departament.objects.all())
    # manager_full_name = serializers.ReadOnlyField(source='manager.get_full_name')
    manager_id = serializers.PrimaryKeyRelatedField(queryset=Employee.objects.all())
    # job_title = serializers.ReadOnlyField(source='job.title')
    job_id = serializers.PrimaryKeyRelatedField(queryset=Job.objects.all())
    job = JobSerializer(read_only=True)
    # projects = serializers.PrimaryKeyRelatedField(many=True, queryset=Project.objects.all())
    # tasks = TaskSerializer(many=True, read_only=True)

    class Meta:
        model = Employee
        fields = ('id', 'email', 'first_name', 'last_name', 'phone_number', 'profile_photo', 'category',
                  'department_id', 'department_title', 'job_id', 'job', 'manager_id', )


class SessionUserSerializer(serializers.ModelSerializer):
    department_title = serializers.ReadOnlyField(source='department.title')
    department_id = serializers.PrimaryKeyRelatedField(queryset=Departament.objects.all())
    manager_id = serializers.PrimaryKeyRelatedField(queryset=Employee.objects.all())
    job_id = serializers.PrimaryKeyRelatedField(queryset=Job.objects.all())
    job = JobSerializer(read_only=True)
    manager = EmployeeSerializer(read_only=True)

    class Meta:
        model = Employee
        fields = ('id', 'email', 'first_name', 'last_name', 'phone_number', 'profile_photo', 'category',
                  'department_id', 'department_title', 'job_id', 'job', 'manager_id', 'manager', )


class ClientSerializer(serializers.ModelSerializer):
    # projects = serializers.HyperlinkedRelatedField(many=True, read_only=True, view_name='project-detail')

    class Meta:
        model = Client
        # fields = ('id', 'name', 'email', 'projects')
        fields = ('id', 'name', 'email')


class ProjectSerializer(serializers.ModelSerializer):
    client_id = serializers.PrimaryKeyRelatedField(queryset=Client.objects.all(), source='client',)
    client = ClientSerializer(read_only=True)
    department_id = serializers.PrimaryKeyRelatedField(queryset=Departament.objects.all(), source='department',)
    team_id = serializers.PrimaryKeyRelatedField(many=True, queryset=Employee.objects.all(), source='team', write_only=True)
    team = EmployeeSerializer(many=True, read_only=True)

    class Meta:
        model = Project
        fields = ('id', 'status', 'title', 'detail', 'file', 'client_id', 'client', 'department_id',
                  'team_id', 'start_date', 'end_date', 'created_at', 'team', )


class EditEmployeeSerializer(serializers.ModelSerializer):
    """
    Serializer for edit employee endpoint.
    """
    email = serializers.EmailField(max_length=255, allow_blank=False)
    first_name = serializers.CharField(max_length=30, allow_blank=False)
    last_name = serializers.CharField(max_length=150, allow_blank=False)
    phone_number = serializers.CharField(max_length=100, allow_blank=False)

    class Meta:
        model = Employee
        fields = ('id', 'email', 'first_name', 'last_name', 'phone_number', 'profile_photo',)


class ChangePasswordSerializer(serializers.Serializer):
    """
    Serializer for password change endpoint.
    """
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)

    def validate_new_password(self, value):
        validate_password(value)
        return value


class DeviceTokenSerializer(serializers.Serializer):
    """
    Serializer for device-token endpoint.
    """
    token = serializers.CharField(required=True)
    type = serializers.IntegerField(required=True)


class ContactSerializer(serializers.Serializer):
    """
    Serializer for contact endpoint.
    """
    name = serializers.CharField(required=True)
    subject = serializers.CharField(required=True)
    message = serializers.CharField(required=True)
    sender_email = serializers.CharField(required=True)