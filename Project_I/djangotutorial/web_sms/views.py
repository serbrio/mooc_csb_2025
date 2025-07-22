import sqlite3

from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db import transaction
from django.shortcuts import render, redirect

from .forms import RegisterForm, MessageForm

## Fix Flaw 4
## The next line to be commented-out for the fix.
from .forms import PasswordRecoveryForm, SecretQuestionForm, PasswordChangeForm
## End Fix Flaw 4

from .models import Account, Message


@login_required
def homePageView(request):
    messages = Message.objects.filter(receiver=Account.objects.get(user_id=request.user.id))
    accounts = Account.objects.exclude(user_id=request.user.id)
    msg_form = MessageForm()
    return render(request, 
                  "web_sms/index.html", 
                  {"messages": messages, "accounts": accounts, "form": msg_form})


@login_required
def readMessageView(request, message_id):
    
    ## Alternative Fix Flaw 3
    """
    msg = Message.objects.get(id=message_id)
    user = User.objects.get(id=request.user.id)
    user_account = Account.objects.get(user=user)
    if msg.receiver != user_account:
        return HttpResponse("You have no read access to this message!..")
    return HttpResponse(msg.text)
    """
    ## End Alternative Fix Flaw 3 ##

    ## Flaw 3
    sql_statement = "SELECT text FROM web_sms_message WHERE id='" + message_id + "'"
    # example of SQL injection: 
    # http://127.0.0.1:8000/web_sms/' union all select text from web_sms_message;--/read_message/
    
    ## Fix Flaw 3
    ## sql_statement = "SELECT text FROM web_sms_message WHERE id=?"
    ## End Fix Flaw 3
   
    con = sqlite3.connect("db.sqlite3")
    cur = con.cursor()

    ## Fix Flaw 3
    ## The next line to be commented-out for the fix.
    res = cur.execute(sql_statement)

    ## res = cur.execute(sql_statement, (message_id,))
    ## End Fix Flaw 3

    return HttpResponse(f"{res.fetchall()}")


def registerView(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            # process the data in form.cleaned_data
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            secret_question = form.cleaned_data['secret_question']
            secret_answer = form.cleaned_data['secret_answer']
            # register new user
            user = User.objects.create_user(username=username, email=email, password=password)
            Account.objects.create(balance=100, secret_question=secret_question, 
                                   secret_answer=secret_answer, user=user)
            return redirect('/web_sms/')
    else:
        form = RegisterForm()

    return render(request, 'web_sms/register.html', {'form': form})


## Flaw 4
## Fix Flaw 4
## The following three functions to be completely commented-out for the fix:
## recoverPasswordView, secretQuestionView, passwordChangeView

def recoverPasswordView(request):
    if request.method == "POST":
        form = PasswordRecoveryForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            return HttpResponseRedirect(reverse("web_sms:secret_question", args=(username,)))
    else:
        form = PasswordRecoveryForm()

    return render(request, 'web_sms/password_recovery.html', {'form': form})


def secretQuestionView(request, username):
    user = User.objects.get(username=username)
    account = Account.objects.get(user=user)
    secret_question = account.secret_question

    if request.method == "POST":
        form = SecretQuestionForm(request.POST)
        if form.is_valid():
            received_answer = form.cleaned_data['secret_answer']
            if received_answer == account.secret_answer:
                request.session["got_secret_answer"] = True
                request.session["username"] = username
                return HttpResponseRedirect(reverse("web_sms:password_change", args=(username,)))
            else:
                return render(request, 'web_sms/not_quite_right.html')
    else:
        request.session["got_secret_answer"] = False
        request.session["username"] = ''
        form = SecretQuestionForm()

    return render(request, 'web_sms/secret_question.html', 
                  {'form': form, 'secret_question': secret_question, 'username': username})


def passwordChangeView(request, username):
    # Check, if secret_answer has been received
    if request.session.get('got_secret_answer') != True:
        return HttpResponseRedirect(reverse("web_sms:secret_question", args=(username,)))
    
    # Check, that username has not been changed scince secret_answer received
    if request.session.get('username') != username:
        return HttpResponseRedirect(reverse("web_sms:secret_question", args=(username,)))

    user = User.objects.get(username=username)

    if request.method == "POST":
        form = PasswordChangeForm(request.POST)
        if form.is_valid():
            password = form.cleaned_data['password']
            user.set_password(password)
            user.save()
            return redirect('/web_sms/')
    else:
        form = PasswordChangeForm()

    return render(request, 'web_sms/password_change.html', {'form': form, 'username': username})

## End Fix Flaw 4


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


@login_required
def sendView(request):
    if request.method == "POST":
        receiver = User.objects.get(username=request.POST.get('to'))
        sender = User.objects.get(id=request.user.id)
        message = request.POST.get('message')
        send_message(sender, receiver, message)
    
    return redirect('/web_sms/')


@transaction.atomic
def delete_message(message_id, user):
    ## Flaw 1
    msg = Message.objects.get(id=message_id)
    
    ## Fix Flaw 1 
    """
    user_account = Account.objects.get(user=user)
    if msg.receiver != user_account:
        return
    """
    ## End Fix Flaw 1

    msg.delete()


@login_required
def deleteView(request):
    if request.method == "POST":
        message_id = request.POST.get('message_id')
        user = User.objects.get(id=request.user.id)
        delete_message(message_id, user)

    return redirect('/web_sms/')