from django.contrib import admin
from .models import Profession, Step, StepItem, UserProgress

admin.site.register(Profession)
admin.site.register(Step)
admin.site.register(StepItem)
admin.site.register(UserProgress)
