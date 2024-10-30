import requests
import pandas as pd

# GitHub API setup
GITHUB_TOKEN = 'generated_token_id'
HEADERS = {'Authorization': f'token {GITHUB_TOKEN}'}

def fetch_users(location="Bangalore", min_followers=100):
    # Fetch users in Bangalore with followers > 100
    users = []
    page = 1
    while True:
        url = f"https://api.github.com/search/users?q=location:{location}+followers:>{min_followers}&page={page}"
        response = requests.get(url, headers=HEADERS)
        data = response.json()
        if 'items' not in data:
            break
        for user in data['items']:
            # Get user details
            user_info = requests.get(user['url'], headers=HEADERS).json()
            users.append({
                "login": user_info['login'],
                "name": user_info.get('name', ''),
                "company": str(user_info.get('company', '')).lstrip('@').strip().upper(),
                "location": user_info.get('location', ''),
                "email": user_info.get('email', ''),
                "hireable": user_info.get('hireable', ''),
                "bio": user_info.get('bio', ''),
                "public_repos": user_info.get('public_repos', 0),
                "followers": user_info['followers'],
                "following": user_info['following'],
                "created_at": user_info['created_at']
            })
        page += 1
        if 'next' not in response.links:
            break
    return pd.DataFrame(users)

def fetch_repos(user_logins):
    repos = []
    for login in user_logins:
        page = 1
        while True:
            url = f"https://api.github.com/users/{login}/repos?sort=pushed&page={page}"
            response = requests.get(url, headers=HEADERS)
            data = response.json()
            if not data:
                break
            for repo in data[:500]:  # Limit to 500 repos per user
                repos.append({
                    "login": login,
                    "full_name": repo['full_name'],
                    "created_at": repo['created_at'],
                    "stargazers_count": repo['stargazers_count'],
                    "watchers_count": repo['watchers_count'],
                    "language": repo.get('language', ''),
                    "has_projects": repo['has_projects'],
                    "has_wiki": repo['has_wiki'],
                    "license_name": repo['license']['key'] if repo['license'] else ''
                })
            page += 1
            if 'next' not in response.links:
                break
    return pd.DataFrame(repos)

# Save data to CSV files
users_df = fetch_users()
users_df.to_csv('users.csv', index=False)

repos_df = fetch_repos(users_df['login'].tolist())
repos_df.to_csv('repositories.csv', index=False)
