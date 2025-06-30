LINK: https://github.com/serbrio/mooc_csb_2025.git

(Installation instructions?)

FLAW 1:
https://github.com/serbrio/mooc_csb_2025/blob/project_I/Project_I/djangotutorial/web_sms/views.py#L1 (Line 1 in views.py)

curl -X POST http://127.0.0.1:8000/web_sms/delete_message/ -H "Cookie: csrftoken=8tnBWPOftNCcVHNxn4iliRO4JlIM2dHS; sessionid=9fkjqe5rhcnvmbsx1xtnj4dgw542e91l" -v -d "csrfmiddlewaretoken=XFSimlhWl9hGNy8296BGZNLbIQyrWUYLVY5J80V1EMJIy5Lpm0JR7up5h163OXvt&message_id=18"

How to fix:
https://github.com/serbrio/mooc_csb_2025/blob/project_I/Project_I/djangotutorial/web_sms/views.py#L70 (Line 70 in views.py)

