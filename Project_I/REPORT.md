LINK: https://github.com/serbrio/mooc_csb_2025.git

Installation instructions:
```
python manage.py migrate
```

### Short description of the web application
After user have registered and logged in, app allows user:
- to send messages to other users
- to view messages received by the user
- to delete received messages.

# FLAW 1:
https://github.com/serbrio/mooc_csb_2025/blob/project_I/Project_I/djangotutorial/web_sms/views.py#L67 (Line 67 in views.py)

There is no check in the application, if a user is authorized to delete a message.

Though a user can not see in the web page messages addressed to other users, 
he can try to delete them.

For example, after user ***test7*** has logged in and sent/deleted a message, he obtains [csfrmiddlewaretoken](screenshots/flaw-1-before-1.png), and in a cookie, [sessionid and csrftoken](screenshots/flaw-1-before-2.png), which he can use in POST requests to the app to attempt deletion.

User ***test7*** has no received messages, as shown on the web page.\
Here are all messages currently saved in the database: [messages](screenshots/flaw-1-before-4.png).\ 
User ***test7*** has ***id=7***, which is not among the ***receiver_id***s.\ 
For convenience, in this example, text of every message is descriptive: "from userN to userK".

User is able to delete any message, even if it is not addressed to him, just guessing its ***id*** and providing previously obtained tokens and sessionid.

For example, to delete message with ***id=12***, he does the following:
```
curl -X POST http://127.0.0.1:8000/web_sms/delete_message/ -H "Cookie: csrftoken=F6OFlgxFYtrLu5GQGph2x910uIDR9xvN; sessionid=2wiig7eafg80eps326e8ngalvc6npdth" -d "csrfmiddlewaretoken=InINKoAEPdOJH5JUJJOyia9cYbZ5W3HFdjmiVuX9Dw5k10fAfYVqF902iJsMVq2i&message_id=12"
```
As result, [message is deleted](screenshots/flaw-1-before-6.png).

## Fix
To fix the flaw, add check if the user who requested deletion has access to the message, i.e. if the user and the receiver of the message are the same person.
https://github.com/serbrio/mooc_csb_2025/blob/project_I/Project_I/djangotutorial/web_sms/views.py#L70 (Line 70 in views.py)

Attempt to delete message with ***id=23***:
```
curl -X POST http://127.0.0.1:8000/web_sms/delete_message/ -H "Cookie: csrftoken=F6OFlgxFYtrLu5GQGph2x910uIDR9xvN; sessionid=2wiig7eafg80eps326e8ngalvc6npdth" -d "csrfmiddlewaretoken=InINKoAEPdOJH5JUJJOyia9cYbZ5W3HFdjmiVuX9Dw5k10fAfYVqF902iJsMVq2i&message_id=23"
```
Attempt failed: [message is not deleted](screenshots/flaw-1-after-2.png).

References: [A Broken Access Control](https://owasp.org/Top10/A01_2021-Broken_Access_Control/).

# FLAW 2:
https://github.com/serbrio/mooc_csb_2025/blob/project_I/Project_I/djangotutorial/web_sms/forms.py#L7 (Line 7 in forms.py)

Application permits weak, or well-known passwords.

User can be registered with a weak password, for example, [root/root](screenshots/flaw-2-before-1.png),
can successfully [login](screenshots/flaw-2-before-2.png) and [use](screenshots/flaw-2-before-3.png) application.

## Fix
In application, the following password validators are activated by default: 
- UserAttributeSimilarityValidator
- MinimumLengthValidator
- CommonPasswordValidator
- NumericPasswordValidator

To fix the flaw, add password validation to the registration form, i.e. reimplement the clean() method of the form:
https://github.com/serbrio/mooc_csb_2025/blob/project_I/Project_I/djangotutorial/web_sms/forms.py#L11 (Line 11 in forms.py).

As there is custom "Account" model in the application, to make password validation work, add property **password_validator_target** to the model, which will be checked by validator:
https://github.com/serbrio/mooc_csb_2025/blob/project_I/Project_I/djangotutorial/web_sms/models.py#L13 (Line 13 in models.py).

Make UserAttributeSimilarityValidator to check property **password_validator_target** of the "Account" model:
https://github.com/serbrio/mooc_csb_2025/blob/project_I/Project_I/djangotutorial/mysite/settings.py#L94 (Line 94 in settings.py).\
Optionally: fine tune the **max_similarity** option of the validator.

After fix, weak passwords (or credential pairs) are not accepted with the appropriate error messages:
- [root/root](screenshots/flaw-2-after-1.png): too similar, too short, too common;
- [password: 123123123](screenshots/flaw-2-after-2.png): too common, entirely numeric;
- [test200/test123123](screenshots/flaw-2-after-3.png): too similar;
- [test200/qwe](screenshots/flaw-2-after-4.png): too short, too common.

References: [Identification and Authentication Failures](https://owasp.org/Top10/A07_2021-Identification_and_Authentication_Failures/), [password-management-in-django](https://docs.djangoproject.com/en/5.2/topics/auth/passwords/#password-management-in-django), [using-forms-to-validate-data](https://docs.djangoproject.com/en/5.2/ref/forms/api/#using-forms-to-validate-data), [validating-fields-with-clean](https://docs.djangoproject.com/en/5.2/ref/forms/validation/#validating-fields-with-clean), [Learn_web_development: Django](https://developer.mozilla.org/en-US/docs/Learn_web_development/Extensions/Server-side/Django), [attribute_similarity_authentication_fails](https://www.reddit.com/r/django/comments/8tyhhe/attribute_similarity_authentication_fails/).

# FLAW 3:

## Fix