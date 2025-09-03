import imaplib
import email
import os
import json

script_dir = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(script_dir, "login.json")
with open(file_path) as f:
    d = f.read()
    login_credentials = json.loads(d)

imap = imaplib.IMAP4_SSL("imap.gmail.com")

imap.login(login_credentials["email"], password =  login_credentials["imap_pass"])

imap.select('"INBOX"')
status, messages = imap.search(None, 'ALL')

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
print("---------------------------")
print("""Welcome to emailcli. Here are the commands:
Enter: Show the current page again. Default is 1.
x: Next page
z: Previous page
q: exit the programme
Number: Go to specified page""")
print("---------------------------")

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
    elif input == "":
        pass
    elif input == "q":
        return
    else:
        page = int(input)
    start = page * 5 - 4
    end = page * 5 + 1
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
    print_results()
        
print_results()

print("Logged Out!")
imap.logout()
print("---------------------------")
