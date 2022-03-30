import os
import re
from warnings import warn
from similarity import non_informant_words, punctuation

### Code for extracting candidates from "selected student works" README files
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
    if ("outstanding student achievements" in line or
        "selected student works" in line):
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
                cur_section = get_section_label(line.lower())
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

def get_outstanding_contributions(path_contributions):
    """
    Extracts candidate contributions from a year's readme file listing the outstanding ones.
    This method assumes that the given folder contains subfolders with
    README files from which the contributions should be extracted.
    """
    candidates_all = []
    for folder in os.listdir(path_contributions):
        path_year =  os.path.join(path_contributions, folder)
        if os.path.isdir(path_year):
            path_readme = find_readme(path_year)
            if path_readme:
                candidates_all += get_candidates_from(path_readme)
    return candidates_all

### Code for extracting candidates from the set of all contributions of a year
def get_all_contributions(path_contributions):
    """
    Extracts candidates from folders containing all contributions of the respective year.
    This method assumes that there is a subfolder for every year, which has another subfolder
    the name of which contains "contributions" which has a subfolder for every assignment type 
    which again have subfolders for every assignment which contain the README.md from which the
    information about the contribution can be extracted. In short, we assume a structure:
    path_contributions/<yyyy>/<contributions-yyyy>/<assignment-type>/<team-name>/README.md
    """
    candidates_all = []
    for year_folder in os.listdir(path_contributions):
        path_year = os.path.join(path_contributions, year_folder)
        if os.path.isdir(path_year):
            for cyear_folder in os.listdir(path_year):
                path_cyear = os.path.join(path_year, cyear_folder)
                if os.path.isdir(path_cyear):
                    for type_folder in os.listdir(path_cyear):
                        path_type = os.path.join(path_cyear, type_folder)
                        if os.path.isdir(path_type):
                            for team_folder in os.listdir(path_type):
                                path_team = os.path.join(path_type, team_folder)
                                if os.path.isdir(path_team):
                                    found_readme = False
                                    for file in os.listdir(path_team):
                                        if "readme.md" in file.lower():
                                            path_readme = os.path.join(path_team, file)
                                            relative_url = "/".join([year_folder, cyear_folder, type_folder, team_folder, file])
                                            candidates_all += extract_from_regular(path_readme,
                                                                                   assignment_type=type_folder,
                                                                                   relative_url=relative_url)
                                    else:
                                        warn(f"Could not find README.md in folder {path_team}, please check this contribution!")
    return candidates_all

def extract_from_regular(path_readme, assignment_type, relative_url):
    """
    Extracts the relevant information from the README.md of a contribution.
    Although they are formatted well in more recent years, they have an
    arbitrary formatting in earlier years. We apply some heuristic
    """
    # Figure out the format
    # -> Check if any heading contains the word "topic" or "title"
    # If there is none, assume the first header to be the title
    with open(path_readme, "r", encoding="utf8", errors="ignore") as f:
        is_first_line = True
        cur_section = "irrelevant-section"
        first_header = ""
        for line in f.readlines():
            if is_first_line and is_heading(line):
                first_header = line.strip(" \n#")
                cur_section = get_regular_readme_section(line.lower())
                is_first_line = False
            if cur_section == "title" and not is_empty(line):
                return [{
                    "title": line.strip(" \n#"),
                    "relative_url": relative_url,
                    "type": assignment_type
                }]
        # If no title / heading section was found, return simply the first header
        if is_not_trivial_header(first_header):
            return [{
                    "title": first_header.strip(" \n#"),
                    "relative_url": relative_url,
                    "type": assignment_type
                }]
        return []

def get_regular_readme_section(line):
    if "title" in line or "topic" in line:
        return "title"
    else:
        return "irrelevant-section"

def is_empty(line):
    return line.strip(" \n#") != ""

def is_not_trivial_header(header):
    header = header.lower()
    for w in list(non_informant_words):
        header = header.replace(w, "")
    for p in list(punctuation):
        header = header.replace(p, "")
    header = header.strip(" \n#")
    return header != ""