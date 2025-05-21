from django.db import models
from django.contrib.auth.models import User

class Topic(models.Model):
    topic_id = models.AutoField(primary_key=True)
    topic_name = models.CharField(max_length=255, unique=True)
    
    class Meta:
        verbose_name = "Topic"
        verbose_name_plural = "Topics"

    def __str__(self):
        return self.topic_name
class Quiz(models.Model):
    quiz_id = models.AutoField(primary_key=True)
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name="quizzes")
    description = models.TextField(null=True, blank=True)  # Added description field
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Quiz on {self.topic.topic_name}"

class Question(models.Model):
    question_id = models.AutoField(primary_key=True)
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name="questions")
    question_text = models.TextField()
    option_a = models.CharField(max_length=255)
    option_b = models.CharField(max_length=255)
    option_c = models.CharField(max_length=255)
    option_d = models.CharField(max_length=255)

    correct_answer = models.CharField(max_length=255, null=True, blank=True)

    def get_answer_choices(self):
        return [
            (self.option_a, self.option_a),
            (self.option_b, self.option_b),
            (self.option_c, self.option_c),
            (self.option_d, self.option_d),
        ]

    def save(self, *args, **kwargs):
        if self.correct_answer:
            valid_options = {self.option_a, self.option_b, self.option_c, self.option_d}
            if self.correct_answer not in valid_options:
                raise ValueError("Correct answer must be one of the given options.")
        
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Q{self.question_id}: {self.question_text[:50]}..."


class QuizAttempt(models.Model):
    attempt_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE)
    score = models.PositiveIntegerField()
    attempt_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'topic'], name="unique_attempt_per_topic")
        ]
        ordering = ['-attempt_date']

    def __str__(self):
        return f"{self.user.username} - {self.topic.topic_name} - Score: {self.score}"

class UserResponse(models.Model):
    response_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    
    ANSWER_CHOICES = [
        ('A', 'Option A'),
        ('B', 'Option B'),
        ('C', 'Option C'),
        ('D', 'Option D'),
    ]
    selected_answer = models.CharField(max_length=1, choices=ANSWER_CHOICES)
    is_correct = models.BooleanField()

    class Meta:
        verbose_name = "User Response"
        verbose_name_plural = "User Responses"

    def __str__(self):
        return f"{self.user.username} - {self.question.question_text} - {self.selected_answer} ({'✔' if self.is_correct else '✘'})"
class Leaderboard(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    total_score = models.PositiveIntegerField(default=0)  # Accumulated total score across all topics
    highest_score = models.PositiveIntegerField(default=0)  # Best single attempt across all quizzes
    total_attempted_questions = models.PositiveIntegerField(default=0)  # Total questions attempted
    last_attempt_date = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-total_score', '-highest_score', 'last_attempt_date']
        verbose_name = "Leaderboard"
        verbose_name_plural = "Leaderboard"

    def __str__(self):
        return f"{self.user.username} - Total Score = {self.total_score}, Highest Score = {self.highest_score}"

class Profile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Correct field name
    photo = models.ImageField(upload_to='profile_images/', default='default.jpg')  # Profile image

    def __str__(self):
        return self.user.username
