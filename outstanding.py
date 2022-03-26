import os
import re

def is_heading(line):
    """
    Checks whether a given line in a README.md file represents a heading
    """
    return len(line.strip()) >= 1 and line.strip()[0] == "#"


def get_section_label(line):
    """
    Given a heading from a README.md file, returns one out of two labels:
    'irrelevant-section' or 'student-contributions'. The latter indicates that
    candidate contributions can be extracted in this section.
    """
    if ("outstanding student achievements" in line.lower() or
        "selected student works" in line.lower()):
        return "student-contributions"
    else:
        return "irrelevant-section"


def get_candidates_from(path_readme):
    """
    Extracts all the candidate contributions from a given README.md file
    that bundles all the selected contributions from a specific year
    """
    candidates = []
    with open(path_readme, "r", encoding="utf8") as f:
        for line in f.readlines():
            if is_heading(line):
                cur_section = get_section_label(line)
            if cur_section == "student-contributions":
                candidates = update_candidates(line, candidates)
    return candidates

    
def update_candidates(line, candidates):
    """
    Checks whether the line represents a contribution
    and adds it to the list of candidates.
    """
    pattern = ".*\*.*\[(.*)\]\((.*)\)"
    m = re.match(pattern, line.strip())
    if m:
        candidates.append({
            "title": m.group(1),
            "url": m.group(2)
        })
    return candidates

def find_readme(path_year):
    """
    Returns the path to the README file in the path_year folder
    that represents the README of the respective year.
    If none exists, return an empty string.
    """
    if os.path.isdir(path_year):
        for file in os.listdir(path_year):
            if "readme" in file.lower():
                return os.path.join(path_year, file)
    return ""

def get_selected_contributions(path_repo):
    """
    Extracts candidate contributions from a given folder.
    This method assumes that the given folder contains subfolder with
    README files from which the contributions should be extracted.
    """
    #path_contributions = os.path.join(path_repo, os.getenv("TODO"))
    path_contributions = os.path.join(path_repo, "attic")

    candidates_all = []
    for folder in os.listdir(path_contributions):
        path_year =  os.path.join(path_contributions, folder)
        if os.path.isdir(path_year):
            path_readme = find_readme(path_year)
            if path_readme:
                candidates_all += get_candidates_from(path_readme)
    return candidates_all
