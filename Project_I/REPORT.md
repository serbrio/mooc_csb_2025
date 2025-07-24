LINK: https://github.com/serbrio/mooc_csb_2025.git

## Instructions
Install required packages:
```pip install -r requirements.txt```

Prepare DB:
```python manage.py migrate```

Start the server:
```python manage.py runserver```

## Short description of web application
After user have registered and logged in, app allows user:
- to send messages to other users
- to view messages received by the user
- to delete received messages.

To prepare for security flaws investigation, register at least a pair of users, and send several messages.
Web app page: http://127.0.0.1/web_sms/.

# FLAW 1:
https://github.com/serbrio/mooc_csb_2025/blob/master/Project_I/djangotutorial/web_sms/views.py#L185 (Line 185 in views.py)

**Broken access control** \
There is no check in the application, if a user is authorized to delete a message.

Though a user is not supposed to *see* messages addressed to other users, he can try to *delete* them. \
(Actually, there is another flaw of the same type in application which allows user to see messages addressed to other users. For conveniency, it is not discussed here but mentioned and fixed in [alternative fix](#alternative-fix) for Flaw 3.)

For example, after user ***test7*** has logged in and sent/deleted a message, he obtains [csfrmiddlewaretoken](screenshots/flaw-1-before-1.png), and in a cookie, [sessionid and csrftoken](screenshots/flaw-1-before-2.png), which he can use in POST requests to the app to attempt deletion.

User ***test7*** has no received messages, as shown on the web page. \
Here are all messages currently saved in the database: [messages](screenshots/flaw-1-before-4.png). \
User ***test7*** has ***receiver_id=7***, which is not among the ***receiver_id***s. \
(For convenience, in this example, text of every message is descriptive: "from userN to userK".)

User is able to delete any message, even if it is not addressed to him, just guessing its ***id*** and providing previously obtained tokens and sessionid.

For example, to delete message with ***id=12***, he does the following:
```
curl -X POST http://127.0.0.1:8000/web_sms/delete_message/ -H "Cookie: csrftoken=F6OFlgxFYtrLu5GQGph2x910uIDR9xvN; sessionid=2wiig7eafg80eps326e8ngalvc6npdth" -d "csrfmiddlewaretoken=InINKoAEPdOJH5JUJJOyia9cYbZ5W3HFdjmiVuX9Dw5k10fAfYVqF902iJsMVq2i&message_id=12"
```
As result, [message is deleted](screenshots/flaw-1-before-6.png).

## Fix
Add check if the user who requested deletion has access to the message, i.e. if the user and the receiver of the message are the same person: \
https://github.com/serbrio/mooc_csb_2025/blob/master/Project_I/djangotutorial/web_sms/views.py#L188 (Line 188 in views.py)

Attempt to delete message with ***id=23***:
```
curl -X POST http://127.0.0.1:8000/web_sms/delete_message/ -H "Cookie: csrftoken=F6OFlgxFYtrLu5GQGph2x910uIDR9xvN; sessionid=2wiig7eafg80eps326e8ngalvc6npdth" -d "csrfmiddlewaretoken=InINKoAEPdOJH5JUJJOyia9cYbZ5W3HFdjmiVuX9Dw5k10fAfYVqF902iJsMVq2i&message_id=23"
```
Attempt fails: [message is not deleted](screenshots/flaw-1-after-2.png).

## References 
[A Broken Access Control](https://owasp.org/Top10/A01_2021-Broken_Access_Control/)


# FLAW 2:
https://github.com/serbrio/mooc_csb_2025/blob/master/Project_I/djangotutorial/web_sms/forms.py#L9 (Line 9 in forms.py)

**Identification and Authentication Failures** \
Application permits weak, or well-known passwords.

User can be registered with a weak password, for example, [root/root](screenshots/flaw-2-before-1.png),
can successfully [login](screenshots/flaw-2-before-2.png) and [use](screenshots/flaw-2-before-3.png) application.

## Fix
In application, the following password validators are activated by default: 
- UserAttributeSimilarityValidator
- MinimumLengthValidator
- CommonPasswordValidator
- NumericPasswordValidator

To fix the flaw, add password validation to the registration form, i.e. reimplement the clean() method of the form by utilizing ***password_validation*** from the django.contrib.auth: \
https://github.com/serbrio/mooc_csb_2025/blob/master/Project_I/djangotutorial/web_sms/forms.py#L16 (Line 16 in forms.py).

As there is the custom "Account" model in the application, to make password validation work, add property ***password_validator_target*** to the model, which will be checked by validator: \
https://github.com/serbrio/mooc_csb_2025/blob/master/Project_I/djangotutorial/web_sms/models.py#L16 (Line 16 in models.py).

In settings, make UserAttributeSimilarityValidator check property ***password_validator_target*** of the "Account" model: \
https://github.com/serbrio/mooc_csb_2025/blob/master/Project_I/djangotutorial/mysite/settings.py#L94 (Line 94 in mysite/settings.py). \
Optionally: fine tune the ***max_similarity*** option of the validator.

After the fix, weak passwords (or credential pairs) are not accepted with the appropriate error messages:
- [root/root](screenshots/flaw-2-after-1.png): too similar, too short, too common;
- [password: 123123123](screenshots/flaw-2-after-2.png): too common, entirely numeric;
- [test200/test123123](screenshots/flaw-2-after-3.png): too similar;
- [test200/qwe](screenshots/flaw-2-after-4.png): too short, too common.

## References 
[Identification and Authentication Failures](https://owasp.org/Top10/A07_2021-Identification_and_Authentication_Failures/)\
[password-management-in-django](https://docs.djangoproject.com/en/5.2/topics/auth/passwords/#password-management-in-django)\
[using-forms-to-validate-data](https://docs.djangoproject.com/en/5.2/ref/forms/api/#using-forms-to-validate-data)\
[validating-fields-with-clean](https://docs.djangoproject.com/en/5.2/ref/forms/validation/#validating-fields-with-clean)\
[Learn_web_development: Django](https://developer.mozilla.org/en-US/docs/Learn_web_development/Extensions/Server-side/Django)\
[attribute_similarity_authentication_fails](https://www.reddit.com/r/django/comments/8tyhhe/attribute_similarity_authentication_fails/)


# FLAW 3:
https://github.com/serbrio/mooc_csb_2025/blob/master/Project_I/djangotutorial/web_sms/views.py#L45 (Line 45 in views.py)

**Injection (SQL)** \
Application does not prevent SQL injection attacks.

To show to user one of the [messages](screenshots/flaw-3-before-1.png), application uses url ```http://127.0.0.1/web_sms/<message_id>/read_message/```. Like [this](screenshots/flaw-3-before-2.png). \
Parameter ***message_id*** in the request can be replaced with a SQL injection, for example:
```' union all select text from web_sms_message;--```
[Such SQL injection](screenshots/flaw-3-before-3.png) can lead to data leakage, for example, it can [reveal messages](screenshots/flaw-3-before-4.png) of other users. \
(Messages are not encrypted. This issue is approached and fixed in [Flaw 5](#flaw-5).)

## Fix
When assembling the query, get rid of the string concatenation which makes the injection attack possible. Use DB-API's parameter substitution (placeholder ***?***) instead: \
https://github.com/serbrio/mooc_csb_2025/blob/master/Project_I/djangotutorial/web_sms/views.py#L50 (Line 50 in views.py).

Accordingly, instead of the concatenated and vulnerable string, use parameter substituion when executing SQL query: \
https://github.com/serbrio/mooc_csb_2025/blob/master/Project_I/djangotutorial/web_sms/views.py#L57 (Line 57 in views.py).

After the fix, application [prevents](screenshots/flaw-3-after-1.png) SQL injection attack.

## Alternative Fix
Alternative to using DB-API's parameter substituion is using of Django ORM: \
https://github.com/serbrio/mooc_csb_2025/blob/master/Project_I/djangotutorial/web_sms/views.py#L34 (Line 34 in views.py).

This fix prevents SQL injection [as well](screenshots/flaw-3-after-2.png). (By the way, additionally, it [remidies](screenshots/flaw-3-after-3.png) a broken access control flaw in this piece of code: it checks if the user has access to read the message.)

## References 
[Injection](https://owasp.org/Top10/A03_2021-Injection/)\
[how-to-use-placeholders-to-bind-values-in-sql-queries](https://docs.python.org/3/library/sqlite3.html#how-to-use-placeholders-to-bind-values-in-sql-queries)


# FLAW 4:
https://github.com/serbrio/mooc_csb_2025/blob/master/Project_I/djangotutorial/web_sms/views.py#L88 (Line 88 in views.py)

**Insecure design** \
Password recovery workflow includes "questions and answers", which can not be trusted as evidence of identity because more than one person can know the answers.

Attacker can [reset](screenshots/flaw-4-before-1.png) user's password by providing a matching [username](screenshots/flaw-4-before-2.png) and [secret answer](screenshots/flaw-4-before-3.png) pair, and therefore submitting the [password change](screenshots/flaw-4-before-4.png) form, which resets the user's password. (The "question and answer" pair has been saved during the user registration).

## Fix
Get rid of the "questions and answers" logic completely. \
Views: \
https://github.com/serbrio/mooc_csb_2025/blob/master/Project_I/djangotutorial/web_sms/views.py#L89 (Line 89 in views.py) \
https://github.com/serbrio/mooc_csb_2025/blob/master/Project_I/djangotutorial/web_sms/views.py#L13 (Line 13 in views.py) \
Forms: \
https://github.com/serbrio/mooc_csb_2025/blob/master/Project_I/djangotutorial/web_sms/forms.py#L35 (Line 35 in forms.py) \
Urls: \
https://github.com/serbrio/mooc_csb_2025/blob/master/Project_I/djangotutorial/web_sms/urls.py#L15 (Line 15 in web_sms/urls.py)

And optionally, get rid of useless "questions and answers", i.e. ***secret_question*** and ***secret_answer*** in user registration procedure: in models.py, forms.py, and views.py. Not to mention the useless ***secret_question.html*** template. (All listed optional things do not fix Flaw 4 and are rather cosmetical, that is why, to not overload the code, the fix is not provided for them.)

Instead, use secure password recovery workflow. For example, default django password management workflow (password_reset views, forms and urls). 

To do so, include the provided URLconf in django.contrib.auth.url in application's URLconf: \
https://github.com/serbrio/mooc_csb_2025/blob/master/Project_I/djangotutorial/mysite/urls.py#L27 (Line 27 in mysite/urls.py) 

For convenience, instead of original login template, use the fixed one: \
https://github.com/serbrio/mooc_csb_2025/blob/master/Project_I/djangotutorial/web_sms/templates/web_sms/login_fix_flaw_4.html#L15 (Line 15 in templates/web_sms/login_fix_flaw_4.html)

Finally, to let django send you a one-time use link for password reset, set up sending emails: \
https://github.com/serbrio/mooc_csb_2025/blob/master/Project_I/djangotutorial/mysite/settings.py#L138 (Line 138 in mysite/settings.py) \
(In this example, smtp.gmail.com is used. To make it work, you have to set up a google account. See references.)

After the fix, there is no insecure "secret question and secret answer" logic left in the application. Instead, password can be reset in django password reset workflow via one-time password reset link, which is sent to the user's email.

A user's password reset workflow:
click [recover](screenshots/flaw-4-after-1.png), [provide email address](screenshots/flaw-4-after-2.png), get confirmation that [password reset link is sent](screenshots/flaw-4-after-3.png), check email, follow the received link which opens [password change dialog](screenshots/flaw-4-after-4.png), which resolves in [password reset confirmation](screenshots/flaw-4-after-5.png) and password change.

## References
[Insecure Design](https://owasp.org/Top10/A04_2021-Insecure_Design/)\
[using-sessions-in-views](https://docs.djangoproject.com/en/5.2/topics/http/sessions/#using-sessions-in-views)\
[app-passwords for google account](https://myaccount.google.com/u/4/apppasswords)\
[smtp-backend](https://docs.djangoproject.com/en/5.2/topics/email/#smtp-backend)\
[django-reset-password-not-sending-email](https://stackoverflow.com/questions/20325729/django-reset-password-not-sending-email)\
[Authentication Views](https://docs.djangoproject.com/en/5.2/topics/auth/default/#module-django.contrib.auth.views)


# FLAW 5:
https://github.com/serbrio/mooc_csb_2025/blob/master/Project_I/djangotutorial/web_sms/models.py#L26 (Line 26 in models.py)

**Cryptographic Failures** \
Sensitive data (in this case, private messages) not encrypted at rest, allowing an attacker to retrieve this data using, for examle, SQL injection flaws.

As described in [Flaw 3](#flaw-3), [SQL injection](screenshots/flaw-3-before-3.png) can [reveal](screenshots/flaw-3-before-4.png) messages of users. And as the messages are not encrypted, attacker can gain access to the personal and sensitive data in these messages.

## Fix
To encrypt the fields in django Models, it is convenient to use the django-fernet-encrypted-fields package. \
If not installed yet: \
```pip install django-fernet-encrypted-fields```

Make *Message* model encrypt text of messages before saving them to the database: \
https://github.com/serbrio/mooc_csb_2025/blob/master/Project_I/djangotutorial/web_sms/models.py#L27 (Line 27 in models.py) \
From now on, messages will be stored encrypted in the database.
(When working with the ORM (i.e. retrieving the messages from the django.db.models), messages are retrieved automatically decrypted. But in the DB they are stored encrypted.)

Set random **SALT_KEY**: \
https://github.com/serbrio/mooc_csb_2025/blob/master/Project_I/djangotutorial/mysite/settings.py#L150 (Line 150 in mysite/settings.py) \

After the fix, a SQL injection attack will not reveal the sensitive data in plain text, but [encrypted](screenshots/flaw-5-after-1.png).

Side effect of the fix: to show a message to a user, the application uses the DB-API instead of the ORM, so user will see his [messages](screenshots/flaw-5-after-2.png) [encrypted](screenshots/flaw-5-after-3.png). \
Use ORM to allow user to see his messages [decrypted](screenshots/flaw-5-after-4.png) - apply the [alternatnative fix](#alternative-fix) for Flaw 3.

## References
[Cryptographic Failures](https://owasp.org/Top10/A02_2021-Cryptographic_Failures/)\
[django-fernet-encrypted-fields](https://pypi.org/project/django-fernet-encrypted-fields/)