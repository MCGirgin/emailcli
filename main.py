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

class color:
    PURPLE = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

imap = imaplib.IMAP4_SSL("imap.gmail.com")

def print_line():
    print("---------------------------")

def try_login():
    try:
        imap.login(data["email"], password = data["imap_pass"])
    except:
        print(f"{color.RED}Login Credentials are incorrect. again. Make sure you are using a gmail account and a valid app password (From https://myaccount.google.com/apppasswords).{color.END}")
        return get_data()

def get_data():
    mail = input("please Enter your Gmail adress: ")
    if mail[-10:] != "@gmail.com":
        print(f"{color.RED}The mail you just entered is not valid. Currently we support only Gmail acoounts.{color.END}")
        return get_data()
    data["email"] = mail
    pw = input("Please enter your IMAP password: ")
    if not pw:
        return get_data()
    data["imap_pass"] = pw
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    try_login()

if data["email"] == "" or data["imap_pass"] == "":
    print(f"{color.RED}You have not entered your email credentials.{color.END}")
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
    return
commands()

def await_input():
    return input("Enter command:")

page = 1

def next_page():
    global page
    page += 1

def previous_page():
    global page
    page = max(1,page - 1)

def reload():
    imap.select('"INBOX"')
    status, messages = imap.search(None, 'ALL')

def space():
    pass

def mails_per_page(input):
    try:
        input = input.split()
    except:
        print(f"{color.RED}Unexpected command. Example usage 'mpp 5'.{color.END}")
        print_line()
        return print_results()
    try:
        data["mails_per_page"] = int(input[1])
    except:
        print(f"{color.RED}Unexpected command. Example usage 'mpp 5'.{color.END}")
        print_line()
        return print_results()
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def logout():
    print("Logged Out!")
    imap.logout()
    print_line()
    sys.exit()

actions = {
    "x": next_page,
    "z": previous_page,
    "r": reload,
    "q": logout,
    "": space
}

def print_results():
    global page
    global status
    global messages
    input = await_input()
    print_line()
    if input[:3] == "mpp":
        mails_per_page(input)
    elif input == "c":
        commands()
        return print_results()
    elif input in actions:
        actions[input]()
    else:
        try:
            page = int(input)
        except:
            print(f"{color.RED}'{input}' command not found.{color.END}")
            print_line()
            return print_results()
    
    start = page * data["mails_per_page"] - (data["mails_per_page"] - 1)
    end = page * data["mails_per_page"] + 1
    try:
        print(f"{color.GREEN}PAGE NUMBER: {page}{color.END}")
        print_line()
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

            print(f"{color.PURPLE}Subject:{color.END}", color.YELLOW + subject+ color.END)
            print(f"{color.UNDERLINE}From:{color.END}", message["From"])
            print(f"{color.UNDERLINE}Date:{color.END}", message["Date"])
            print(f"{color.UNDERLINE}Gmail Link:{color.END}", color.CYAN + gmail_link + color.END)
            print_line()
    except:
        print(f"{color.RED}The number of page you just entered doesn't exist. Please provide another one!{color.END}")
        print_line()
    print_results()
    print_line()

print_results()

print("Logged Out!")
imap.logout()
print_line()
