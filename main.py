import imaplib
import email
import os
import json
import sys

script_dir = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(script_dir, "login.json")
with open(file_path, "r", encoding="utf-8") as f:
    d = f.read()
    login_credentials = json.loads(d)

class ansicolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

print(login_credentials["email"][-10:])

def get_credentials():
    mail = input("please Enter your Gmail adress: ")
    if mail[-10:] != "@gmail.com":
        print(f"{ansicolors.FAIL}The mail you just entered is not valid. Currently we support only Gmail acoounts.{ansicolors.ENDC}")
        return get_credentials()
    login_credentials["email"] = mail
    pw = input("Please enter your IMAP password: ")
    if not pw:
        return get_credentials()
    login_credentials["imap_pass"] = pw
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(login_credentials, f, ensure_ascii=False, indent=4)
    try:
        imap.login(login_credentials["email"], password = login_credentials["imap_pass"])
    except:
        print(f"{ansicolors.FAIL}Login Credentials are incorrect. again. Make sure you are using a gmail account and a valid app password (From https://myaccount.google.com/apppasswords).{ansicolors.ENDC}")
        get_credentials()

if login_credentials["email"] == "":
    print(f"{ansicolors.FAIL}You have not entered your email credentials.{ansicolors.ENDC}")
    get_credentials()

imap = imaplib.IMAP4_SSL("imap.gmail.com")

try:
    imap.login(login_credentials["email"], password = login_credentials["imap_pass"])
except:
    print(f"{ansicolors.FAIL}Login Credentials are incorrect. again. Make sure you are using a gmail account and a valid app password (From https://myaccount.google.com/apppasswords).{ansicolors.ENDC}")
    get_credentials()

imap.select('"INBOX"')
status, messages = imap.search(None, 'ALL')

print("---------------------------")

def commands():
    print("""Welcome to emailcli. Here are the commands:
    c: Shows commands.
    Enter: Show the current page again. Default is 1.
    x: Next page
    z: Previous page
    q: exit the programme
    Number: Go to specified page""")
    print("---------------------------")
commands()

def await_input():
    return input("Enter command:")

page = 1

def print_results():
    global page
    input = await_input()
    print("---------------------------")
    if input == "x":
        page = page + 1
    elif input == "z" and page != 1:
        page = page - 1
    elif input == "z" and page == 1:
        pass
    elif input == "c":
        commands()
        print_results()
    elif input == "":
        pass
    elif input == "q":
        print("Logged Out!")
        imap.logout()
        print("---------------------------")
        sys.exit()
    else:
        try:
            page = int(input)
        except:
            print(f"{ansicolors.FAIL}'{input}' command not found.{ansicolors.ENDC}")
            print("---------------------------")
            print_results()
    start = page * 5 - 4
    end = page * 5 + 1
    try:
        for i in range(start, end):
            num = messages[0].split()[::-1][i-1]

            _, msg = imap.fetch(num, "(RFC822)")
            message = email.message_from_bytes(msg[0][1])

            subject_header = message['Subject']
            decoded_subject = email.header.decode_header(subject_header)
            subject = decoded_subject[0][0]
            message_id = message['Message-ID']
            gmail_link = f"https://mail.google.com/mail/u/0/#search/rfc822msgid:{message_id[1:-1]}"

            if isinstance(subject, bytes):
                subject = subject.decode("utf-8")

            print(f"{ansicolors.HEADER}Subject:{ansicolors.ENDC}", ansicolors.WARNING + subject+ ansicolors.ENDC)
            print(f"{ansicolors.UNDERLINE}From:{ansicolors.ENDC}", message["From"])
            print(f"{ansicolors.UNDERLINE}Date:{ansicolors.ENDC}", message["Date"])
            print(f"{ansicolors.UNDERLINE}Gmail Link:{ansicolors.ENDC}", ansicolors.OKCYAN + gmail_link + ansicolors.ENDC)
            print("---------------------------")
    except:
        print(f"{ansicolors.FAIL}The number of page you just entered doesn't exist. Please provide another one!{ansicolors.ENDC}")
    print_results()
    print("---------------------------")

print_results()

print("Logged Out!")
imap.logout()
print("---------------------------")
