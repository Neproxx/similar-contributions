import os
import re
from warnings import warn
from similarity import non_informant_words, punctuation

### Code for extracting candidates from "selected student works" README files
def is_heading(line):
    """
    Checks whether a given line in a README.md file represents a heading
    """
    return len(line.strip()) >= 1 and line.strip(" \n")[0] == "#"


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

def get_type_label(line, allowed_types, default):
    """
    Given a line from a README.md file, determines whether this line indicates
    a sub-header like "essays" by testing whether one of the allowed assignment types
    is a substring. Returns the substring if that is the case and an empty string if
    the line represents a not allowed assignment type.
    """
    contribution_pattern = "^\s*?\*.\s*?\[(.*)\]\((.*)\)\s*?$"
    type_pattern = "^\s*?\*?\s*?([a-zA-Z ]+)\s*?$"
    is_contribution = bool(re.match(contribution_pattern, line.strip()))
    match = re.match(type_pattern, line.replace(":", "").strip())
    if not is_contribution and match:
        match_str = match.group(1)
        for t in allowed_types:
            if t.lower() in match_str.lower():
                return t
        return ""
    return default

def get_candidates_from(path_readme, allowed_types):
    """
    Extracts all the candidate contributions from a given README.md file
    that bundles all the selected contributions from a specific year
    """
    # Sort the allowed types so that more explicit, large names are
    # prioritized over short ones in get_type_label()
    allowed_types = sorted(allowed_types.copy(), key=len, reverse=True)
    candidates = []
    cur_section = ""
    cur_type = ""
    on_record = False
    rec_line = ""
    rec_depth = 0
    with open(path_readme, "r", encoding="utf8") as f:
        for line in f.readlines():
            if is_heading(line):
                cur_section = get_section_label(line.lower())
            if cur_section == "student-contributions":
                cur_type = get_type_label(line, allowed_types, default=cur_type)
                if cur_type in allowed_types:
                    candidates = update_candidates(line, cur_type, candidates)
                if is_partial_pattern(line.strip()) or on_record:
                    on_record = True
                    rec_line += " " + line.strip()
                    rec_depth += 1
                    if is_full_pattern(rec_line):
                        candidates = update_candidates(rec_line, cur_type, candidates)
                    if is_full_pattern(rec_line) or rec_depth >= 3:
                        on_record = False
                        rec_line = ""
                        rec_depth = 0
    return candidates

def is_partial_pattern(line):
    """
    Checks if line starts out like a contribution bullet point but ends early.
    This indicates that the contribution contains line breaks.
    """
    partial_pattern = "^\s*?\*.\s*?\[\s*?[a-zA-Z ]"
    full_pattern = "^\s*?\*.\s*?\[(.*)\]\((.*)\)\s*?$"
    if re.match(partial_pattern, line.strip()) and not re.match(full_pattern, line.strip()):
        return True


def is_full_pattern(line):
    full_pattern = "^\s*?\*.\s*?\[(.*)\]\((.*)\)\s*?$"
    if re.match(full_pattern, line.strip()):
        return True

    
def update_candidates(line, cur_type, candidates, url_label="url"):
    """
    Checks whether the line represents a contribution
    and adds it to the list of candidates.
    """
    pattern = "^\s*?\*.\s*?\[(.*)\]\((.*)\)\s*?$"
    m = re.match(pattern, line.strip())
    if m:
        candidates.append({
            "title": m.group(1),
            url_label: m.group(2),
            "type": cur_type
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

def get_outstanding_contributions(path_contributions, allowed_types, allowed_years):
    """
    Extracts candidate contributions from a year's readme file listing the outstanding ones.
    This method assumes that the given folder contains subfolders with
    README files from which the contributions should be extracted.
    """
    candidates_all = []
    for folder_year in os.listdir(path_contributions):
        path_year =  os.path.join(path_contributions, folder_year)
        if os.path.isdir(path_year) and folder_year in allowed_years:
            path_readme = find_readme(path_year)
            if path_readme:
                candidates_all += get_candidates_from(path_readme, allowed_types)
    return candidates_all

class Stats:
    def __init__(self):        
        self.from_topic_section = 0
        self.from_first_line = 0
        self.ill_formatted = 0
        self.removed_substrings = 0
        self.filtered_contributions = 0

### Code for extracting candidates from the set of all contributions of a year
def get_all_contributions(path_contributions, allowed_types, allowed_years, substr_filter_until2021, header_filter_until2021):
    """
    Extracts candidates from folders containing all contributions of the respective year.
    This method assumes that there is a subfolder for every year, which has another subfolder
    the name of which contains "contributions" which has a subfolder for every assignment type 
    which again have subfolders for every assignment which contain the README.md from which the
    information about the contribution can be extracted. In short, we assume a structure:
    path_contributions/<yyyy>/<contributions-yyyy>/<assignment-type>/<team-name>/README.md
    For presentations, we assume that there is a subfolder for every week that contains a
    readme with titles and urls for all presentations of that week.
    """
    stats = Stats()
    candidates_all = []

    for path, dirs, files in os.walk(path_contributions, topdown=False):
        ctype = [str for str in allowed_types if str in path]
        cyear = [str for str in allowed_years if str in path]
        if (
            ("README.md" in files) # All candidates must have a README.md
            & (ctype != []) # Filter only allowed proposal types
            & (cyear != []) # Filter only allowed years
        ) :
            ctitle = extract_title_from_readme(path, cyear, stats, substr_filter_until2021, header_filter_until2021)
            #print(f"\t {ctitle}")
            if os.name == "nt":
                rel_path = path_contributions + "\\" + path.lstrip(os.getcwd())
            else:
                rel_path = path_contributions + "/" + path.lstrip(os.getcwd())
            #print(rel_path)
            if (ctitle != ""): # Add candidate only if title could be added
                candidates_all += [{
                                "title": ctitle,
                                "relative_url": rel_path,
                                "type": ctype
                                }]
    #Print stats
    print(f"Contributions extracted based on title / topic header: {stats.from_topic_section}")
    print(f"Contributions extracted from first line, because of missing title indicator: {stats.from_first_line}")
    print(f"Contributions that could not be extracted: {stats.ill_formatted}")
    print(f"Contributions titles, where substrings were stripped: {stats.removed_substrings}")
    print(f"Contributions titles, that were filtered: {stats.filtered_contributions}")
    return candidates_all


def extract_title_from_readme(path, year, stats, substr_filter_until2021, header_filter_until2021):
    """
    Recording Mode part inspired by https://sopython.com/canon/92/extract-text-from-a-file-between-two-markers/
    """
    title = ""
    if os.name == "nt":
        path_readme = path + "\\README.md"
    else:
        path_readme = path + "/README.md"
    #print(f"Extracting from: {path_readme}")
    if(year[0] in ['2019', '2020', '2021']):
        # parse first header
        with open(path_readme, "r", encoding="utf8", errors="ignore") as fp:
            header = ""
            first_line = fp.readline()
            if(not any(str in first_line for str in header_filter_until2021)):
                header = first_line.strip(" \n#")
            else:
                stats.filtered_contributions += 1
        # maybe there is a topic section
        with open(path_readme, "r", encoding="utf8", errors="ignore") as fp:
            topic = ""
            inRecordingMode = False
            for line in fp:
                if not inRecordingMode:
                    if line.startswith('## Topic'):
                        inRecordingMode = True
                elif line.startswith('##'):
                    inRecordingMode = False
                else:
                    topic += line
        # header holds title most likely when it at least 3 words long
        if(len(header.split()) >= 3): 
            title = header
            stats.from_first_line += 1
        # otherwise title is topic when it consists of less then 20 words
        elif(len(topic.split()) <= 20):
            title = topic
            stats.from_topic_section += 1
        else:
            stats.ill_formatted += 1
        title_before = title
        #strip titles from unnecessary info
        for str in substr_filter_until2021:
            title = re.sub('(?i)'+re.escape(str), lambda m: "", title)
        if title_before != title:
            stats.removed_substrings += 1
    elif(year == ['2022']):
        pass
    else:
        with open(path_readme, "r", encoding="utf8", errors="ignore") as fp:
            inRecordingMode = False
            for line in fp:
                if not inRecordingMode:
                    if line.startswith('## Title'):
                        inRecordingMode = True
                elif line.startswith('##'):
                    inRecordingMode = False
                else:
                    title += line
        if title != "":
            stats.from_topic_section += 1
        else:
            stats.ill_formatted += 1
    #Remove markdown URLs from title name
    title = re.sub(r"\[(.+)\]\(.+\)", r"\1", title)
    #Remove markdown chars used for highlighting
    for ch in ['*', '_']:
        title = title.replace(ch, '')
    #Replace newline chars with spaces
    title = title.replace("\n", ' ')
    #Remove double spaces
    title = re.sub("\s\s+", " ", title)
    #Remove all leading and trailing spaces
    title = title.strip()
    #Capitalize first letter
    if title != "":
        title = title[0].upper() + title[1:]
    return title