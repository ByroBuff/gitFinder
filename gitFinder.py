import argparse
import requests
import time

# ANSI color codes
RESET = "\033[0m"
RED = "\033[31m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
CYAN = "\033[36m"
MAGENTA = "\033[35m"

DEBUG = False

class FindGitEmail:
    def __init__(self, username):
        self.git_username = username
        self.apiURL = "https://api.github.com"

    def get(self):
        return self.__checkUserExists()

    def __checkUserExists(self):
        response = requests.get(self.apiURL + "/users/" + self.git_username)
        response_json = response.json()

        if response.status_code == 200:
            start_time = time.time()
            emails = self.__getEmail()
            execution_time = "{:.2f}s".format(time.time() - start_time)
            return {'found': True, 'execution_time': execution_time, 'email': emails}
        elif str(response_json["message"]).startswith("API"):
            return {'found': False, 'error_message': str(response_json["message"] + " Documentation URL: " + response_json["documentation_url"])}
        else:
            return {'found': False, 'error_message': "Provided GitHub username: " + self.git_username + " does not exist."}

    def __getEmail(self):
        email_sources = {}

        reposURL = self.apiURL + "/users/" + self.git_username + "/repos"
        repos = requests.get(reposURL).json()

        for repo in repos:
            repo_name = repo["name"]
            if repo["fork"] is False:
                commitsURL = self.apiURL + "/repos/" + self.git_username + "/" + repo_name + "/commits"
                commits = requests.get(commitsURL).json()

                for commit in commits:
                    try:
                        if commits["message"] == "Git Repository is empty.":
                            continue
                    except:
                        try:
                            commit_email = commit["commit"]["author"]["email"]
                            commit_name = commit["author"]["login"]
                        except TypeError as e:
                            # rate limit exceeded
                            # notify the user
                            if DEBUG:
                                print(RED + str(e) + RESET)
                        if commit_email not in email_sources:
                            email_sources[commit_email] = []
                        email_sources[commit_email].append(f'Repo: https://www.github.com/{self.git_username}/{repo_name}, User: {commit_name}')

        if len(email_sources) != 0:
            return email_sources

        commitsURL = self.apiURL + "/users/" + self.git_username + "/events/public"
        payloads = requests.get(commitsURL).json()

        for payload in payloads:
            if payload["type"] == "PushEvent":
                data = payload["payload"]
                payload_email = str(data["commits"][0]["author"]["email"])
                payload_name = str(data["actor"]["login"])
                if payload_email not in email_sources:
                    email_sources[payload_email] = []
                email_sources[payload_email].append(f'Public Commit, User: {payload_name}')

        return email_sources

def find(username):
    finder_response = FindGitEmail(username).get()
    return finder_response

def main():
    parser = argparse.ArgumentParser(description="Find GitHub user's email(s)")
    parser.add_argument("username", help="GitHub username to search for")
    parser.add_argument("-m", "--masked", action="store_true", help="Show masked emails as well (@users.noreply.github.com emails)")
    parser.add_argument("-s", "--sources", action="store_true", help="Show sources of emails ")
    parser.add_argument("-u", "--user", action="store_true", help="Only show emails linked directly to the specified account (no cross-commits)")
    parser.add_argument("-o", "--output", help="Output results to file")
    
    args = parser.parse_args()

    username = args.username
    hidden = args.masked
    user = args.user

    if args.user and not args.sources:
        print(RED + "Error: -u/--user requires -s/--sources to be enabled" + RESET)
        exit(1)

    response = find(username)

    if response['found'] is False:
        print(RED + response['error_message'] + RESET)
        exit(1)

    email_sources = response['email']

    if not hidden:
        email_sources = {email: sources for email, sources in email_sources.items() if not email.endswith('@users.noreply.github.com')}

    if response['found']:

        if not args.sources:
            for email in email_sources:
                print(CYAN + f"Email: {email}" + RESET)
        else:

            # Filter emails based on the specified user
            if user:
                email_sources = {email: sources for email, sources in email_sources.items() if any(f'User: {username}' in source for source in sources)}

            # Update the count of found emails
            num_found_emails = len(email_sources)

            print(GREEN + f"Found {num_found_emails} email{'s' if num_found_emails != 1 else ''} for GitHub user: {username}" + RESET)
            
            # Rest of your code remains the same
            if num_found_emails == 0 and not hidden:
                print(YELLOW + "Use --hidden to show any hidden emails (@users.noreply.github.com emails)\n" + RESET)
                exit(0)

            for email, sources in email_sources.items():
                # clear out any duplicate sources
                sources = list(dict.fromkeys(sources))
                # print email and sources
                if args.sources:
                    print(CYAN + f"Email: {email}" + RESET)
                    print("Sources:")
                    for source in sources:
                        print(MAGENTA + f"  - {source}" + RESET)
                    print()
    else:
        print(RED + f"Error: {response['error_message']}" + RESET)

    if args.output:
        with open(args.output, 'w') as f:
            for email, sources in email_sources.items():
                # clear out any duplicate sources
                sources = list(dict.fromkeys(sources))
                # print email and sources
                f.write(f"Email: {email}\n")
                if args.sources:
                    f.write("Sources:\n")
                    for source in sources:
                        f.write(f"  - {source}\n")
                    f.write("\n")

if __name__ == "__main__":
    main()