LINK: https://github.com/serbrio/mooc_csb_2025.git

## Short description of the web application
After user have registered and logged in, app allows user:
- to send messages to other users
- to view messages received by the user
- to delete received messages.


# FLAW 1:
https://github.com/serbrio/mooc_csb_2025/blob/project_I/Project_I/djangotutorial/web_sms/views.py#L185 (Line 185 in views.py)

**Broken access control** \
There is no check in the application, if a user is authorized to delete a message.

Though a user can not see messages addressed to other users, 
he can try to delete them.

For example, after user ***test7*** has logged in and sent/deleted a message, he obtains [csfrmiddlewaretoken](screenshots/flaw-1-before-1.png), and in a cookie, [sessionid and csrftoken](screenshots/flaw-1-before-2.png), which he can use in POST requests to the app to attempt deletion.

User ***test7*** has no received messages, as shown on the web page. \
Here are all messages currently saved in the database: [messages](screenshots/flaw-1-before-4.png). \
User ***test7*** has ***id=7***, which is not among the ***receiver_id***s. \ 
For convenience, in this example, text of every message is descriptive: "from userN to userK".

User is able to delete any message, even if it is not addressed to him, just guessing its ***id*** and providing previously obtained tokens and sessionid.

For example, to delete message with ***id=12***, he does the following:
```
curl -X POST http://127.0.0.1:8000/web_sms/delete_message/ -H "Cookie: csrftoken=F6OFlgxFYtrLu5GQGph2x910uIDR9xvN; sessionid=2wiig7eafg80eps326e8ngalvc6npdth" -d "csrfmiddlewaretoken=InINKoAEPdOJH5JUJJOyia9cYbZ5W3HFdjmiVuX9Dw5k10fAfYVqF902iJsMVq2i&message_id=12"
```
As result, [message is deleted](screenshots/flaw-1-before-6.png).

## Fix
Add check if the user who requested deletion has access to the message, i.e. if the user and the receiver of the message are the same person: \
https://github.com/serbrio/mooc_csb_2025/blob/project_I/Project_I/djangotutorial/web_sms/views.py#L188 (Line 188 in views.py)

Attempt to delete message with ***id=23***:
```
curl -X POST http://127.0.0.1:8000/web_sms/delete_message/ -H "Cookie: csrftoken=F6OFlgxFYtrLu5GQGph2x910uIDR9xvN; sessionid=2wiig7eafg80eps326e8ngalvc6npdth" -d "csrfmiddlewaretoken=InINKoAEPdOJH5JUJJOyia9cYbZ5W3HFdjmiVuX9Dw5k10fAfYVqF902iJsMVq2i&message_id=23"
```
Attempt failed: [message is not deleted](screenshots/flaw-1-after-2.png).

## References 
[A Broken Access Control](https://owasp.org/Top10/A01_2021-Broken_Access_Control/)


# FLAW 2:
https://github.com/serbrio/mooc_csb_2025/blob/project_I/Project_I/djangotutorial/web_sms/forms.py#L8 (Line 8 in forms.py)

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

To fix the flaw, add password validation to the registration form, i.e. reimplement the clean() method of the form: \
https://github.com/serbrio/mooc_csb_2025/blob/project_I/Project_I/djangotutorial/web_sms/forms.py#L15 (Line 15 in forms.py).

As there is custom "Account" model in the application, to make password validation work, add property ***password_validator_target*** to the model, which will be checked by validator: \
https://github.com/serbrio/mooc_csb_2025/blob/project_I/Project_I/djangotutorial/web_sms/models.py#L13 (Line 13 in models.py).

Make UserAttributeSimilarityValidator to check property ***password_validator_target*** of the "Account" model: \
https://github.com/serbrio/mooc_csb_2025/blob/project_I/Project_I/djangotutorial/mysite/settings.py#L94 (Line 94 in mysite/settings.py). \
Optionally: fine tune the ***max_similarity*** option of the validator.

After fix, weak passwords (or credential pairs) are not accepted with the appropriate error messages:
- [root/root](screenshots/flaw-2-after-1.png): too similar, too short, too common;
- [password: 123123123](screenshots/flaw-2-after-2.png): too common, entirely numeric;
- [test200/test123123](screenshots/flaw-2-after-3.png): too similar;
- [test200/qwe](screenshots/flaw-2-after-4.png): too short, too common.

## References 
[Identification and Authentication Failures](https://owasp.org/Top10/A07_2021-Identification_and_Authentication_Failures/) [password-management-in-django](https://docs.djangoproject.com/en/5.2/topics/auth/passwords/#password-management-in-django) [using-forms-to-validate-data](https://docs.djangoproject.com/en/5.2/ref/forms/api/#using-forms-to-validate-data) [validating-fields-with-clean](https://docs.djangoproject.com/en/5.2/ref/forms/validation/#validating-fields-with-clean) [Learn_web_development: Django](https://developer.mozilla.org/en-US/docs/Learn_web_development/Extensions/Server-side/Django) [attribute_similarity_authentication_fails](https://www.reddit.com/r/django/comments/8tyhhe/attribute_similarity_authentication_fails/)


# FLAW 3:
https://github.com/serbrio/mooc_csb_2025/blob/project_I/Project_I/djangotutorial/web_sms/views.py#L46 (Line 46 in views.py)

**Injection** \
Application does not prevent SQL injection attacks.

To show to user one of the [messages](screenshots/flaw-3-before-1.png), application uses url ```<message_id>/read_message/```. Like [this](screenshots/flaw-3-before-2.png). \
Parameter ***message_id*** in the request can be replaced with a [SQL injection](screenshots/flaw-3-before-3.png), which can lead to data leakage, for example, it can [reveal messages](screenshots/flaw-3-before-4.png) of other users.

## Fix
When assembling the query, get rid of the string concatenation which makes the injection attack possible. Use DB-API's parameter substitution (placeholder ***?***) instead: \
https://github.com/serbrio/mooc_csb_2025/blob/project_I/Project_I/djangotutorial/web_sms/views.py#L51 (Line 51 in views.py).

Accordingly, instead of the concatenated and vulnerable string, use parameter substituion when executing SQL query: \
https://github.com/serbrio/mooc_csb_2025/blob/project_I/Project_I/djangotutorial/web_sms/views.py#L58 (Line 58 in views.py).

After fix, application [prevents](screenshots/flaw-3-after-1.png) SQL injection attack.

## Alternative Fix
Alternative to using DB-API's parameter substituion is using of Django ORM: \
https://github.com/serbrio/mooc_csb_2025/blob/project_I/Project_I/djangotutorial/web_sms/views.py#L35 (Line 35 in views.py).

This fix prevents SQL injection [as well](screenshots/flaw-3-after-2.png). (By the way, it [remidies](screenshots/flaw-3-after-3.png) additionally a broken access control flaw in this piece of code: it checks if the user has access to read the message.)

## References 
[Injection](https://owasp.org/Top10/A03_2021-Injection/) [how-to-use-placeholders-to-bind-values-in-sql-queries](https://docs.python.org/3/library/sqlite3.html#how-to-use-placeholders-to-bind-values-in-sql-queries)


# FLAW 4:
https://github.com/serbrio/mooc_csb_2025/blob/project_I/Project_I/djangotutorial/web_sms/views.py#L89 (Line 89 in views.py)

**Insecure design** \
Password recovery workflow includes "questions and answers", which can not be trusted as evidence of identity because more than one person can know the answers.

User can [recover](screenshots/flaw-4-before-1.png) his password by providing [username](screenshots/flaw-4-before-2.png) and [secret answer](screenshots/flaw-4-before-3.png), and therefore submitting the [password change](screenshots/flaw-4-before-4.png) form, which resets the user's password. (The "question and answer" pair has been saved during user registration).

## Fix
Get rid of the "questions and answers" logic completely. \
Views: \
https://github.com/serbrio/mooc_csb_2025/blob/project_I/Project_I/djangotutorial/web_sms/views.py#L90 (Line 90 in views.py) \
https://github.com/serbrio/mooc_csb_2025/blob/project_I/Project_I/djangotutorial/web_sms/views.py#L14 (Line 14 in views.py) \
Forms: \
https://github.com/serbrio/mooc_csb_2025/blob/project_I/Project_I/djangotutorial/web_sms/forms.py#L34 (Line 34 in forms.py) \
Urls: \
https://github.com/serbrio/mooc_csb_2025/blob/project_I/Project_I/djangotutorial/web_sms/urls.py#L15 (Line 15 in web_sms/urls.py)

And optionally, get rid of useless "questions and answers", i.e. ***secret_question*** and ***secret_answer*** in user registration procedure: in models.py, forms.py, and views.py. Not to mention the useless ***secret_question.html*** template. (All listed above optional things do not fix Flaw 4 and are rather cosmetical, that is why, to not overload the code, the commented-out fix is not provided for them.)

Instead, use secure password recovery workflow. For example, default django password management workflow (password_reset views, forms and urls). \
To do so, include the provided URLconf in django.contrib.auth.url in your own URLconf: \
https://github.com/serbrio/mooc_csb_2025/blob/project_I/Project_I/djangotutorial/mysite/urls.py#L27 (Line 27 in mysite/urls.py) \
For convenience, instead of original login template we use the fixed one: \
https://github.com/serbrio/mooc_csb_2025/blob/project_I/Project_I/djangotutorial/web_sms/templates/web_sms/login_fix_flaw_4.html#L15 (Line 15 in templates/web_sms/login_fix_flaw_4.html)

Finally, to let django send you a one-time use link for password reset, set up sending emails: \
https://github.com/serbrio/mooc_csb_2025/blob/project_I/Project_I/djangotutorial/mysite/settings.py#L138 (Line 138 in mysite/settings.py) \
(In this example, smtp.gmail.com is used. To make it work, you have to set up a google account. See references.)

After fix, user can recover password using django password reset workflow:
click [recover](screenshots/flaw-4-after-1.png), [provide email address](screenshots/flaw-4-after-2.png), get confirmation that [password reset is sent](screenshots/flaw-4-after-3.png), check provided email, follow the received link which opens [password change](screenshots/flaw-4-after-4.png) dialog, which resolves in [password reset confirmation](screenshots/flaw-4-after-5.png) and password change.

## References
[Insecure Design](https://owasp.org/Top10/A04_2021-Insecure_Design/) [using-sessions-in-views](https://docs.djangoproject.com/en/5.2/topics/http/sessions/#using-sessions-in-views) [app-passwords for google account](https://myaccount.google.com/u/4/apppasswords) [smtp-backend](https://docs.djangoproject.com/en/5.2/topics/email/#smtp-backend) [django-reset-password-not-sending-email](https://stackoverflow.com/questions/20325729/django-reset-password-not-sending-email) [Authentication Views](https://docs.djangoproject.com/en/5.2/topics/auth/default/#module-django.contrib.auth.views)


# FLAW 5:

## Fix

## References