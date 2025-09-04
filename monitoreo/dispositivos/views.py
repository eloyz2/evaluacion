from django.shortcuts import render, get_object_or_404, redirect
from .models import Device, Measurement, Alert, Category, Zone
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib import messages


# ====================
# VISTAS PRINCIPALES (HU1–HU5)
# ====================

@login_required
def dashboard(request):
    devices_by_category = Category.objects.count()
    devices_by_zone = Zone.objects.count()
    alerts = Alert.objects.order_by("-created_at")[:5]
    measurements = Measurement.objects.order_by("-created_at")[:10]


    return render(request, "dashboard.html", {
        "devices_by_category": devices_by_category,
        "devices_by_zone": devices_by_zone,
        "alerts": alerts,
        "measurements": measurements,
    })


@login_required
def device_list(request):
    category_filter = request.GET.get("category")
    devices = Device.objects.filter(organization=request.user.organization)
    if category_filter:
        devices = devices.filter(category_id=category_filter)
    categories = Category.objects.filter(organization=request.user.organization)
    return render(request, "devices/device_list.html", {"devices": devices, "categories": categories})


@login_required
def device_detail(request, pk):
    device = get_object_or_404(Device, pk=pk, organization=request.user.organization)
    measurements = Measurement.objects.filter(device=device).order_by("-created_at")
    alerts = Alert.objects.filter(device=device).order_by("-created_at")
    return render(request, "devices/device_detail.html", {"device": device, "measurements": measurements, "alerts": alerts})


@login_required
def measurement_list(request):
    measurements = Measurement.objects.filter(device__organization=request.user.organization).order_by("-created_at")[:50]
    return render(request, "measurements/measurement_list.html", {"measurements": measurements})


@login_required
def alert_list(request):
    alerts = Alert.objects.filter(device__organization=request.user.organization).order_by("-created_at")
    return render(request, "alerts/alert_list.html", {"alerts": alerts})


# ====================
# VISTAS AUTENTICACIÓN (HU6–HU8)
# ====================

def login_view(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect("dashboard")
            else:
                messages.error(request, "Credenciales inválidas")
        else:
            messages.error(request, "Credenciales inválidas")
    else:
        form = AuthenticationForm()
    return render(request, "auth/login.html", {"form": form})


def register_view(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Registro exitoso, ahora puedes iniciar sesión")
            return redirect("login")
    else:
        form = UserCreationForm()
    return render(request, "auth/register.html", {"form": form})


def password_reset_view(request):
    if request.method == "POST":
        email = request.POST.get("email")
        # Simulación de envío
        messages.success(request, f"Se enviaron instrucciones a {email} (simulado)")
        return redirect("login")
    return render(request, "auth/password_reset.html")
