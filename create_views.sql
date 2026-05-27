DROP TABLE IF EXISTS demography_broad_age;

CREATE TABLE demography_broad_age AS

WITH births_broad AS (
    SELECT
        'births' AS dataset,
        year,
        territory_raw AS territory,
        CASE
            WHEN TRIM(measure) IN ('Възраст на майката | под 20', '20 - 24') THEN 'under 25'
            WHEN TRIM(measure) IN ('25 - 29', '30 - 34') THEN '25 - 34'
            WHEN TRIM(measure) IN ('35 - 39', '40 - 44', '45', '45 +', '45+') THEN '35+'
            ELSE NULL
        END AS broad_age_group,
        SUM(CAST(value AS REAL)) AS value
    FROM births_by_mother_age_clean
    WHERE TRIM(territory_raw) = 'Общо за страната'
      AND TRIM(measure) IN (
            'Възраст на майката | под 20',
            '20 - 24',
            '25 - 29',
            '30 - 34',
            '35 - 39',
            '40 - 44',
            '45',
            '45 +',
            '45+'
      )
    GROUP BY
        year,
        territory_raw,
        broad_age_group
),

marriages_broad AS (
    SELECT
        'marriages' AS dataset,
        year,
        group_name AS territory,
        CASE
            WHEN TRIM(age_group) IN ('18', '18 - 19', '18-19', '20 - 24', '20-24') THEN 'under 25'
            WHEN TRIM(age_group) IN ('25 - 29', '25-29', '30 - 34', '30-34') THEN '25 - 34'
            WHEN TRIM(age_group) IN ('35 - 39', '35-39', '40 - 49', '40-49', '50 - 59', '50-59', '60', '60+') THEN '35+'
            ELSE NULL
        END AS broad_age_group,
        SUM(CAST(value AS REAL)) AS value
    FROM marriages_by_age_sex_clean
    WHERE LOWER(TRIM(group_name)) = 'Общо за страната'
      AND TRIM(age_group) IN (
            '18', '18 - 19', '18-19', '20 - 24', '20-24',
            '25 - 29', '25-29', '30 - 34', '30-34',
            '35 - 39', '35-39', '40 - 49', '40-49',
            '50 - 59', '50-59', '60', '60+'
      )
    GROUP BY
        year,
        group_name,
        broad_age_group
),

divorces_broad AS (
    SELECT
        'divorces' AS dataset,
        year,
        group_name AS territory,
        CASE
            WHEN TRIM(age_group) IN ('18', '18 - 19', '18-19', '20 - 24', '20-24') THEN 'under 25'
            WHEN TRIM(age_group) IN ('25 - 29', '25-29', '30 - 34', '30-34') THEN '25 - 34'
            WHEN TRIM(age_group) IN ('35 - 39', '35-39', '40 - 49', '40-49', '50 - 59', '50-59', '60', '60+') THEN '35+'
            ELSE NULL
        END AS broad_age_group,
        SUM(CAST(value AS REAL)) AS value
    FROM divorces_by_age_sex_clean
    WHERE LOWER(TRIM(group_name)) = 'Общо за страната'
      AND TRIM(age_group) IN (
            '18', '18 - 19', '18-19', '20 - 24', '20-24',
            '25 - 29', '25-29', '30 - 34', '30-34',
            '35 - 39', '35-39', '40 - 49', '40-49',
            '50 - 59', '50-59', '60', '60+'
      )
    GROUP BY
        year,
        group_name,
        broad_age_group
)

SELECT * FROM births_broad
UNION ALL
SELECT * FROM marriages_broad
UNION ALL
SELECT * FROM divorces_broad;