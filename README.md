# similar-contributions
This action is embedded in the [KTH devops course](https://github.com/KTH/devops-course) and only makes sense to be used in that context. 

Upon a pull request of a student to submit an assignment proposal, this action browses the repository for all previous years' contributions and creates a comment linking those with similar titles. The comment is split in two sections, the first section contains similar contributions out of those that are highlighted as **outstanding** for that year. Students that feel overwhelmed at the beginning of the course or are struggling to find a good structure for their assignment are given high quality reading suggestions to help overcome these initial hurdles. The second section of the comment is created based on comparison with **all** previous contributions and helps the TA to assess whether the proposal is too similar to a previous contribution. ... TODO ...
### Outstanding Student contributions
... TODO ...

### All student contributions
... TODO ...

##### Presentations
... TODO ...


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
