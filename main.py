import os
import re
from candidate_selection import get_outstanding_contributions, get_all_contributions
from similarity import filter_candidates

# Get proposal title
proposal_title = os.getenv("PROPOSAL_TITLE")
#Replace newline chars with spaces
proposal_title = proposal_title.replace("\n", ' ')
#Remove double spaces
proposal_title = re.sub("\s\s+", " ", proposal_title)
#Remove all leading and trailing spaces
proposal_title = proposal_title.strip()
# Path for workflow
path_repo = os.getenv("GITHUB_WORKSPACE")
#path_repo = 'C:\\Users\\marce\\Documents\\work\\KTH\Devops\\similar-contributions'
repo_owner = os.getenv("GITHUB_REPOSITORY")
#repo_owner = "KTH/devops-course"
branch = os.getenv("GITHUB_BASE_REF")
#branch = "main"
cont_folder = os.getenv("INPUT_SEARCH_DIR")
#cont_folder = "attic"
allowed_types = os.getenv("INPUT_FILTER_TYPE").strip("[] \n").split(", ")
allowed_types = [t.strip("\'") for t in allowed_types]
#allowed_types = ["essay", "course-automation", "demo", "presentation", "executable-tutorial", "tutorial", "open-source", "open"]
allowed_years = os.getenv("INPUT_FILTER_YEAR").strip("[] \n").split(", ")
allowed_years = [t.strip("\'") for t in allowed_years]
#allowed_types = ["2019", "2020", "2021"]
extra_stopwords = os.getenv("INPUT_EXTRA_STOPWORDS").strip("[] \n").split(", ")
extra_stopwords = [t.strip("\'") for t in extra_stopwords]
min_sim = float(os.getenv("INPUT_MIN_WORD_SIMILARITY"))
sort_option = os.getenv("INPUT_SORT_OPTION")

#Print some debug info
print(f"GITHUB_WORKSPACE = {os.getenv('GITHUB_WORKSPACE')}")
print(f"GITHUB_REPOSITORY = {os.getenv('GITHUB_REPOSITORY')}")
print(f"GITHUB_BASE_REF = {os.getenv('GITHUB_BASE_REF')}")
print(f"INPUT_SEARCH_DIR = {os.getenv('INPUT_SEARCH_DIR')}")
print(f"INPUT_FILTER = {os.getenv('INPUT_FILTER')}")
print(f"allowed types: {allowed_types}")
print(f"allowed_years: {allowed_years}")
print(f"min_sim: {min_sim}")
print(f"proposal_title: {proposal_title}")
print(f"sort_option: {sort_option}")

#######################
# CANDIDATE SEARCHING #
#######################

path_contributions = os.path.join(path_repo, cont_folder)
# Get candidate from outstanding contributions
outstanding_contributions = get_outstanding_contributions(path_contributions, allowed_types, allowed_years)
# Get candidate from all contributions
all_contributions = get_all_contributions(cont_folder, allowed_types, allowed_years)
# Also regard contributions of current course round as candidates
all_contributions += get_all_contributions("contributions", allowed_types, ["contributions"])

# Remove duplicates
out_seen = set()
all_seen = set()
out_contributions_unique = []
all_contributions_unique = []
for c in outstanding_contributions:
    if not c["title"] in out_seen:
        out_seen.add(c["title"])
        out_contributions_unique.append(c)
for c in all_contributions:
    if not c["title"] in all_seen:
        all_seen.add(c["title"])
        all_contributions_unique.append(c)
outstanding_contributions = out_contributions_unique
all_contributions = all_contributions_unique

print("Outstanding candidate contributions:")
for c in outstanding_contributions:
    print(c)
print("\n")

#######################
# CANDIDATE SELECTION #
#######################

# Filter candidates based on similarity to proposal title
outstanding_conts_final = filter_candidates(proposal_title, outstanding_contributions, min_sim, extra_stopwords)
all_conts_final = filter_candidates(proposal_title, all_contributions, min_sim, extra_stopwords)

#######################
#  GENERATE CONMMENT  #
#######################
output = """## Reading Recommendations
Based on your proposal title, we have found the following contributions from previous years highlighted as "outstanding" works. Hopefully, they can serve as inspiration.\n"""
for c in outstanding_conts_final:
    output += f"- [{c['title']}]({c['url']}) \[{c['type']}\]\n"

output += "\n## Similar topics found by comparing to all previous contributions:\n\n"

if(sort_option == "sort_by_keywords"):
    token_set = set([])
    for c in all_conts_final:
        for token in c['matching_token']:
            token_set.add(token)
    token_list = list(token_set)

    for token in token_list:
        output += f"#### {token}:\n"
        for c in all_conts_final:
            if token in c['matching_token']:
                url = f"https://github.com/{repo_owner}/tree/{branch}/{c['relative_url']}"
                output += f"- [{c['title']}]({url})  \[{c['type']}\]\n" 

elif(sort_option == "no_sorting"):
    pass
else:
    for c in all_conts_final:
        
        url = f"https://github.com/{repo_owner}/tree/{branch}/{c['relative_url']}"
        output += f"- [{c['title']}]({url})  \[{c['type']}\]\n"

#######################
#    WRITE CONMMENT   #
#######################
# Write similar contributions to file that can be read from the github workflow
# and then turned into a PR comment

path_output = os.path.join(path_repo, "generated_comment.md")
with open(path_output, "w", encoding="utf8") as f:
    f.write(output)
print(f"Output generated at: {path_output}")

# TODO: Format output in a way that shows which recommendations relate to which part of the title?
# TODO: Make sure to not include duplicates
