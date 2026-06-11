DROP TABLE IF EXISTS demography_broad_age;

CREATE TABLE demography_broad_age AS

WITH births_broad AS (
    SELECT
        'births' AS dataset_type,
        CAST(year AS INTEGER) AS year,
        TRIM(territory_raw) AS territory,
        CASE
            WHEN TRIM(measure) IN (
                'Възраст на майката | под 20',
                '20 - 24'
            ) THEN 'under_25'

            WHEN TRIM(measure) IN (
                '25 - 29',
                '30 - 34'
            ) THEN '25_34'

            WHEN TRIM(measure) IN (
                '35 - 39',
                '40 - 44',
                '45',
                '45 +',
                '45+'
            ) THEN '35_plus'

            ELSE NULL
        END AS age_group,

        SUM(CAST(value AS REAL)) AS total_count

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
        CAST(year AS INTEGER),
        TRIM(territory_raw),
        age_group
),

marriages_broad AS (
    SELECT
        'marriages' AS dataset_type,
        CAST(year AS INTEGER) AS year,
        TRIM(group_name) AS territory,

        CASE
            WHEN TRIM(age_group) IN (
                '18',
                '18 - 19',
                '18-19',
                '20 - 24',
                '20-24'
            ) THEN 'under_25'

            WHEN TRIM(age_group) IN (
                '25 - 29',
                '25-29',
                '30 - 34',
                '30-34'
            ) THEN '25_34'

            WHEN TRIM(age_group) IN (
                '35 - 39',
                '35-39',
                '40 - 49',
                '40-49',
                '50 - 59',
                '50-59',
                '60',
                '60+'
            ) THEN '35_plus'

            ELSE NULL
        END AS age_group,

        SUM(CAST(value AS REAL)) AS total_count

    FROM marriages_by_age_sex_clean

    WHERE LOWER(TRIM(group_name)) = LOWER('Общо за страната')
      AND TRIM(age_group) IN (
            '18',
            '18 - 19',
            '18-19',
            '20 - 24',
            '20-24',  
            '25 - 29',
            '25-29',
            '30 - 34',
            '30-34',
            '35 - 39',
            '35-39',
            '40 - 49',
            '40-49',
            '50 - 59',
            '50-59',
            '60',
            '60+'
      )

    GROUP BY
        CAST(year AS INTEGER),
        TRIM(group_name),
        age_group
)

SELECT * FROM births_broad
UNION ALL
SELECT * FROM marriages_broad

ORDER BY
    dataset_type,
    age_group,
    year;