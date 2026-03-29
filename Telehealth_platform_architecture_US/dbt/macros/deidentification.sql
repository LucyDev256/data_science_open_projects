-- dbt macro for de-identifying patient UUIDs
-- Uses SHA256 hashing with a salt for one-way de-identification
-- This allows analytics without exposing actual patient identifiers

{% macro deidentify_patient_uuid(patient_uuid_column) %}
    TO_HEX(
        SHA256(
            CONCAT(
                {{ patient_uuid_column }},
                '{{ var("deidentification_salt") }}'
            )
        )
    )
{% endmacro %}


-- Macro for generating surrogate keys
{% macro generate_surrogate_key(columns) %}
    TO_HEX(
        MD5(
            CONCAT(
                {% for column in columns %}
                    COALESCE(CAST({{ column }} AS STRING), '')
                    {% if not loop.last %}, '|', {% endif %}
                {% endfor %}
            )
        )
    )
{% endmacro %}


-- Macro for safe JSON extraction with null handling
{% macro safe_json_extract(json_column, json_path, default_value='NULL') %}
    COALESCE(
        JSON_EXTRACT_SCALAR({{ json_column }}, '{{ json_path }}'),
        {{ default_value }}
    )
{% endmacro %}


-- Macro for calculating days between dates with null handling
{% macro days_between(start_date, end_date) %}
    DATE_DIFF(
        COALESCE({{ end_date }}, CURRENT_DATE()),
        {{ start_date }},
        DAY
    )
{% endmacro %}


-- Macro for HIPAA-compliant age bucketing
-- Returns age ranges instead of exact ages
{% macro age_bucket(date_of_birth) %}
    CASE
        WHEN DATE_DIFF(CURRENT_DATE(), {{ date_of_birth }}, YEAR) < 18 THEN 'under_18'
        WHEN DATE_DIFF(CURRENT_DATE(), {{ date_of_birth }}, YEAR) BETWEEN 18 AND 24 THEN '18-24'
        WHEN DATE_DIFF(CURRENT_DATE(), {{ date_of_birth }}, YEAR) BETWEEN 25 AND 34 THEN '25-34'
        WHEN DATE_DIFF(CURRENT_DATE(), {{ date_of_birth }}, YEAR) BETWEEN 35 AND 44 THEN '35-44'
        WHEN DATE_DIFF(CURRENT_DATE(), {{ date_of_birth }}, YEAR) BETWEEN 45 AND 54 THEN '45-54'
        WHEN DATE_DIFF(CURRENT_DATE(), {{ date_of_birth }}, YEAR) BETWEEN 55 AND 64 THEN '55-64'
        WHEN DATE_DIFF(CURRENT_DATE(), {{ date_of_birth }}, YEAR) >= 65 THEN '65+'
        ELSE 'unknown'
    END
{% endmacro %}


-- Macro for k-anonymity validation
-- Ensures de-identified datasets have sufficient group sizes
{% macro validate_k_anonymity(table_name, quasi_identifier_columns, k_value=5) %}
    WITH group_sizes AS (
        SELECT
            {% for column in quasi_identifier_columns %}
                {{ column }}{% if not loop.last %},{% endif %}
            {% endfor %},
            COUNT(*) AS group_size
        FROM {{ table_name }}
        GROUP BY
            {% for column in quasi_identifier_columns %}
                {{ column }}{% if not loop.last %},{% endif %}
            {% endfor %}
    )
    
    SELECT
        COUNT(*) AS groups_below_k,
        MIN(group_size) AS min_group_size,
        AVG(group_size) AS avg_group_size
    FROM group_sizes
    WHERE group_size < {{ k_value }}
{% endmacro %}
