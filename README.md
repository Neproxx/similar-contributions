# similar-contributions
This action is embedded in the [KTH devops course](https://github.com/KTH/devops-course) and only makes sense to be used in that context. 

Upon a pull request of a student to submit an assignment proposal, this action browses the repository for all previous and current years' contributions and creates a comment linking those with similar titles. The comment is split in two sections, the first section contains similar contributions out of those that are highlighted as **outstanding** for that year. Students that feel overwhelmed at the beginning of the course or are struggling to find a good structure for their assignment are given high quality reading suggestions to help overcome these initial hurdles. The second section of the comment is created based on comparison with **all** previous contributions and helps the TA to assess whether the proposal is too similar to a previous contribution. However, due to the non-uniform structure of the different readme files in previous years, this output seems to be unreliable and thus must be activated explicitly in the workflow to be shown.

### Minimal example
```
name: Write comment about similar contributions

on: 
  pull_request:
    types: [opened, edited]

jobs:
  similar-contributions:
    steps: 
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v3
        with:
          python-version: '3.7.12'
          
      # Get title from PR comment
      - name: Get proposal title from PR body
        run: |
            echo 'PROPOSAL_TITLE<<EOF' >> $GITHUB_ENV
            echo "${{ github.event.pull_request.body }}" | sed -n '/^## Title/,${p;/^## Names/q}' | sed '1d;$d' | sed '/^$/d' >> $GITHUB_ENV
            echo 'EOF' >> $GITHUB_ENV
      - name: echo proposal title
        run: |
            echo "${{ env.PROPOSAL_TITLE }}"
            
      # Create comment body and stores it in env.GENERATED_COMMENT
      - name: Run action
        uses: ./<PLACEHOLDER>
        
      # Check if there is already a recommendation comment under current pull request
      - name: Find Comment
        uses: peter-evans/find-comment@v2
        id: fc # this tag will be used for the conditional selection of either creating or updating
        with:
          issue-number: ${{ github.event.pull_request.number }}
          comment-author: 'github-actions[bot]'
          body-includes: Reading Recommendations
       
      # Create comment if there isn't
      - name: Create comment
        if: steps.fc.outputs.comment-id == ''
        uses: peter-evans/create-or-update-comment@v2
        with:
          issue-number: ${{ github.event.pull_request.number }}
          body: ${{ env.GENERATED_COMMENT }}

      # Update comment if there is
      - name: Update comment
        if: steps.fc.outputs.comment-id != ''
        uses: peter-evans/create-or-update-comment@v2
        with:
          comment-id: ${{ steps.fc.outputs.comment-id }}
          edit-mode: replace
          body: ${{ env.GENERATED_COMMENT }}
          reactions: hooray
```

## Inputs

| Input variable           | Required | Default | Description |
| ------------------------ | -------- | ------------- | ----------- |
| cont_dir                 | Yes      | "cont"        | Directory containing the contributions |
| attic_dir                | Yes      | "attic"       | Directory containing the contributions |
| filter_type              | Yes      | "['essay', 'course-automation', 'demo', 'presentation', 'executable-tutorial', 'tutorial', 'open-source', 'open']"        |             |
| filter_year              | Yes      | "['2019', '2020', '2021']" | Filter for contribution types that are should be regarded |
| min_word_similarity      | Yes      | "0.8"        | Filter for contribution years that should be regarded |
| words_ignore             | Yes      | "['testing', 'automated', 'pipeline', 'deployment', 'using', 'system', 'inner', 'introduction', 'analysis', 'build', 'tools', 'tool', 'practice', 'end-to-end', 'useful', 'comparison', 'problem', 'devOps']" | Treshold for similiarity check of keywords |
| header_filter_before2021 | Yes      | "['Agenda for Student', 'Remarkable presentations from', 'Members:', 'Member:', 'This project is a part of', 'Adam Hasselberg and Aigars Tumanis', 'Author:', 'Selected 2021', 'Please see the grading criteria for live demo', '<img src =', 'Paul Löwenström: paulher@kth.se', 'This folder contains students', 'anders sjöbom asjobom@kth.se']" | Add words to ignore when comparing the proposal titles |
| substr_filter_before2021 | Yes      | "['Topic:', '##  ', '****topic**** : #', 'presentation proposal:', 'presentation submission:', 'presentation -', 'presentation:', 'Open-source contribution proposal:', 'opensource contribution:', 'open source contribution:', 'open-source:', 'opentask: ', 'executable-tutorial:', 'Executable Tutorial:', 'executible Tutorial:', 'exectuable tutorial:', 'Executable Tutorial Submission:', 'tutorial proposal -', 'Tutorial Submission:', 'Tutorial submission:', 'Tutorial Proposal:', 'Complete Tutorial:', 'Tutorial:', 'essay proposal :', 'essay proposal -', 'Essay proposal:', 'Essay:', 'Video demo submission:', 'Demo Submission After feedback:', 'Demo proposal:', 'Video demo:', 'Demo submission:', 'DEMO 🎥 :', 'demo -', 'Demo:', 'demo of ',  'course automation proposal:', 'Course automation:' 'Course-automation:', 'Proposal ']"   | The formatting of the contributions until 2021 was not streamlined. This list contains filters that are not considered as titles |
| sort_option              | Yes      | 'sort_by_keywords' | Specify sorting type for contributions (no_sorting, sort_by_keywords) |

### Assumptions
The action assumes that there is one folder that contains all the contributions from previous years and the name of which can be specified with the input "attic_dir" (see section **inputs** for details). In this folder, more subfolders are located that represent the previous years. The searching algorithm will consider all files named "README.md" (case sensitive) in these folders.
  
Each of these year-folders can contain another "README.md" (case insensitive). We refer to this markdown file as "selected-readme" (because it states the selected student works). The selected-readme is used to extract possible contributions for the first section of the resulting comment, while the other files are used to extract possible contributions for the second section of the comment.

### Similarity between titles
We compare the title of the proposal and each previous contribution to determine whether they are similar. To this end, we remove stopwords and other non-informant words from both titles and then determine for each word in the proposal title, whether it has a counterpart in the contribution title. We compare words using the [difflib](https://docs.python.org/3/library/difflib.html) library which generates a similarity measure in the range [0,1] for two strings. Two words from the respective titles match if their similarity is above a specified threshold which can be defined with the input "min_word_similarity" (see section **inputs** for details). The authors state that a value above 0.6 represents a close match. Because some titles are extremely short while others are very long, we decided to include a contribution in the output comment if at least one word from the proposal title has a counterpart in the contribution title.

### Limitations
Until 2021 there was no unified way, how proposal "README.md" files had to be formatted. Thus, it is not possible to consider every contribution. However, we managed to get the number of the non-parsable contributions, down to a number of just 23 of ~400 total contributions.
