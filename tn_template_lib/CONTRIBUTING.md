# Contribute to Trial Network Descriptor Templates

## Add a descriptor file

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

6. Submit a pull request with the changes to the `develop` branch and include **@CarlosAndreo** as a reviewer.

    6.1. The pull request must include:
    
    * The **descriptor file** for the trial network.
    * The **image** of the trial network.
    * The updated `TrialNetworks.drawio` file with the new image.
    * The updated `README.md` file.

7. Once the pull request has been reviewed, the changes will be merged into the `develop` branch.

## Update a descriptor file

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

6. Submit a pull request with the changes to the `develop` branch and include **@CarlosAndreo** as a reviewer.

    6.1. The pull request must include:
    
    * The **updated descriptor file** for the trial network.
    * The **updated image** of the trial network.
    * The updated `TrialNetworks.drawio` file with the new image.
    * The updated `README.md` file.