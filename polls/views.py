from django.shortcuts import render

from polls.models import Poll

# Create your views here.
def home(request):
    context = {'polls': Poll.objects.all()}
    return render(request, 'home.html', context)

def poll():
    pass
