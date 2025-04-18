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
import csv
from django.db.models import Avg, Count
from django.utils import timezone
from datetime import datetime, timedelta
from django.db.models import DateField
from django.db.models.functions import TruncDay, TruncWeek, TruncMonth

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
    data = WaterData.objects.filter(user=request.user).order_by('-timestamp')

    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    quick_filter = request.GET.get('quick_filter')
    group_by = request.GET.get('group_by', '')  # can be day/week/month

    now = timezone.now()

    if quick_filter == '7days':
        start = now - timedelta(days=7)
        data = data.filter(timestamp__gte=start)
    elif quick_filter == 'thismonth':
        start = now.replace(day=1)
        data = data.filter(timestamp__gte=start)
    elif quick_filter == 'all':
        pass
    elif start_date and end_date:
        try:
            start = datetime.strptime(start_date, "%Y-%m-%d")
            end = datetime.strptime(end_date, "%Y-%m-%d")
            data = data.filter(timestamp__date__gte=start, timestamp__date__lte=end)
        except ValueError:
            pass

    # Grouping logic
    summary_data = None
    if group_by in ['day', 'week', 'month']:
        if group_by == 'day':
            trunc = TruncDay('timestamp')
        elif group_by == 'week':
            trunc = TruncWeek('timestamp')
        else:
            trunc = TruncMonth('timestamp')

        summary_data = (
            data
            .annotate(period=trunc)
            .values('period')
            .annotate(
                avg_water_level=Avg('water_level'),
                avg_conductivity=Avg('conductivity'),
                count=Count('id')
            )
            .order_by('period')
        )

    context = {
        'data': data,
        'start_date': start_date or '',
        'end_date': end_date or '',
        'quick_filter': quick_filter or '',
        'group_by': group_by,
        'summary_data': summary_data,
    }

    return render(request, 'monitor/water_data.html', context)

@login_required
def about(request):
    return render(request, 'monitor/about.html')


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
    alerts = Alert.objects.filter(user=request.user).order_by('-timestamp')

    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    alert_type = request.GET.get('type')

    # Filter by alert type
    if alert_type == 'level':
        alerts = alerts.filter(message__icontains='water level')
    elif alert_type == 'conductivity':
        alerts = alerts.filter(message__icontains='conductivity')

    # Filter by date range
    if start_date and end_date:
        try:
            start = datetime.strptime(start_date, "%Y-%m-%d")
            end = datetime.strptime(end_date, "%Y-%m-%d")
            alerts = alerts.filter(timestamp__date__gte=start, timestamp__date__lte=end)
        except ValueError:
            pass

    context = {
        'alerts': alerts,
        'start_date': start_date or '',
        'end_date': end_date or '',
        'alert_type': alert_type or '',
    }

    return render(request, 'monitor/alerts.html', context)

@login_required
def export_alerts_csv(request):
    alerts = Alert.objects.filter(user=request.user).order_by('-timestamp')

    # Apply filters if they exist
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    alert_type = request.GET.get('type')

    if alert_type == 'level':
        alerts = alerts.filter(message__icontains='water level')
    elif alert_type == 'conductivity':
        alerts = alerts.filter(message__icontains='conductivity')

    if start_date and end_date:
        try:
            from datetime import datetime
            start = datetime.strptime(start_date, "%Y-%m-%d")
            end = datetime.strptime(end_date, "%Y-%m-%d")
            alerts = alerts.filter(timestamp__date__gte=start, timestamp__date__lte=end)
        except ValueError:
            pass  # Invalid date format; ignore

    # Create CSV response
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="alerts.csv"'

    writer = csv.writer(response)
    writer.writerow(['Timestamp', 'Level', 'Message'])

    for alert in alerts:
        writer.writerow([alert.timestamp, alert.level, alert.message])

    return response

def about(request):
    return render(request, 'monitor/about.html')

def contact(request):
    return render(request, 'monitor/contact.html')

@login_required
def export_csv(request):
    # Get all readings for the logged-in user
    data = WaterData.objects.filter(user=request.user).order_by('-timestamp')

    # Set up HTTP response with CSV headers
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="water_data.csv"'

    writer = csv.writer(response)
    writer.writerow(['Timestamp', 'Water Level (%)', 'Conductivity (µS/cm)'])

    for row in data:
        writer.writerow([row.timestamp, row.water_level, row.conductivity])

    return response