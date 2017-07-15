# emailvalidator - speedy email validation

## Background

This is a little project I did for a client on UpWork. If you need help with a project with Python, Django, JavaScript, email me: `hgezim [at] gmail.com`.

## Description

Validate email addresses using [Email Verifier App](http://emailverifierapp.com/) API using multiple threads to speed up the process.

This can be used for email addresses you collect to ensure they're not garbage but are actually valid emails addresses.

![demo.gif](demo.gif)

## Installation and Usage

 Requires: Python 3

 ```
 $ pip install -r requirements.txt

 $ python emailvalidator.py
```

It first asks you for the number of threads you'd like to use to get this done. If you select 2 threads, it means 2 emails will be valiated at the same time, and so on. If you select too many threads, the Email Verifier App servers may start telling you to back off. Default is 5 threads.

It then asks you for a CSV file that needs to be in the current directory. The format can be like this:

```
name@example.com
name1@excample.com;My Name is Joe
name2@example.com
```

The script will create a file named `<old-file-name-without-extension>-valid.<extension>`. So, if the CSV you entered is `emails.txt`, it will store valid emails in `emails-valid.txt`