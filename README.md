# similar-contributions
This action is embedded in the [KTH devops course](https://github.com/KTH/devops-course) and only makes sense to be used in that context. 

Upon a pull request of a student to submit an assignment proposal, this action browses the repository for all previous years' contributions and creates a comment linking those with similar titles. The comment is split in two sections, the first section contains similar contributions out of those that are highlighted as **outstanding** for that year. Students that feel overwhelmed at the beginning of the course or are struggling to find a good structure for their assignment are given high quality reading suggestions to help overcome these initial hurdles. The second section of the comment is created based on comparison with **all** previous contributions and helps the TA to assess whether the proposal is too similar to a previous contribution. However, due to the non-uniform structure of the different readme files in previous years, this output seems to be unreliable and thus must be activated explicitly in the workflow to be shown.

### Assumptions
The action assumes that there is one folder that contains all the contributions from previous years and the name of which can be specified with the input "search_dir" (see section **inputs** for details). In this folder, more subfolders are located that represent the previous years. Only those subfolder that are specified by the input "TODO-GIVE-NAME" are taken into account. Each of these subfolders then contain an additional folder and a markdown file which must contain the term "readme" (case insensitive). We refer to this markdown file as "selected-readme" (because it states the selected student works). The additional folder has one subfolder per assignment type which again have subfolders for every group with a respective markdown file that again must contain the term "readme". We refer to these group-level markdown files as "group-readme". The presentations subfolder represent a special case, as they contain folders for every week with a markdown file that states the week's presentation schedule. This file is refered to as "presentations-readme". In conclusion, the following folders and files must exist:

- \<search-directory>/\<year-directory>/\<selected-readme>
- \<search-directory>/\<year-directory>/\<contributions-directory>/\<assignment-type>/\<group-name>/\<group-readme>
- \<search-directory>/\<year-directory>/\<contributions-directory>/\presentation/\<presentation-readme>

The selected-readme is used to extract possible contributions for the first section of the resulting comment, while the group-readme and presentation-readme are used to extract possible contributions for the second section of the comment.

##### Presentations
... TODO ...

### Assumptions
- Specific folder structures

TODO: 
- explain how different contributions are found
- explain what "similarity" means
- explain limitations


## Inputs

### `github_token`

**Required** The GITHUB_TOKEN secret.

### `text`

**Required** The text which is parsed for a repository.

### Minimum Requirements
The minimum amount of a specific stat that is required for the action to pass.

The following requirement inputs can be passed into the action, the default is 0:
`min_stars`,
`min_watchers`,
`min_contributors`,
`min_forks`,
`min_commits`,
`min_commits_last_year`,
`min_open_issues`

## Outputs

### Workflow for DevOps Course
```
name: ...
on:
  pull_request:
    ...

jobs:
  ...
```
