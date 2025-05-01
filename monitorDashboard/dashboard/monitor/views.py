from django.shortcuts import render
from .models import WaterData, Alert, UserSettings
import matplotlib.pyplot as plt
from io import BytesIO
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect
from .forms import CustomUserCreationForm, UserSettingsForm
from django.utils import timezone
import csv, json
from django.db.models import Avg, Count
from django.utils import timezone
from datetime import datetime, timedelta
from django.db.models import DateField
from django.utils.dateformat import format
from django.db.models.functions import TruncDay, TruncWeek, TruncMonth
from django.contrib import messages
from django.contrib.messages import get_messages
from django.conf import settings
from django.core.mail import send_mail
from datetime import timedelta
from django.utils.timezone import now
from django.db.models import Avg
from .models import WaterData, Alert, UserSettings
from django.contrib.auth.models import User

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
    # Clear leftover messages
    list(get_messages(request))

    # Get last 20 readings
    data = WaterData.objects.filter(user=request.user).order_by('-timestamp')[:20]
    data = list(reversed(list(data)))  # Ensure iterable twice

    latest_data = data[-1] if data else None

    timestamps = [format(d.timestamp, 'H:i:s') for d in data]
    water_levels = [d.water_level for d in data]
    conductivity = [d.conductivity for d in data]

    # Get user settings for thresholds + notifications
    user_settings, _ = UserSettings.objects.get_or_create(user=request.user)

    alert = None
    if latest_data:
        if latest_data.water_level < user_settings.low_water_threshold:
            alert = f"Low water level detected: {latest_data.water_level}%"
            created, _ = Alert.objects.get_or_create(user=request.user, message=alert, level="Warning")
            if created and user_settings.notify_low_water:
                send_mail(
                    'Water Monitor Alert - Low Water Level',
                    alert,
                    settings.DEFAULT_FROM_EMAIL,
                    [request.user.email],
                    fail_silently=True,
                )

        elif latest_data.conductivity > user_settings.high_conductivity_threshold:
            alert = f"High conductivity detected: {latest_data.conductivity} µS/cm"
            created, _ = Alert.objects.get_or_create(user=request.user, message=alert, level="Warning")
            if created and user_settings.notify_high_conductivity:
                send_mail(
                    'Water Monitor Alert - High Conductivity',
                    alert,
                    settings.DEFAULT_FROM_EMAIL,
                    [request.user.email],
                    fail_silently=True,
                )
    # Historical summary
    one_week_ago = now() - timedelta(days=7)
    past_week_data = WaterData.objects.filter(user=request.user, timestamp__gte=one_week_ago)
    weekly_data = WaterData.objects.filter(user=request.user, timestamp__date__gte=one_week_ago)
    weekly_alerts = Alert.objects.filter(user=request.user, timestamp__date__gte=one_week_ago)

    days_with_low_water = past_week_data.filter(water_level__lt=20).dates('timestamp', 'day').count()
    days_with_high_conductivity = past_week_data.filter(conductivity__gt=200).dates('timestamp', 'day').count()
    total_days = past_week_data.dates('timestamp', 'day').count()
    avg_water = weekly_data.aggregate(avg=Avg('water_level'))['avg'] or 0
    avg_cond = weekly_data.aggregate(avg=Avg('conductivity'))['avg'] or 0
    low_water_count = weekly_alerts.filter(message__icontains='low water').count()
    high_cond_count = weekly_alerts.filter(message__icontains='conductivity').count()

    summary_text = "No data available this week."
    if total_days:
        summary_text = (
            f"Water level was below 20% on {days_with_low_water} of {total_days} days this week. "
            f"High conductivity (>200 µS/cm) occurred on {days_with_high_conductivity} days."
        )

    context = {
        'latest_data': latest_data,
        'alert': alert,
        'timestamps': timestamps,
        'water_levels': water_levels,
        'conductivity': conductivity,
        'summary_text': summary_text,
        'avg_water': round(avg_water, 1),
        'avg_cond': round(avg_cond, 1),
        'low_water_count': low_water_count,
        'high_cond_count': high_cond_count,
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

    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    if start_date and end_date:
        try:
            start = datetime.strptime(start_date, '%Y-%m-%d')
            end = datetime.strptime(end_date, '%Y-%m-%d')
            data = data.filter(timestamp__date__range=(start, end))
        except ValueError:
            pass  # Ignore invalid dates

    timestamps = [format(entry.timestamp, 'H:i:s') for entry in data]
    water_levels = [entry.water_level for entry in data]
    conductivity = [entry.conductivity for entry in data]

    # Get user-defined alert thresholds
    settings = UserSettings.objects.filter(user=request.user).first()
    water_threshold = settings.low_water_threshold if settings else 20
    conductivity_threshold = settings.high_conductivity_threshold if settings else 200

    context = {
        'timestamps': json.dumps(timestamps),
        'water_levels': json.dumps(water_levels),
        'conductivity': json.dumps(conductivity),
        'start_date': start_date or '',
        'end_date': end_date or '',
        'water_threshold': water_threshold,
        'conductivity_threshold': conductivity_threshold,
    }

    return render(request, 'monitor/graph.html', context)


@login_required
def get_graph_data(request):
    latest = WaterData.objects.filter(user=request.user).order_by('-timestamp')[:1]

    timestamps = [format(entry.timestamp, 'H:i:s') for entry in latest]
    water_levels = [entry.water_level for entry in latest]
    conductivity = [entry.conductivity for entry in latest]

    return JsonResponse({
        'timestamps': timestamps,
        'water_levels': water_levels,
        'conductivity': conductivity
    })

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

@login_required
def settings_view(request):
    settings, created = UserSettings.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = UserSettingsForm(request.POST, instance=settings)
        if form.is_valid():
            form.save()
            messages.success(request, "Settings updated successfully.")
            return redirect('settings')
    else:
        form = UserSettingsForm(instance=settings)

    return render(request, 'monitor/settings.html', {'form': form})



def arduino_thresholds(request, username):
    try:
        user = User.objects.get(username=username)
        settings = UserSettings.objects.get(user=user)

        return JsonResponse({
            'low_water_threshold': settings.low_water_threshold,
            'high_conductivity_threshold': settings.high_conductivity_threshold,
        })
    except User.DoesNotExist:
        return JsonResponse({'error': 'User not found'}, status=404)
    except UserSettings.DoesNotExist:
        return JsonResponse({'error': 'Settings not found'}, status=404)