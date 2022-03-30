# similar-contributions
This action is embedded in the [KTH devops course](https://github.com/KTH/devops-course) and only makes sense to be used in that context. 

Upon a pull request of a student to submit an assignment proposal, this action browses the repository for all previous years' contributions and creates a comment linking those with similar titles. The comment is split in two sections, the first section contains similar contributions out of those that are highlighted as **outstanding** for that year. Students that feel overwhelmed at the beginning of the course or are struggling to find a good structure for their assignment are given high quality reading suggestions to help overcome these initial hurdles. The second section of the comment is created based on comparison with **all** previous contributions and helps the TA to assess whether the proposal is too similar to a previous contribution. However, due to the non-uniform structure of the different readme files in previous years, this output seems to be unreliable and thus must be activated explicitly in the workflow to be shown.

### Assumptions
The action assumes that there is one folder that contains all the contributions from previous years and the name of which can be specified with the input "search_dir" (see section **inputs** for details). In this folder, more subfolders are located that represent the previous years. Only those subfolder that are specified by the input "TODO-GIVE-NAME" are taken into account. Each of these subfolders then contain an additional folder and a markdown file which must contain the term "readme" (case insensitive). We refer to this markdown file as "selected-readme" (because it states the selected student works). The additional folder has one subfolder per assignment type which again have subfolders for every group with a respective markdown file that again must contain the term "readme". We refer to these group-level markdown files as "group-readme". The presentations subfolder represent a special case, as they contain folders for every week with a markdown file that states the week's presentation schedule. This file is refered to as "presentations-readme". In conclusion, the following folders and files must exist:

- \<search-directory>/\<year-directory>/\<selected-readme>
- \<search-directory>/\<year-directory>/\<contributions-directory>/\<assignment-type>/\<group-name>/\<group-readme>
- \<search-directory>/\<year-directory>/\<contributions-directory>/presentation/\<presentation-readme>

The selected-readme is used to extract possible contributions for the first section of the resulting comment, while the group-readme and presentation-readme are used to extract possible contributions for the second section of the comment.

### Similarity between titles
We compare the title of the proposal and each previous contribution to determine whether they are similar. To this end, we remove stopwords and other non-informant words from both titles and then determine for each word in the proposal title, whether it has a counterpart in the contribution title. We compare words using the [difflib](https://docs.python.org/3/library/difflib.html) library which generates a similarity measure in the range [0,1] for two strings. Two words from the respective titles match if their similarity is above a specified threshold which can be defined with the input "TODO-GIVE-NAME" (see below for details). The authors state that a value above 0.6 represents a close match. Because some titles are extremely short while others are very long, we decided to include a contribution in the output comment if at least one word from the proposal title has a counterpart in the contribution title.


### Limitations
We found that the group-readme files of the previous years have a very heterogenous format and can thus not be parsed in a fully valid manner. We apply heuristics as follows to extract the title of the contribution. We assume that if the markdown file contains a header "title", the following lines specify the title of the contribution. Although this also applies to many files where a header "topic" is present, many students used this header to then state a verbose description of the assignment, resulting in rather unreadable outputs. We thus only used the keyword "title" to indicate the contribution's title. If no such header can be found, it is assumed that the first header represents the title if it is not an empty string after removing non-informant keywords. As an example, the following header would not be extracted as a title: "Essay proposal:".

Overall this approach leads to a medium accuracy in extracting the right titles, but is likely to miss a lot of titles due to the often arbitrary formatting. For this reason, we recommend generating the action's output only based on the selected-readme, i.e. generate only the first section of the comment. 


## Inputs

### `example 1`

**Required** My description...

### `example2`

**Required** My other description....

## Output

A comment is generated for a pull request when it is opened or edited.

### Workflow for DevOps Course
```
name: ...
on:
  pull_request:
    ...

jobs:
  ...
```
