import os

print("Hello from Python!")
print("Environment variable REPO_FULLNAME == %s"%os.getenv("REPO_FULLNAME"))
print("Git repo path == %s"%os.getenv("GITHUB_WORKSPACE"))
print("Content:")
print(os.listdir(os.getenv("GITHUB_WORKSPACE")))
