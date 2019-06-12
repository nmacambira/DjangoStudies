from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group
from django.utils.html import format_html
from django.db.models import Q

from .models import Employee, Job, Departament, Client, Project, Task


# Inline forms

class EmployeeInline(admin.TabularInline):
    model = Employee
    extra = 0
    can_delete = False
    fields = ('first_name', 'last_name', 'category', 'job', )
    readonly_fields = ['first_name', 'last_name', 'job', 'category', ]

    def has_add_permission(self, request):
        return False


class ProjectInline(admin.TabularInline):
    model = Project
    extra = 0
    can_delete = False
    fields = ('title', 'team', 'start_date', 'end_date', 'client')
    readonly_fields = ['title', 'team', 'start_date', 'end_date', 'client', ]

    def has_add_permission(self, request):
        return False


class TaskInline(admin.TabularInline):
    model = Task
    extra = 0
    can_delete = False
    fields = ('employee', 'title', 'priority', 'due_date', 'status', 'working_hours')
    readonly_fields = ['employee', 'title', 'priority', 'due_date', 'status', 'working_hours', ]

    def has_add_permission(self, request):
        return False


class TeamInline(admin.TabularInline):
    model = Project.team.through  # .through: display many-to-many relations
    extra = 0
    can_delete = False
    readonly_fields = ['project', ]

    def has_add_permission(self, request):
        return False


# Models

class EmployeeAdmin(UserAdmin):
    list_display = ('full_name', 'email', 'manager', 'department', 'group', 'admin', 'is_active')
    list_display_links = ('full_name', 'email',)
    list_filter = ('is_active', 'job', )
    search_fields = ('email', 'full_name',)
    ordering = ('first_name',)
    readonly_fields = []
    empty_value_display = 'Nenhum'
    inlines = [TeamInline, ]
    # radio_fields = {"manager": admin.VERTICAL}

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Informações pessoais', {'fields': ('first_name', 'last_name', 'phone_number', 'category', 'profile_photo')}),
        ('Informações empregatícias', {'fields': ('department', 'manager', 'job', 'salary',)}),
        ('Tipo de usuário do sistema', {'fields': ('is_superuser', 'is_staff',)}),
        ('Permissões', {'fields': ('groups',)}),
        ('Status', {'fields': ('is_active',)}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2',)}
         ),
        ('Informações pessoais', {'fields': ('first_name', 'last_name', 'phone_number', 'category', 'profile_photo')}),
        ('Informações empregatícias', {'fields': ('department', 'manager', 'job', 'salary',)}),
        ('Tipo de usuário do sistema', {'fields': ('is_superuser', 'is_staff',)}),
        ('Permissões', {'fields': ('groups',)}),
        ('Status', {'fields': ('is_active',)}),
    )

    admin_fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Informações pessoais', {'fields': ('first_name', 'last_name', 'phone_number', 'category', 'profile_photo')}),
        ('Informações empregatícias', {'fields': ('department', 'manager', 'job', 'salary',)}),
        ('Tipo de usuário do sistema', {'fields': ('is_staff',)}),
        ('Permissões', {'fields': ('groups',)}),
        ('Status', {'fields': ('is_active',)}),
    )

    admin_add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2',)}
         ),
        ('Informações pessoais', {'fields': ('first_name', 'last_name', 'phone_number', 'category', 'profile_photo')}),
        ('Informações empregatícias', {'fields': ('department', 'manager', 'job', 'salary',)}),
        ('Tipo de usuário do sistema', {'fields': ('is_staff',)}),
        ('Permissões', {'fields': ('groups',)}),
    )

    manager_fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Informações pessoais', {'fields': ('first_name', 'last_name', 'phone_number', 'category', 'profile_photo')}),
        ('Informações empregatícias', {'fields': ('department', 'manager', 'job', 'salary',)}),
        ('Permissões', {'fields': ('groups',)}),
        ('Status', {'fields': ('is_active',)}),
    )

    manager_add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2',)}
         ),
        ('Informações pessoais', {'fields': ('first_name', 'last_name', 'phone_number', 'category', 'profile_photo')}),
        ('Informações empregatícias', {'fields': ('job', 'salary',)}),
    )

    class Meta:
        model = Employee
        fields = '__all__'

    # Use user's methods
    def full_name(self, user):
        return user.get_full_name()
    full_name.short_description = 'Nome completo'

    # Display user's groups
    def group(self, user):
        groups = []
        for group in user.groups.all():
            groups.append(group.name)
        return ' '.join(groups)
    group.short_description = 'Grupo de permissões'

    # Rename property on list_display
    def admin(self, obj):
        return obj.is_superuser
    admin.short_description = 'Administrador\n do sistema'
    admin.boolean = True

    def staff(self, obj):
        return obj.is_staff
    staff.short_description = 'Gerente\n do sistema'
    staff.boolean = True

    # Display different list_display
    def changelist_view(self, request, extra_content=None):
        if not request.user.is_superuser:
            self.list_display = ('full_name', 'email', 'date_joined', 'is_active',)
        return super(EmployeeAdmin, self).changelist_view(request, extra_content)

    # Display attributes of ForeignKey fields in list_display
    def job_max_salary(self, obj):
        if obj.job:
            return obj.job.max_salary
    job_max_salary.short_description = 'Salário limite'

    # Change fieldsets by a condition
    def get_fieldsets(self, request, obj=None):
        if request.user.is_superuser:
            if obj is None:
                return self.add_fieldsets
            return self.fieldsets
        else:
            if request.user.category == 'Admin':
                if obj is None:
                    return self.admin_add_fieldsets
                return self.admin_fieldsets
            else:
                if obj is None:
                    return self.manager_add_fieldsets
                return self.manager_fieldsets

    # Rename property on form
    def get_form(self, request, obj, **kwargs):
        form = super(EmployeeAdmin, self).get_form(request, obj, **kwargs)
        if request.user.is_superuser:
            form.base_fields['is_superuser'].label = 'Administrador do sistema'
            form.base_fields['is_staff'].label = 'Gerente do sistema'

        else:
            if request.user.category == 'Admin':
                form.base_fields['is_staff'].label = 'Gerente do sistema'
                form.base_fields['category'].choices = (('Manager', 'Gerente'), ('Employee', 'Funcionário'),)
            if request.user.category == 'Manager':
                form.base_fields['category'].choices = (('Employee', 'Funcionário'),)
        return form

    # Add extra fieldsets
    # def get_form(self, request, obj, **kwargs):
    #     form = super(EmployeeAdmin, self).get_form(request, obj, **kwargs)
    #     self.fieldsets = self.regular_fieldsets
    #     if obj.task_finished:
    #         self.fieldsets = self.regular_fieldsets + self.extra_fieldsets
    #     return form

    # Filter foreignkey field 'manager' by is_staff
    def render_change_form(self, request, context, *args, **kwargs):
        if request.user.is_superuser:
            context['adminform'].form.fields['manager'].queryset = Employee.objects.filter(is_staff=True)

        return super(EmployeeAdmin, self).render_change_form(request, context, *args, **kwargs)

    # override foreignkey formfield's
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if not request.user.is_superuser:
            # Set default value for user ForeignKey with Django admin
            if db_field.name == 'department':
                kwargs['initial'] = request.user.department.id

            if db_field.name == 'manager':
                kwargs['initial'] = request.user.id

            # Filter foreignkey field 'department' by request.user.department.id
            if db_field.name == 'department':
                kwargs['queryset'] = Departament.objects.filter(id=request.user.department.id)

            # Filter foreignkey field 'manager' by request.user.id
            if db_field.name == 'manager':
                if request.user.category == 'Admin':
                    kwargs['queryset'] = Employee.objects.filter(category='Manager')
                else:
                    kwargs['queryset'] = Employee.objects.filter(id=request.user.id)

            # Filter foreignkey field 'job' by request.user.department and order by title
            if db_field.name == 'job':
                kwargs['queryset'] = Job.objects.filter(department=request.user.department)

        return super(EmployeeAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)

    # Set fields to readonly
    def get_readonly_fields(self, request, obj=None):
        if not request.user.is_superuser and request.user.category == 'Manager':
            return ['manager', 'department', 'groups', ]
        else:
            return super(EmployeeAdmin, self).get_readonly_fields(request, obj)

    # Filter employees by manager
    def get_queryset(self, request):
        employees = super(EmployeeAdmin, self).get_queryset(request)
        if not request.user.is_superuser:
            if request.user.category == 'Admin':
                return employees.filter(department=request.user.department)
            else:
                # SELECT * from employee WHERE id = request.user.id OR manager = request.user
                # result = employees.filter(Q(id=request.user.id) | Q(manager=request.user))
                manager = employees.filter(id=request.user.id)
                users = employees.filter(manager=request.user)
                result = manager | users
                return result
        return employees

    # Coloring category
    def category_colored(self, obj):
        color = '33cc33'
        if obj.category == 'Manager':
            color = '0066cc'
        elif obj.category == 'Admin':
            color = 'ff0000'
        return format_html(
            '<span style="color: #{};">{}</span>',
            color,
            obj.category,
        )
    category_colored.admin_order_field = 'category'
    category_colored.short_description = 'Categoria colorida'

    # Save model object
    def save_model(self, request, obj, form, change):
        if not request.user.is_superuser and request.user.category == 'Manager' and not change:
            obj.manager = request.user
            obj.department = request.user.department
            super().save_model(request, obj, form, change)

            group = Group.objects.get(name='Funcionários')
            user = Employee.objects.get(email=obj.email)
            user.groups.add(group)
            # group.user_set.add(user)
        else:
            super().save_model(request, obj, form, change)


admin.site.register(Employee, EmployeeAdmin)


class DepartamentAdmin(admin.ModelAdmin):
    inlines = [EmployeeInline, ProjectInline, ]


admin.site.register(Departament, DepartamentAdmin)


class ClientAdmin(admin.ModelAdmin):
    inlines = [ProjectInline, ]


admin.site.register(Client, ClientAdmin)


class ProjectAdmin(admin.ModelAdmin):
    list_display = ('title_colored', 'start_date', 'end_date', 'client', 'status',)
    list_editable = ('status',)
    list_filter = ('status',)
    search_fields = ('title', 'client__name', )
    inlines = [TaskInline, ]
    # exclude = ('team',)

    def title_colored(self, obj):
        color = '33cc33'
        if obj.status == 'late':
            color = 'ffcc00'
        elif obj.status == 'finished':
            color = '0066cc'
        elif obj.status == 'suspended':
            color = '999999'
        elif obj.status == 'canceled':
            color = 'ff0000'
        return format_html(
            '<span style="color: #{};">{}</span>',
            color,
            obj.title,
        )
    title_colored.admin_order_field = 'title_colored'
    title_colored.short_description = 'Projeto'

    # def render_change_form(self, request, context, *args, **kwargs):
    #     department = self.form.cleaned_data.get('department')
    #     context['adminform'].form.fields['department'].queryset = Employee.objects.filter(department=department)
    #
    #     return super(ProjectAdmin, self).render_change_form(request, context, *args, **kwargs)

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name == 'team':
            if not request.user.is_superuser:
                kwargs['queryset'] = Employee.objects.filter(department=request.user.department)
            # else:
            #     department = self.fields['department']
            #     print(self.fields)
            #     if department:
            #         kwargs['queryset'] = Employee.objects.filter(department=department)
        return super(ProjectAdmin, self).formfield_for_manytomany(db_field, request, **kwargs)

    # Set fields to readonly (override readonly_fields = ('created_at', 'department', ))
    def get_readonly_fields(self, request, obj=None):
        if request.user.is_superuser:
            return ['created_at', ]
        else:
            return ['created_at', 'department', ]

    def get_queryset(self, request):
        projects = super(ProjectAdmin, self).get_queryset(request)
        if not request.user.is_superuser:
            if request.user.category == 'Admin':
                return projects.filter(department=request.user.department)
            else:
                return projects.filter(team__manager=request.user).distinct()
        return projects

    def save_model(self, request, obj, form, change):
        if not request.user.is_superuser and not change:
            obj.department = request.user.department
            super().save_model(request, obj, form, change)
        else:
            super().save_model(request, obj, form, change)


admin.site.register(Project, ProjectAdmin)


class TaskAdmin(admin.ModelAdmin):
    list_display = ('title_colored', 'project', 'priority', 'employee', 'due_date', 'status', 'working_hours',)
    actions = []
    list_filter = ('project__title', 'priority', 'status', )
    search_fields = ('title', 'employee__first_name', 'employee__last_name', )
    # ordering = ('priority',)
    readonly_fields = ['created_at']

    def get_project(self, obj):
        return obj.project

    # override foreignkey formfield's
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if not request.user.is_superuser:
            # Filter foreignkey field 'employee__manager' by request.user
            if db_field.name == 'employee':
                # SELECT * from employee WHERE id = request.user.id OR manager = request.user
                kwargs['queryset'] = Employee.objects.filter(Q(id=request.user.id) | Q(manager=request.user))

        return super(TaskAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)

    # Set fields to readonly (override readonly_fields = ['created_at'])
    # def get_readonly_fields(self, request, obj=None):
    #     if obj is None:  # creating obj
    #         return super(TaskAdmin, self).get_readonly_fields(request, obj)
    #     else:  # editing obj
    #         return ['project', 'employee', 'title', 'due_date', ]

    # Filter queryset
    def get_queryset(self, request):
        tasks = super(TaskAdmin, self).get_queryset(request)
        if not request.user.is_superuser:
            # SELECT * from task WHERE iemployee = request.user OR employee__manager = request.user
            return tasks.filter(Q(employee=request.user) | Q(employee__manager=request.user))
        return tasks

    # Coloring category
    def title_colored(self, obj):
        color = 'DB4622'
        if obj.status == 'on_hold':
            color = 'F98237'
        elif obj.status == 'completed':
            color = '30BBF7'
        elif obj.status == 'created':
            color = 'DB4622'
        elif obj.status == 'canceled':
            color = 'C6C2C2'
        elif obj.status == 'in_progress':
            color = '4DE65D'
        return format_html(
            '<span style="color: #{};">{}</span>',
            color,
            obj.title,
        )
    title_colored.admin_order_field = 'title_colored'
    title_colored.short_description = 'Tarefa'


admin.site.register(Task, TaskAdmin)


class JobAdmin(admin.ModelAdmin):
    list_display = ('title', 'department', )
    list_filter = ('department', )


admin.site.register(Job, JobAdmin)


admin.site.site_header = 'Empresa top 10'
admin.site.site_title = 'Top 10'
admin.site.index_title = 'Admin'
# admin.site.site_url = 'https://www.djangoproject.com'

