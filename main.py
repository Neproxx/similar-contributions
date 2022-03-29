import os
import re
from candidate_selection import get_outstanding_contributions, get_all_contributions
from similarity import filter_candidates

proposal_title = 'React CI testing' # TODO: Get from environment

# Path for workflow
path_repo = os.getenv("GITHUB_WORKSPACE")
#repo_owner = os.getenv("GITHUB_REPOSITORY")
cont_folder = "attic" # TODO -> ENV
branch = "2022" # TODO
#path_repo = 'C:\\Users\\Marcel\\Documents\\working\\Uni\\KTH\\DevOps\\devops-course'
repo_owner = "KTH/devops-course"

#path_contributions = os.path.join(path_repo, os.getenv("TODO"))
path_contributions = os.path.join(path_repo, cont_folder)

# Get candidate contributions
outstanding_contributions = get_outstanding_contributions(path_contributions)
all_contributions = get_all_contributions(path_contributions)
#print("Candidate contributions:")
#for c in outstanding_contributions:
#    print(c)
#print("\n")

# Filter candidates based on similarity to proposal title
outstanding_conts_final = filter_candidates(proposal_title, outstanding_contributions)
all_conts_final = filter_candidates(proposal_title, candidates=all_contributions)

# Write similar contributions to file that can be read from the github workflow
# and then turned into a PR comment
output = """## Reading Recommendations
There are many good contributions from the last years that can help as inspiration of how to create a high quality contribution yourself. Based on your proposal title, I have found the following outstanding previous student works that could be interesting to you:

"""
for c in outstanding_conts_final:
    output += f"- [{c['title']}]({c['url']})\n"

output += "\n## Similar topics found by comparing to all previous contributions:\n\n"

for c in all_conts_final:
    url = f"https://github.com/{repo_owner}/tree/{branch}/{cont_folder}/{c['relative_url']}"
    output += f"- [{c['title']}]({url})\n"

path_output = os.path.join(path_repo, "generated_comment.md")
with open(path_output, "w", encoding="utf8") as f:
    f.write(output)
print(f"Output generated at: {path_output}")

# TODO: Format output in a way that shows which recommendations relate to which part of the title?
# TODO: Make sure to not include duplicates
