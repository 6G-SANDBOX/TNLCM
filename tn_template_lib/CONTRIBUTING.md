# Contribute to TN Template Library

To add a descriptor file for a trial network, follow these steps:

1. Create a branch from `develop`. 

    1.1. The branch name should follow the format `feature/tn_template_lib/<componentName>`.

    1.2. The `<componentName>` should be meaningful.

    ```bash
    git switch -c feature/tn_template_lib/<componentName> develop
    ```

2. Create the trial network descriptor file in the [`tn_template_lib`](../tn_template_lib/) directory.

    2.1. The descriptor file name should be `<componentName>.yaml`.

    2.2. The descriptor file extension must be **YAML**.

    2.3. To create the trial network descriptor, you can follow the guide provided in the [wiki](https://github.com/6G-SANDBOX/TNLCM/wiki/Trial-Network-Descriptor-Guide).

3. Add an image of the trial network in the `images` directory.

    3.1. The image name should be `<componentName>.png`.

    3.2. The image file extension must be **.png**.

    3.3. To create the image, you can use the [draw.io](https://app.diagrams.net/) tool. Import the file [`TrialNetworks.drawio`](./drawio/TrialNetworks.drawio) into the draw.io website and create the graphical representation of the trial network.

4. Add the [`TrialNetworks.drawio`](./drawio/TrialNetworks.drawio) file with the new graphical representation of the trial network.

    4.1. Save the file with the new image.

    4.2. Export the file and save it in [`drawio`](./drawio/) directory.

5. Add the trial network to the [`README.md`](./README.md) file in the [`tn_template_lib`](../tn_template_lib/) folder at the end. 

    4.1. To do this, add a section with the trial network name and its image.

    4.2. Add a list of the trial network components.

    4.3. Add a list with the platforms where the trial network can be deployed.

    4.4. Format:

    ```markdown
    ## [<componentName>](./<componentName>.yaml)

    ![<componentName>](./images/<componentName>.png)

    ### Components

    * <component1>
    * <component2>

    ### Platforms

    * uma
    * athens
    * berlin
    * oulu
    ```

6. Submit a pull request with the changes to the `develop` branch and include **@CarlosAndreo** as a reviewer.

    5.1. The pull request must include:
    
    * The **descriptor file** for the trial network.
    * The **image** of the trial network.
    * The updated `TrialNetworks.drawio` file with the new image.
    * The updated `README.md` file.

7. Once the pull request has been reviewed, the changes will be merged into the `develop` branch.