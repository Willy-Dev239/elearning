from django.contrib import admin
from .models import Attempt, Choice, Question, Quiz

admin.site.register(Quiz)
admin.site.register(Question)
admin.site.register(Choice)
admin.site.register(Attempt)
