# install.test.spec.md
This is a specification for the testing install.py

# Overview
This repo is called infraDevContainerTest.
This repo is used to test infraDevContainer.
infraDevContainer is a git submodule and appears as a directory.
In infraDevContainer is a script called install.py.
install.py installs and uninstalls files to ./.devcontainer

# Instructions
- Review ./install.spec.md
- The create python based unit test to verify that install.py meets the install.spec.md.
- The test cases should not depend on any internal knowledge of install.py. The tests should only use the commandline options and look at the resulting changes in the files system.

# Framework instructions
- Use python venv to create a Virtual Environment for testing.
- Use python pytest framwork