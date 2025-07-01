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

FLAW 1:
https://github.com/serbrio/mooc_csb_2025/blob/project_I/Project_I/djangotutorial/web_sms/views.py#L67 (Line 67 in views.py)

Description:
[A Broken Access Control](https://owasp.org/Top10/A01_2021-Broken_Access_Control/) Flaw 
There is no check in the application, if a user is authorized to delete a message.
Though user can not see messages in the web page addressed to other users, 
he/she can try to delete them.
For example, after user **test7** has logged in and sent/deleted a message, he/she obtains [csfrmiddlewaretoken](screenshots/flaw-1-before-1.png), and in cookie, [sessionid and csrftoken](screenshots/flaw-1-before-2.png).
In this case, user **test7** has no received messages.



curl -X POST http://127.0.0.1:8000/web_sms/delete_message/ -H "Cookie: csrftoken=8tnBWPOftNCcVHNxn4iliRO4JlIM2dHS; sessionid=9fkjqe5rhcnvmbsx1xtnj4dgw542e91l" -v -d "csrfmiddlewaretoken=XFSimlhWl9hGNy8296BGZNLbIQyrWUYLVY5J80V1EMJIy5Lpm0JR7up5h163OXvt&message_id=18"

How to fix:
https://github.com/serbrio/mooc_csb_2025/blob/project_I/Project_I/djangotutorial/web_sms/views.py#L70 (Line 70 in views.py)

