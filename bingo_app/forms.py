from django import forms
from .models import Suggestion, BingoProject

class CreateProjectForm(forms.ModelForm):
    class Meta:
        model = BingoProject
        fields = ['project_id']
    

class JoinProjectForm(forms.Form):
    project = forms.ModelChoiceField(queryset=BingoProject.objects.all(), empty_label="", to_field_name="project_id", label="Die gibts")

class SuggestionForm(forms.Form):
    suggestion = forms.CharField(label='Your Suggestion', max_length=200)
    category = forms.ChoiceField(choices=Suggestion.CATEGORY_CHOICES, required=True, label='Category')