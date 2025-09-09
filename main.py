import imaplib
import email
import os
import json
import sys

script_dir = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(script_dir, "data.json")
with open(file_path, "r", encoding="utf-8") as f:
    d = f.read()
    data = json.loads(d)

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

imap = imaplib.IMAP4_SSL("imap.gmail.com")

def print_line():
    print("---------------------------")

def try_login():
    try:
        imap.login(data["email"], password = data["imap_pass"])
    except:
        print(f"{ansicolors.FAIL}Login Credentials are incorrect. again. Make sure you are using a gmail account and a valid app password (From https://myaccount.google.com/apppasswords).{ansicolors.ENDC}")
        return get_data()

def get_data():
    mail = input("please Enter your Gmail adress: ")
    if mail[-10:] != "@gmail.com":
        print(f"{ansicolors.FAIL}The mail you just entered is not valid. Currently we support only Gmail acoounts.{ansicolors.ENDC}")
        return get_data()
    data["email"] = mail
    pw = input("Please enter your IMAP password: ")
    if not pw:
        return get_data()
    data["imap_pass"] = pw
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    try_login()

if data["email"] == "":
    print(f"{ansicolors.FAIL}You have not entered your email credentials.{ansicolors.ENDC}")
    get_data()
else:
    try_login()


imap.select('"INBOX"')
status, messages = imap.search(None, 'ALL')

print_line()

def commands():
    print("""Welcome to emailcli. Here are the commands:
    c: Shows commands.
    Enter: Show the current page again. Default is 1.
    r: Reloads the pages
    x: Next page
    z: Previous page
    q: exit the program
    mpp <number>: Sets the number of mails will be shown per page.
    Number: Go to specified page""")
    print_line()
commands()

def await_input():
    return input("Enter command:")

page = 1

def print_results():
    global page
    global status
    global messages
    input = await_input()
    print_line()
    if input == "x":
        page = page + 1
    elif input == "z" and page != 1:
        page = page - 1
    elif input == "z" and page == 1:
        pass
    elif input == "r":
        imap.select('"INBOX"')
        status, messages = imap.search(None, 'ALL')
    elif input == "c":
        commands()
        print_results()
    elif input == "":
        pass
    elif input == "q":
        print("Logged Out!")
        imap.logout()
        print_line()
        sys.exit()
    elif input[:3] == "mpp":
        try:
            input = input.split()
        except:
            print(f"{ansicolors.FAIL}Unexpected command. Example usage 'mpp 5'.{ansicolors.ENDC}")
            print_line()
            return print_results()
        try:
            data["mails_per_page"] = int(input[1])
        except:
            print(f"{ansicolors.FAIL}Unexpected command. Example usage 'mpp 5'.{ansicolors.ENDC}")
            print_line()
            return print_results()
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
    else:
        try:
            page = int(input)
        except:
            print(f"{ansicolors.FAIL}'{input}' command not found.{ansicolors.ENDC}")
            print_line()
            print_results()
    
    start = page * data["mails_per_page"] - (data["mails_per_page"] - 1)
    end = page * data["mails_per_page"] + 1
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
            print_line()
    except:
        print(f"{ansicolors.FAIL}The number of page you just entered doesn't exist. Please provide another one!{ansicolors.ENDC}")
    print_results()
    print_line()

print_results()

print("Logged Out!")
imap.logout()
print_line()
