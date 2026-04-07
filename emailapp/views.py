import ssl
ssl._create_default_https_context = ssl._create_unverified_context


from django.shortcuts import render, redirect
from django.core.mail import EmailMessage
from django.conf import settings
from .models import EmailLog, Contact

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

from django.views.decorators.csrf import csrf_exempt


# =========================
# 🔐 LOGIN
# =========================
def user_login(request):
    if request.method == "POST":
        user = authenticate(
            username=request.POST.get('username'),
            password=request.POST.get('password')
        )
        if user:
            login(request, user)
            return redirect('send')

        return render(request, 'auth/login.html', {
            'error': 'Invalid credentials ❌'
        })

    return render(request, 'auth/login.html')


# =========================
# 🆕 REGISTER
# =========================
@csrf_exempt
def register(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        if User.objects.filter(username=username).exists():
            return render(request, 'auth/register.html', {
                'error': 'User already exists ❌'
            })

        user = User.objects.create_user(
            username=username,
            password=password
        )

        login(request, user)
        return redirect('send')

    return render(request, 'auth/register.html')


# =========================
# 🔓 LOGOUT
# =========================
def logout_view(request):
    logout(request)
    return redirect('login')


# =========================
# 📧 SEND EMAIL (FINAL FIXED)
# =========================
@login_required
def send_mail_page(request):
    context = {}
    contacts = Contact.objects.filter(user=request.user)

    if request.method == 'POST':
        address = request.POST.get('address')
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        files = request.FILES.getlist('files')

        email_list = [email.strip() for email in address.split(',')]

        print("📩 Sending Email To:", email_list)   # DEBUG

        try:
            email = EmailMessage(
                subject,
                message,
                settings.EMAIL_HOST_USER,
                email_list
            )

            email.content_subtype = "html"

            # Attach files
            for f in files:
                email.attach(f.name, f.read(), f.content_type)

            # 🔥 IMPORTANT → RESULT CHECK
            result = email.send()
            print("✅ Send Result:", result)

            if result == 1:
                EmailLog.objects.create(
                    user=request.user,
                    to=address,
                    subject=subject,
                    message=message,
                    status="Sent"
                )

                context['result'] = "✅ Email sent successfully"

            else:
                EmailLog.objects.create(
                    user=request.user,
                    to=address,
                    subject=subject,
                    message=message,
                    status="Failed"
                )

                context['result'] = "❌ Email not delivered (blocked or spam)"

        except Exception as e:
            print("❌ ERROR:", e)

            EmailLog.objects.create(
                user=request.user,
                to=address,
                subject=subject,
                message=message,
                status="Failed"
            )

            context['result'] = f"❌ Error: {e}"

    context['contacts'] = contacts
    return render(request, "send.html", context)


# =========================
# 📒 CONTACTS
# =========================
@login_required
def contacts(request):
    if request.method == "POST":
        Contact.objects.create(
            user=request.user,
            name=request.POST.get('name'),
            email=request.POST.get('email')
        )

    contacts = Contact.objects.filter(user=request.user)
    return render(request, "contacts.html", {'contacts': contacts})


# =========================
# 📜 HISTORY
# =========================
@login_required
def history(request):
    query = request.GET.get('q')
    emails = EmailLog.objects.filter(user=request.user)

    if query:
        emails = emails.filter(to__icontains=query)

    return render(request, "history.html", {'emails': emails})


# =========================
# 📊 DASHBOARD
# =========================
@login_required
def dashboard(request):
    total = EmailLog.objects.filter(user=request.user).count()
    sent = EmailLog.objects.filter(user=request.user, status="Sent").count()
    failed = EmailLog.objects.filter(user=request.user, status="Failed").count()

    return render(request, "dashboard.html", {
        'total': total,
        'sent': sent,
        'failed': failed
    })