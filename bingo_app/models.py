from django.db import models

# Create your models here.
class BingoProject(models.Model):
    project_id = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.project_id

class Suggestion(models.Model):
    UTOPIC = 'UT'
    DYSTOPIC = 'DY'
    CATEGORY_CHOICES = [
        (UTOPIC, 'Utopisch'),
        (DYSTOPIC, 'Dystopisch'),
    ]

    text = models.CharField(max_length=200)
    category = models.CharField(max_length=2, choices=CATEGORY_CHOICES, default=UTOPIC)
    upvotes = models.IntegerField(default=0)
    project = models.ForeignKey(BingoProject, on_delete=models.CASCADE, default=1)

    def __str__(self):
        return self.text