import sqlite3

from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db import transaction
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_protect

from .forms import RegisterForm, MessageForm
from .models import Account, Message


@login_required
def homePageView(request):
    messages = Message.objects.filter(receiver=Account.objects.get(user_id=request.user.id))
    accounts = Account.objects.exclude(user_id=request.user.id)
    msg_form = MessageForm()
    return render(request, "web_sms/index.html", {"messages": messages, "accounts": accounts, "form": msg_form})


def showMessageView(request, message_id):

    # Alternative fix
    """
    msg = Message.objects.get(id=message_id)
    user = User.objects.get(id=request.user.id)
    user_account = Account.objects.get(user=user)
    if msg.receiver != user_account:
        return HttpResponse("You have no read access to this message!..")
    return HttpResponse(msg.text)
    """

    sql_statement = "SELECT text FROM web_sms_message WHERE id='" + message_id + "'"
    # example of SQL injection: 
    # http://127.0.0.1:8000/web_sms/' union all select text from web_sms_message;--/read_message/
    
    # Fix:
    #sql_statement = "SELECT text FROM web_sms_message WHERE id=?"
   
    con = sqlite3.connect("db.sqlite3")
    cur = con.cursor()

    # the next line to be commented-out for the fix
    res = cur.execute(sql_statement)

    # Fix:
    #res = cur.execute(sql_statement, (message_id,))

    return HttpResponse(f"{res.fetchall()}")


def registerView(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            # process the data in form.cleaned_data
            # register new user
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = User.objects.create_user(username=username, password=password)
            Account.objects.create(balance=100, user=user)
            return redirect('/web_sms/')
    else:
        form = RegisterForm()

    return render(request, 'web_sms/register.html', {'form': form})


@transaction.atomic
def send_message(sender, receiver, message):
    if len(message.strip()) == 0:
        return

    sender_account = Account.objects.get(user=sender)
    receiver_account = Account.objects.get(user=receiver)

    if sender_account.balance <= 0:
        return
      
    Message.objects.create(text=message, sender=sender_account, receiver=receiver_account)

    sender_account.balance -= 1
    sender_account.save()

@csrf_protect
def sendView(request):
    if request.method == "POST":
        receiver = User.objects.get(username=request.POST.get('to'))
        sender = User.objects.get(id=request.user.id)
        message = request.POST.get('message')
        send_message(sender, receiver, message)
    
    return redirect('/web_sms/')


@transaction.atomic
def delete_message(message_id, user):
    msg = Message.objects.get(id=message_id)
    """
    user_account = Account.objects.get(user=user)
    if msg.receiver != user_account:
        return
    """
    msg.delete()


@csrf_protect
def deleteView(request):
    if request.method == "POST":
        message_id = request.POST.get('message_id')
        user = User.objects.get(id=request.user.id)
        delete_message(message_id, user)

    return redirect('/web_sms/')