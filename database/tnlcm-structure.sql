DROP TABLE IF EXISTS `trial_network`;
CREATE TABLE `trial_network` (
    `tn_id`                 VARCHAR(255) NOT NULL,
    `status`                VARCHAR(255) NOT NULL,
    `raw_descriptor`        VARCHAR(3000) NOT NULL,
    `sorted_descriptor`     VARCHAR(3000) NOT NULL,
    PRIMARY KEY (`tn_id`)
);

DROP TABLE IF EXISTS `6glibrary`;
CREATE TABLE `6glibrary` (
    `component`            VARCHAR(255) NOT NULL,
    `branch`               VARCHAR(255) NOT NULL,
    `commit`               VARCHAR(255) NOT NULL,
    PRIMARY KEY (`component`)
);