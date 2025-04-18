from django.shortcuts import render
from .models import WaterData, Alert
import matplotlib.pyplot as plt
from io import BytesIO
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect
from .forms import CustomUserCreationForm
from django.utils import timezone

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
    # Get latest data for the logged-in user
    data = WaterData.objects.filter(user=request.user).order_by('-timestamp')
    latest_data = data.first()

    alert = None  # Message to show on the homepage

    if latest_data:
        # Conditions
        low_water_level = latest_data.water_level < 20
        high_conductivity = latest_data.conductivity > 200

        # Generate alert message
        if low_water_level:
            alert = f"Low water level detected: {latest_data.water_level}%"

            # Save alert if it hasn't already been saved today
            if not Alert.objects.filter(user=request.user, message=alert, timestamp__date=timezone.now().date()).exists():
                Alert.objects.create(user=request.user, message=alert, level="Warning")

        elif high_conductivity:
            alert = f"High conductivity detected: {latest_data.conductivity} µS/cm"

            if not Alert.objects.filter(user=request.user, message=alert, timestamp__date=timezone.now().date()).exists():
                Alert.objects.create(user=request.user, message=alert, level="Warning")

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

@login_required
def alerts_list(request):
    # You can filter by time if needed (e.g., last 7 days)
    alerts = Alert.objects.filter(user=request.user).order_by('-timestamp')
    return render(request, 'monitor/alerts.html', {'alerts': alerts})


def about(request):
    return render(request, 'monitor/about.html')

def contact(request):
    return render(request, 'monitor/contact.html')