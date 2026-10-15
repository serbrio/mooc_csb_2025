# Cyber Security Base 2025: Project I

This is my project for the course Cyber Security Base 2025 (MOOC, University of Helsinki).\
It demonstrates some cyber security flaws of different types in a Django web application and shows how to mitigate them.

## Analyzed Flaws

**Broken access control** \
There is no check in the application, if a user is authorized to delete a message.

**Identification and Authentication Failures** \
Application permits weak, or well-known passwords.

**Injection (SQL)** \
Application does not prevent SQL injection attacks.

**Insecure design** \
Password recovery workflow includes "questions and answers", which can not be trusted as evidence of identity because more than one person can know the answers.

**Cryptographic Failures** \
Sensitive data (in this case, private messages) not encrypted at rest, allowing an attacker to retrieve this data using, for examle, SQL injection flaws.


More details: [REPORT.md](Project_I/REPORT.md)
