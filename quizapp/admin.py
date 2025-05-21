from django.contrib import admin
from .models import Topic, Question, QuizAttempt, UserResponse, Quiz, Leaderboard
# Register your models her
from django import forms

class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Remove the ChoiceField override


class QuestionAdmin(admin.ModelAdmin):
    form = QuestionForm

admin.site.register(Question, QuestionAdmin)

admin.site.register(Quiz)
admin.site.register(Topic)
admin.site.register(QuizAttempt)
admin.site.register(UserResponse)
admin.site.register(Leaderboard)