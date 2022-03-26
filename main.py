import os
import re
from outstanding import get_selected_contributions
from similarity import filter_candidates


# Path for workflow
path_repo = os.getenv("GITHUB_WORKSPACE")

# Path local
#path_repo = 'C:\\Users\\Marcel\\Documents\\working\\Uni\\KTH\\DevOps\\devops-course'
proposal_title = 'React CI testing' # TODO: Get from environment

# Get candidate contributions
selected_contributions = get_selected_contributions(path_repo)
pr_contributions = [] #get_pr_contributions() # TODO
print("Candidate contributions:")
for c in selected_contributions:
    print(c)
print("\n")

# Filter candidates based on similarity to proposal title
selected_conts_final = filter_candidates(proposal_title, selected_contributions)
pr_conts_final = [] #filter_candidates(candidates=pr_contributions) # TODO

# Write similar contributions to file that can be read from the github workflow
# and then turned into a PR comment
output = """## Reading Recommendations
There are many good contributions from the last years that can help as inspiration of how to create a high quality contribution yourself.
Based on your proposal title, I have found the following outstanding previous student works that could be interesting to you:

"""
for c in selected_conts_final:
    output += f"- [{c['title']}]({c['url']})\n"

path_output = os.path.join(path_repo, "generated_comment.md")
with open(path_output, "w", encoding="utf8") as f:
    f.write(output)
print(f"Output generated at: {path_output}")

