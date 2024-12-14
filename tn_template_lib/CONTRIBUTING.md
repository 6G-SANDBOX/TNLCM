# Contribute to Trial Network Descriptor Templates

## :hammer_and_wrench: How to contribute

### Set up your environment

- **Fork the repository**: fork the project to your GitHub account to have your own copy. To do this, click the "Fork" button at the top right of the repository page on GitHub. This will create a copy of the repository in your GitHub account.

- **Clone your fork**: after forking, clone the repository to your local machine. To do this, copy the URL of your fork by clicking the green "Code" button.

    ```bash
    git clone <URL of your fork>
    ```

- **Add the original repository as a remote**: to keep your fork updated with changes from the original repository, add the original repository as a remote.

    ```bash
    git remote add upstream <URL of the original repository>
    ```

### Add trial network descriptor

To add a descriptor file for a trial network, follow these steps:

1. Create a branch from `develop`. 

    1.1. The branch name should follow the format `feature/tn_template_lib/<component_name>`.

    1.2. The `<component_name>` should be meaningful.

    ```bash
    git switch -c feature/tn_template_lib/<component_name> develop
    ```

2. Create the trial network descriptor file in the [`tn_template_lib`](../tn_template_lib/) directory.

    2.1. The descriptor file name should be `<component_name>.yaml`.

    2.2. The descriptor file extension must be **YAML**.

    2.3. To create the trial network descriptor, you can follow the guide provided in the [wiki](https://github.com/6G-SANDBOX/TNLCM/wiki/Trial-Network-Descriptor-Guide).

3. Add an image of the trial network in the [`images`](./images/) directory.

    3.1. The image name should be `<component_name>.png`.

    3.2. The image file extension must be **PNG**.

    3.3. To create the image, you can use the [draw.io](https://app.diagrams.net/) tool. Import the file [`TrialNetworks.drawio`](./drawio/TrialNetworks.drawio) into the draw.io website and create the graphical representation of the trial network.

4. Add the [`TrialNetworks.drawio`](./drawio/TrialNetworks.drawio) file with the new graphical representation of the trial network.

    4.1. Create new page in the draw.io with the name `<component_name>`.

    4.2. Save the file with the new image.

    4.3. Export the file and save it in [`drawio`](./drawio/) directory.

5. Add the trial network to the end of the [`README.md`](./README.md) file in the [`tn_template_lib`](../tn_template_lib/) directory. 

    5.1. To do this, add a section with the trial network name and its image.

    5.2. Add a list of the components that describe the descriptor of the trial network.

    5.3. Add a list with the platforms where the trial network can be deployed.

    ```markdown
    ## [<component_name>](./<component_name>.yaml)

    ![<component_name>](./images/<component_name>.png)

    ### Components

    * <component_name1>
    * <component_name2>

    ### Platforms

    * uma
    * athens
    * berlin
    * oulu
    ```

6. Commit the changes to your branch.

    ```bash
    git add .
    git commit -m "Add <component_name> trial network descriptor template"
    ```

7. Push the changes to your fork.

    ```bash
    git push origin feature/tn_template_lib/<component_name>
    ```

8. Create a pull request on GitHub, go to your TNLCM fork and click "Pull request" to start one. The pull request should be from your branch to the `develop` branch of the original repository.

    8.1. Include **@CarlosAndreo** as a reviewer.
    
    8.2. The pull request must include:
    
    * The **descriptor file** for the trial network.
    * The **image** of the trial network.
    * The updated `TrialNetworks.drawio` file with the new image.
    * The updated `README.md` file.

9. Once the pull request has been reviewed, the changes will be merged into the `develop` branch of the original repository.

### Update trial network descriptor

To update a descriptor file for a trial network, follow these steps:

1. Create a branch from `develop`. 

    1.1. The branch name should follow the format `hotfix/tn_template_lib/<component_name>`.

    1.2. The `<component_name>` should be the name of the component.

    ```bash
    git switch -c hotfix/tn_template_lib/<component_name> develop
    ```

2. Update the trial network descriptor file in the [`tn_template_lib`](../tn_template_lib/) directory.

    2.1. The descriptor file name should be `<component_name>.yaml`.

    2.2. The descriptor file extension must be **YAML**.

    2.3. To update the trial network descriptor, you can follow the guide provided in the [wiki](https://github.com/6G-SANDBOX/TNLCM/wiki/Trial-Network-Descriptor-Guide).

3. Update the image of the trial network in the [`images`](./images/) directory.

    3.1. The image name should be `<component_name>.png`.

    3.2. The image file extension must be **PNG**.

    3.3. To update the image, you can use the [draw.io](https://app.diagrams.net/) tool. Import the file [`TrialNetworks.drawio`](./drawio/TrialNetworks.drawio) into the draw.io website and update the graphical representation of the trial network.

4. Update the [`TrialNetworks.drawio`](./drawio/TrialNetworks.drawio) file with the new graphical representation of the trial network.

    4.1. Update the page with the name `<component_name>`.

    4.2. Save the file with the new image.

    4.3. Export the file and save it in [`drawio`](./drawio/) directory.

5. Update the trial network in the [`README.md`](./README.md) file in the [`tn_template_lib`](../tn_template_lib/) directory. 

6. Commit the changes to your branch.

    ```bash
    git add .
    git commit -m "Add <component_name> trial network descriptor template"
    ```

7. Push the changes to your fork.

    ```bash
    git push origin feature/tn_template_lib/<component_name>
    ```

8. Create a pull request on GitHub, go to your TNLCM fork and click "Pull request" to start one. The pull request should be from your branch to the `develop` branch of the original repository.

    8.1. Include **@CarlosAndreo** as a reviewer.
    
    8.2. The pull request must include:

    * The **updated descriptor file** for the trial network.
    * The **updated image** of the trial network.
    * The updated `TrialNetworks.drawio` file with the new image.
    * The updated `README.md` file.

9. Once the pull request has been reviewed, the changes will be merged into the `develop` branch of the original repository.

### :star2: Best practices

- **Review open issues** before opening a PR. If you think you can solve an issue and no other PR is open, use `#issue-number` in your commit to link it to the issue. It is also helpful to leave a comment so that it's clear which PR is being used for the issue.
- **Review open PRs** to ensure you're not working on something that is already in progress. You can always help on open PRs by contributing changes, comments, reviews, etc.
- **Keep your commits clean and descriptive**.
- **Follow the project's coding conventions**.
- **Update your branch regularly** to keep it up to date with the main branch of the project.