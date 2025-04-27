from django.contrib import admin
from .models import ChatHistory, ChatSession

# Register your models here.
admin.site.register(ChatHistory)
admin.site.register(ChatSession)