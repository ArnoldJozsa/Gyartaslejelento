from django.shortcuts import render, redirect

def main_view(request):
    if not request.session.get('is_authenticated'):
        return redirect('/login/')
    return render(request, 'main/main.html')
