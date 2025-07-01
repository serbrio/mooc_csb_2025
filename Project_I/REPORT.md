LINK: https://github.com/serbrio/mooc_csb_2025.git

Installation instructions:
```
python manage.py migrate
```

Short description of the web application
After user have registered and logged in, app allows user:
- to send messages to other users
- to view messages received by the user
- to delete received messages.

# FLAW 1:
https://github.com/serbrio/mooc_csb_2025/blob/project_I/Project_I/djangotutorial/web_sms/views.py#L67 (Line 67 in views.py)

[A Broken Access Control](https://owasp.org/Top10/A01_2021-Broken_Access_Control/) Flaw 
There is no check in the application, if a user is authorized to delete a message.

Though a user can not see in the web page messages addressed to other users, 
he can try to delete them.

For example, after user **test7** has logged in and sent/deleted a message, he obtains [csfrmiddlewaretoken](screenshots/flaw-1-before-1.png), and in a cookie, [sessionid and csrftoken](screenshots/flaw-1-before-2.png), which he can use in POST requests to the app to attempt deletion.

User **test7** has no received messages, as shown on the web page.
Here are all messages currently saved in the database: [messages](screenshots/flaw-1-before-4.png). 
User **test7** has **id=7**, which is not among the **receiver_id**s. 
For convenience, in this example, text of every message is descriptive: "from userN to userK".

User is able to delete any message, even if it is not addressed to him, just guessing its **id** and providing previously obtained tokens and sessionid.

For example, to delete message with **id=12**, he does the following:
```
curl -X POST http://127.0.0.1:8000/web_sms/delete_message/ -H "Cookie: csrftoken=F6OFlgxFYtrLu5GQGph2x910uIDR9xvN; sessionid=2wiig7eafg80eps326e8ngalvc6npdth" -d "csrfmiddlewaretoken=InINKoAEPdOJH5JUJJOyia9cYbZ5W3HFdjmiVuX9Dw5k10fAfYVqF902iJsMVq2i&message_id=12"
```
As result, [message is deleted](screenshots/flaw-1-before-6.png).

## Fix:
https://github.com/serbrio/mooc_csb_2025/blob/project_I/Project_I/djangotutorial/web_sms/views.py#L70 (Line 70 in views.py)

To fix the flaw, we need to check if the user who requested deletion has access to the message, i.e. if the user and the receiver of the message are the same person.

Attempt to delete message with **id=23**:
```
curl -X POST http://127.0.0.1:8000/web_sms/delete_message/ -H "Cookie: csrftoken=F6OFlgxFYtrLu5GQGph2x910uIDR9xvN; sessionid=2wiig7eafg80eps326e8ngalvc6npdth" -d "csrfmiddlewaretoken=InINKoAEPdOJH5JUJJOyia9cYbZ5W3HFdjmiVuX9Dw5k10fAfYVqF902iJsMVq2i&message_id=23"
```
Attempt failed: [message is not deleted](screenshots/flaw-1-after-2.png).

# FLAW 2:


