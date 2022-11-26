CREATE VIEW s3_user_access
AS SELECT distinct acc.user_id,
                   acc.s3_access_name,
                   acc.s3_access_key,
                   acc.s3_secret_key,
                   endp.s3_default_region,
                   prov.name provider_name,
                   prov.endpoint_url_template,
                   endp.name endpoint_name,
                   endp.trust_ca_bundle,
                   CASE
                       WHEN endp.url IS NOT "" THEN endp.url
                       WHEN prov.endpoint_url_template IS NOT NULL THEN REPLACE(prov.endpoint_url_template, "<region>", endp.s3_default_region)
                       ELSE
                           NULL
                       END	as url
   FROM ( SELECT ug.user_id,
                 s3a.name AS s3_access_name,
                 s3a.s3_access_key,
                 s3a.s3_secret_key,
                 s3a.s3_endpoint_id
          FROM s3_assoc_user_group ug
                   JOIN s3_group gr ON gr.id = ug.s3_group_id
                   JOIN s3_assoc_group_s3access gs3a ON gr.id = gs3a.s3_group_id
                   JOIN s3_access s3a ON gs3a.s3_access_id = s3a.id
          UNION
          SELECT us3a.user_id,
                 s3a.name AS s3_access_name,
                 s3a.s3_access_key,
                 s3a.s3_secret_key,
                 s3a.s3_endpoint_id
          FROM s3_assoc_user_s3access us3a
                   JOIN s3_access s3a ON us3a.s3_access_id = s3a.id
        ) acc
            JOIN s3_endpoint endp ON endp.id = acc.s3_endpoint_id
            LEFT OUTER JOIN s3_provider prov ON endp.s3_provider_id = prov.id;