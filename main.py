import sys
import requests
from bs4 import BeautifulSoup
#----------------------------------------------------------------------------------------------
sys.stdin = open("input.txt","r")
sys.stdout = open("output.txt","w",encoding='utf-8')
sys.stderr = open("error.txt","w")

# Receive the input as a list 
enter = sys.stdin.readlines()                                                       
# Start a session
session = requests.Session()                                                       

# Declaration of functions ------------------------------------------------------------------------------------
# Get the solved problems for given handle
def solved_for_handle(handle):
    # Enter the status page and get it decoded as html and find number of pages of submissions                        
    User_URL = f"https://codeforces.com/submissions/{handle}/page/1"        
    get = session.get(User_URL)                                         
    soup = BeautifulSoup(get.content,'html5lib')                                  
    body = soup.find_all('tr')[1:-1]     
    problems = set()
    lastPageIndex = 1
    page = 1
    # Handle no pages case
    try:
        lastPageIndex = soup.find_all('span', {'class':"page-index"})[-1].text
    except:
        problem_details = body[0].find_all('td')
        if len(problem_details) == 1:
            return problems
    
    # Get all accepted problem in all pages
    while page <= int(lastPageIndex):
        for problem in body:
            problem_details = problem.find_all('td')
            problem_truth = problem_details[5].find('span')['submissionverdict']
            if problem_truth == 'OK':
                problem_name = problem_details[3].find('a').text.strip().strip('\n').split('-')
                problem_name = '-'.join(problem_name[1:]).strip()
                problems.add(problem_name)
        page += 1
        User_URL = f"https://codeforces.com/submissions/{handle}/page/{page}"         
        get = session.get(User_URL)                                                      
        soup = BeautifulSoup(get.content,'html5lib')                 
        body = soup.find_all('tr')[1:-1]               
    return problems

# combine all solved problems for each handle in a dictionary
def solved_problems_for_all(handles):                                        
    accepted = dict()                                                         
    for handle in handles:
        # for every handle get solved problems
        for_handle = solved_for_handle(handle.strip('\n'))
        accepted[handle.strip('\n')] = for_handle 
    return accepted

# Get Csrf tooken to use it in login
def getCsrf(URL:str):
    auth = session.get(URL).content
    soup = BeautifulSoup(auth, 'html.parser')
    csrf = soup.find('input')['value']
    return csrf

# login to codeforces with given handle and password
def login(handle, password):
    URL = "https://codeforces.com/enter"
    session.get(URL)
    csrf_token_login = getCsrf(URL)

    login_data = {
        'action' : 'enter',
        'handleOrEmail' : handle,
        'password' : password,
        'csrf_token' : csrf_token_login,
        'remember' : 'on'
    }
    headers = {
        'X-Csrf-Token' : csrf_token_login
    }
    request = session.post(URL,data=login_data,headers=headers)
    return check_login(request)

# Check login information validity
def check_login(request):
    soup = BeautifulSoup(request.content, 'html5lib')
    status = soup.find('body').find('div', {'id': 'header'}).find_all('a')[-1].text
    if status == 'Logout':
        return True
    return False

self_handle,password = enter[0].strip('\n').split()
validity = login(self_handle,password)
#  Handle login error
if not validity:
    print('Incorrect Password or Username')
    quit()
print(solved_problems_for_all(enter[1:]))