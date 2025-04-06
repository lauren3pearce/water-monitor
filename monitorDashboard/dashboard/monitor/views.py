from django.shortcuts import render
from .models import WaterData
import matplotlib.pyplot as plt
from io import BytesIO
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect
from .forms import CustomUserCreationForm

# Create your views here.

def signup(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')  # Redirect to login after successful signup
    else:
        form = CustomUserCreationForm()
    return render(request, 'registration/signup.html', {'form': form})

@login_required
def home(request):
    data = WaterData.objects.filter(user=request.user).order_by('-timestamp')
    latest_data = data.first()

    # Example alert logic: trigger if water level is too low
    alert = None
    if latest_data and latest_data.water_level < 20:
        alert = f"Water level is low ({latest_data.water_level}%). Please check the sensor!"

    context = {
        'latest_data': latest_data,
        'alert': alert
    }
    return render(request, 'monitor/home.html', context)

# View to display water level and conductivity data
@login_required
def water_data(request):
    data = WaterData.objects.filter(user=request.user).order_by('timestamp')
    return render(request, 'monitor/water_data.html', {'data': data})

# View to display the water level graph
@login_required
def water_level_graph(request):
    data = WaterData.objects.filter(user=request.user).order_by('timestamp')
    times = [entry.timestamp for entry in data]
    levels = [entry.water_level for entry in data]
    conductivity = [entry.conductivity for entry in data]

    plt.figure(figsize=(10, 6))
    plt.plot(times, levels, label="Water Level", marker="o")
    plt.plot(times, conductivity, label="Conductivity", marker="o")
    plt.xlabel('Time')
    plt.ylabel('Values')
    plt.title('Water Level and Conductivity Over Time')
    plt.xticks(rotation=45)
    plt.legend()

    # Save the plot to a BytesIO object
    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    
    return HttpResponse(buffer, content_type='image/png')


def about(request):
    return render(request, 'monitor/about.html')

def contact(request):
    return render(request, 'monitor/contact.html')