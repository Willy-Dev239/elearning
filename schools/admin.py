from django.contrib import admin
from .models import Classroom, Enrollment, School

admin.site.register(School)
admin.site.register(Classroom)
admin.site.register(Enrollment)
