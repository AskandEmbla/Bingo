from django.shortcuts import render, redirect
from .forms import CreateProjectForm, JoinProjectForm, SuggestionForm
from .models import Suggestion, BingoProject
from django.http import HttpResponse
from django.http import HttpResponseRedirect
import random
from reportlab.lib.pagesizes import letter, landscape
from reportlab.pdfgen import canvas
from django.conf import settings
import os
from django.templatetags.static import static
from django.contrib.staticfiles import finders
from reportlab.lib.colors import white, black, grey

CELL_PADDING = 10  # Padding around the cell
TEXT_PADDING = 5   # Padding around the text inside the rectangle

def landing_page(request):
    join_form = JoinProjectForm()
    # handle other context and rendering for the landing page
    return render(request, 'start.html', {'join_form': join_form})
    #return render(request, 'start.html')

def create_project(request):
    if request.method == 'POST':
        form = CreateProjectForm(request.POST)
        if form.is_valid():
            form.save()
            project_id = form.cleaned_data['project_id']
            request.session['project_id'] = project_id  # Store project ID in session
            return redirect('suggest')  # Redirect to join project page
    else:
        form = CreateProjectForm()
    return render(request, 'create_project.html', {'form': form})

def join_project(request):
    if request.method == 'POST':
        form = JoinProjectForm(request.POST)
        if form.is_valid():
            project_id = form.cleaned_data['project'].project_id
            request.session['project_id'] = project_id  # Store in session
            return redirect('suggest')  # Redirect to suggestion view
    else:
        form = JoinProjectForm()
    return render(request, 'join_project.html', {'form': form})

def suggest_view(request):
    project_id = request.session.get('project_id')
    if project_id:
        project = BingoProject.objects.get(project_id=project_id)
        suggestions = Suggestion.objects.filter(project=project).order_by('-upvotes')
        if request.method == 'POST':
            form = SuggestionForm(request.POST)
            if form.is_valid():
                project_id = request.session.get('project_id')
                if project_id:
                    project = BingoProject.objects.get(project_id=project_id)
                    Suggestion.objects.create(text=form.cleaned_data['suggestion'],
                                      category=form.cleaned_data['category'],
                                      project=project)
                    return redirect('suggest')  # Redirect as needed
        else:
            form = SuggestionForm()

        # Order suggestions by upvotes in descending order
        return render(request, 'suggest.html', {'form': form, 'suggestions': suggestions})
    return redirect('join_project')  # Redirect if no project ID in session

def upvote(request, suggestion_id):
    voted_suggestions = request.session.get('voted_suggestions', [])

    if suggestion_id not in voted_suggestions:
        # If the user hasn't voted for this suggestion, proceed with upvoting
        suggestion = Suggestion.objects.get(id=suggestion_id)
        suggestion.upvotes += 1
        suggestion.save()

        # Add this suggestion to the voted set
        voted_suggestions.append(suggestion_id)
        request.session['voted_suggestions'] = voted_suggestions
    return HttpResponseRedirect('/bingo/suggest/')

def downvote(request, suggestion_id):
    voted_suggestions = request.session.get('voted_suggestions', [])
    if suggestion_id not in voted_suggestions:
        # If the user hasn't voted for this suggestion, proceed with upvoting
        suggestion = Suggestion.objects.get(id=suggestion_id)
        suggestion.upvotes -= 1
        suggestion.save()

        # Add this suggestion to the voted set
        voted_suggestions.append(suggestion_id)
        request.session['voted_suggestions'] = voted_suggestions
    return HttpResponseRedirect('/bingo/suggest/')

def thanks_view(request):
    return HttpResponse("Thank you for your suggestion!")
    
def estimate_font_size(text, max_width, max_font_size, min_font_size, font_name):
    """
    Estimate a suitable font size so that the text fits within max_width.
    Adjust between max_font_size and min_font_size.
    """
    # Create a dummy canvas to measure text width
    dummy_canvas = canvas.Canvas("/dev/null")
    font_size = max_font_size

    while font_size >= min_font_size:
        dummy_canvas.setFont(font_name, font_size)
        text_width = dummy_canvas.stringWidth(text)
        if text_width <= max_width:
            return font_size
        font_size -= 1

    return min_font_size

def split_text_into_lines(text, max_width, font_size, font_name):
    """
    Splits text into lines so that each line fits within max_width.
    """
    dummy_canvas = canvas.Canvas("/dev/null")
    dummy_canvas.setFont(font_name, font_size)
    words = text.split()
    lines = []
    current_line = ''

    for word in words:
        test_line = current_line + ' ' + word if current_line else word
        if dummy_canvas.stringWidth(test_line) <= max_width:
            current_line = test_line
        else:
            lines.append(current_line)
            current_line = word

    if current_line:
        lines.append(current_line)

    return lines

def generate_bingo_card(request):
    project_id = request.session.get('project_id')
    if project_id:
        try:
            project = BingoProject.objects.get(project_id=project_id)
            suggestions = list(Suggestion.objects.filter(project=project))
            if len(suggestions) < 16:
                return HttpResponse("Not enough suggestions for a Bingo card.")

            selected_suggestions = random.sample(suggestions, 16)
            random.shuffle(selected_suggestions)

            # Path to background images
            utopia_bg_path = finders.find('Utopisch.png')
            dystopia_bg_path = finders.find('Dystopisch.png')

            # Create PDF response in landscape orientation
            response = HttpResponse(content_type='application/pdf')
            response['Content-Disposition'] = 'attachment; filename="bingo_card.pdf"'
            p = canvas.Canvas(response, pagesize=landscape(letter))
            width, height = landscape(letter)

            # Calculate grid positions
            margin = 50  # Margin from page borders
            cell_width = (width - 2 * margin) / 4 - (2 * CELL_PADDING)
            cell_height = (height - 2 * margin) / 4 - (2 * CELL_PADDING) 

            p.setFont("Helvetica-Bold", 16)
            p.drawCentredString(width / 2, height - 20, f"{project.project_id} Bingo-Karte")

            # Draw cells and text
            for i, suggestion in enumerate(selected_suggestions):
                col = i % 4
                row = i // 4
                x = margin + col * cell_width
                y = height - margin - (row + 1) * cell_height

                # Draw background image
                bg_path = utopia_bg_path if suggestion.category == 'UT' else dystopia_bg_path
                p.drawImage(bg_path, x + CELL_PADDING, y + CELL_PADDING, width=cell_width, height=cell_height, preserveAspectRatio=True, anchor='c')

                # Calculate middle position for text
                text_x = x + cell_width / 2
                text_y = y + cell_height / 2

                max_text_width = cell_width - 20  # Allow some padding
                font_size = estimate_font_size(suggestion.text, max_text_width, 12, 6, "Helvetica")

                # Split text into lines
                lines = split_text_into_lines(suggestion.text, max_text_width, font_size, "Helvetica")

                # Adjust rectangle height based on number of lines
                rect_width = min(max_text_width, cell_width) - 2 * TEXT_PADDING
                rect_height = len(lines) * (font_size * 1.5)
                rect_x = x + CELL_PADDING + (cell_width - rect_width) / 2
                rect_y = y + CELL_PADDING + (cell_height - rect_height) / 2

                # Draw rounded rectangle behind text
                p.setFillColor(grey)
                p.roundRect(rect_x, rect_y, rect_width, rect_height, 10, stroke=1, fill=1)

                # Draw each line of text
                p.setFillColor(white)
                p.setFont("Helvetica", font_size)
                for line_num, line in enumerate(lines):
                    line_y = rect_y + rect_height - (line_num + 1) * (font_size * 1.5)
                    p.drawString(rect_x + TEXT_PADDING, line_y, line)

            p.showPage()
            p.save()
            return response 
        except BingoProject.DoesNotExist:
            return HttpResponse("Invalid project ID.")
    else:
        return redirect('join_project')