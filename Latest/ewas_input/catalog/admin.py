from django.contrib import admin
from .models import Study, Analysis, Participants, Results

admin.site.register(Study)
admin.site.register(Analysis)
admin.site.register(Participants)
admin.site.register(Results)
