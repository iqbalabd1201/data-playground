-- GET DATA FROM DB POSTGRRE

select * from
(select
	s.shipment_id,
	J.booking_id as tokped_shipment_id,
	s.shipment_type,
	s.customer_id,
	s.customer_role,
	s.quantity,
	s.is_deleted,
	s.is_finished,
	s.channel,
	s.status_id,
	t.*
from
	public.shipment s
left join pickup p 
on s.shipment_id = p.shipment_id 
left join task t 
on p.task_id = t.task_id
left join shipment_tokopedia J
on s.shipment_id = J.shipment_id 
)A
where finished_at::DATE between (CURRENT_DATE - INTERVAL '3 DAY') AND CURRENT_DATE


------------ LINUX SCRIPT 
#!/bin/bash

export AWS_ACCESS_KEY_ID=AKIAURRDRKYV2DCM4ZMW
export AWS_SECRET_ACCESS_KEY=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
export AWS_DEFAULT_REGION=ap-southeast-1

sudo chown -R ubuntu /home/data/genesis/ship/temp.csv

aws s3 cp /home/data/genesis/ship/temp.csv s3://lp-s3-algo/ship/output/processing/



--------------------------------------------------------- STAGING CREATING TEMP TABLE
TRUNCATE TABLE algo_temp.shipment_temp;

         COPY algo_temp.shipment_temp FROM 's3://lp-s3-algo/ship/output/processing/temp.csv'
         iam_role 'arn:aws:iam::312533407275:role/lp-role-redshift-customized-dev'
         CSV
         DELIMITER ';'
         ACCEPTINVCHARS
         emptyasnull
         blanksasnull
         IGNOREHEADER 1;

---------- SEND INTO DATA MART

call algo_apps.sp_shipment ('InsData');

CREATE OR REPLACE PROCEDURE algo_apps.sp_shipment(jobname character varying(100))
 LANGUAGE plpgsql
AS $$
BEGIN
    DROP TABLE IF EXISTS algo_shipment;
    CREATE
        TEMP TABLE algo_shipment
        DISTSTYLE KEY
        DISTKEY (shipment_id)
        SORTKEY (shipment_type)
    AS (
        SELECT  
						A.shipment_id,
      					tokped_shipment_id,
                        shipment_type,
      B.package_id, B.shipment_package_id,
                        customer_id::int,
                        customer_role,
                        quantity::int,
                        is_deleted ,
                        is_finished ,
                        channel ,
                        status_id ,
                        task_id::int,
                        task_type ,
                        courier_id::int,
                        TO_TIMESTAMP(created_at,
                            'yyyy-mm-dd HH24:MI:SS')                                      AS created_at,
                         TO_TIMESTAMP(finished_at,
                            'yyyy-mm-dd HH24:MI:SS')                                      AS finished_at,
                        finished_by::int,     
               current_timestamp::date                                                         AS da_batchdate
        FROM algo_temp.shipment_temp A
      	left join algo_apps.shipment_package B
      	on A.shipment_id = B.shipment_id
    );

    DELETE
    FROM algo_apps.shipment
    WHERE shipment_id IN (SELECT shipment_id from algo_shipment);
    INSERT INTO algo_apps.shipment (SELECT * FROM algo_shipment);
END;
$$

-------------------- DATA MART MONITORING

WITH history_algo AS (
    SELECT  created_at::date AS stt_date,
            count(*)            AS TOTAL_HISTORY_ALGO
    FROM algo_apps.history_algo
    WHERE stt_date between '2021-10-01' and current_timestamp::date
    GROUP BY 1
    ORDER BY 1 DESC
    ),
shipment AS(
    SELECT  created_at::date AS stt_date,
            count(*)            AS TOTAL_SHIPMENT
    FROM algo_apps.shipment
    WHERE stt_date between '2021-10-01' and current_timestamp::date
    GROUP BY 1
    ORDER BY 1 DESC
    ),
PACKAGE AS(
    SELECT  created_at::date AS stt_date,
            count(*)            AS TOTAL_PACKAGE
    FROM algo_apps.package
    WHERE stt_date between '2021-10-01' and current_timestamp::date
    GROUP BY 1
    ORDER BY 1 DESC
    ),
history_recap AS (
    SELECT  created_at::date AS stt_date,
            count(*)            AS TOTAL_HISTORY_RECAP
    FROM algo_apps.history_recap
    WHERE stt_date between '2021-10-01' and current_timestamp::date
    GROUP BY 1
    ORDER BY 1 DESC
    ),
shipment_recap AS(
    SELECT  created_at::date AS stt_date,
            count(*)            AS TOTAL_SHIPMENT_RECAP
    FROM algo_apps.shipment_recap
    WHERE stt_date between '2021-10-01' and current_timestamp::date
    GROUP BY 1
    ORDER BY 1 DESC
    ),
PACKAGE_recap AS(
    SELECT  created_at::date AS stt_date,
            count(*)            AS TOTAL_PACKAGE_RECAP
    FROM algo_apps.package_recap
    WHERE stt_date between '2021-10-01' and current_timestamp::date
    GROUP BY 1
    ORDER BY 1 DESC
    )
SELECT  A.*,
        B.TOTAL_SHIPMENT,
        C.TOTAL_PACKAGE,
        D.TOTAL_HISTORY_RECAP,
        E.TOTAL_SHIPMENT_RECAP,
        F.TOTAL_PACKAGE_RECAP,
        A.TOTAL_HISTORY_ALGO-D.TOTAL_HISTORY_RECAP AS DIFF_HISTORY,
        B.TOTAL_SHIPMENT-E.TOTAL_SHIPMENT_RECAP AS DIFF_SHIPMENT,
        C.TOTAL_PACKAGE-F.TOTAL_PACKAGE_RECAP AS DIFF_PACKAGE
from history_algo A
LEFT JOIN shipment B ON A.stt_date = B.stt_date
LEFT JOIN PACKAGE C ON A.stt_date = C.stt_date
LEFT JOIN history_recap D ON A.stt_date = D.stt_date
LEFT JOIN shipment_recap E ON A.stt_date = E.stt_date
LEFT JOIN package_recap F ON A.stt_date = F.stt_date
ORDER BY 1 DESC

-------------------------------------------------------------------------------------- Table SLA calculation

CREATE OR REPLACE PROCEDURE lp_dw.sla_test(jobname character varying(100))
 LANGUAGE plpgsql
AS $$
BEGIN
--XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
DROP TABLE IF EXISTS lp_data_temp.data_elexys;
CREATE TABLE lp_data_temp.data_elexys as  ( 
SELECT A.stt_id,
       A.stt_no_v,
       A.stt_no,
       A.SOURCE,
       A.stt_booked_at,
       A.stt_updated_at,
       A.starting_status,
       A.stt_pod_date,
       A.last_status,
       A.client_code,
       A.client_name,
       A.origin,
       A.destination,
       A.fwd_area_dest,
       A.fwd_area_origin,
       CASE
           --WHEN C.client_code_elexys IS NOT NULL THEN 'ONEPACK'
           WHEN B.nama_customer IS NOT NULL THEN 'ONEPACK'
           ELSE A.product
           END AS product,
       A.sender_name,
       A.sender_phone,
       A.consignee_name,
       A.consignee_phone,
       A.shipment_id,
       A.external_id,
       A.commodity,
       A.pcs,
       A.stt_total_amount,
       A.chargeable_weight,
       A.stt_publish_rate,
       A.stt_booked_by,
       A.stt_booked_for,
       A.created_name,
       A.source_flag,
       A.isgodw,
       A.iselexys,
       A.isgenesis,
       A.da_batchdate,
       A.process_created,
       A.process_finished,
       A.user_process,
       A.validation,
       A.validation_status
FROM (SELECT *
      FROM lp_dw.stt
--  WHERE stt_booked_at::DATE BETWEEN '2021-05-01' AND CURRENT_DATE
      WHERE stt_booked_at::DATE BETWEEN ((CURRENT_TIMESTAMP + INTERVAL '7 Hours')::date - INTERVAL '30 DAY') AND (CURRENT_TIMESTAMP + INTERVAL '7 Hours')::date
     ) A
         LEFT JOIN
     (SELECT code_customer,
             nama_customer
      FROM lp_data_temp.sla_corporate
      WHERE sla_edit = 'Onepack') B
     ON A.client_code = B.code_customer AND A.source = 'CORPORATE'
         LEFT JOIN
     genesis.client C
     ON A.client_code = C.client_code AND A.source = 'CORPORATE');
--XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
DROP TABLE IF EXISTS lp_data_temp.data_a;
CREATE TABLE lp_data_temp.data_a AS (
SELECT *,
       CASE WHEN sla_origin IS NULL THEN 0 ELSE sla_origin::int END +
       CASE WHEN sla_destination IS NULL THEN 0 ELSE sla_destination::int END +
       CASE WHEN estimate_sla IS NULL THEN 0 ELSE estimate_sla::int END AS sla_max,
       TO_CHAR(stt_booked_at::date, 'YYYY-MM')                          AS booked_month_year,
       TO_CHAR(pod_date::date, 'YYYY-MM')                               AS pod_month_year
FROM (SELECT DISTINCT s.stt_no                                                              AS stt_no,
                      stt_id,
                      s.source                                                              AS source,
                      s.client_code,
                      s.client_name,
                      CASE
                          WHEN s.product IS NULL THEN 'undefined'
                          WHEN s.product = 'Jagopack' THEN 'JAGOPACK'
                          ELSE s.product END                                                AS product,
                      s.stt_total_amount,
                      s.chargeable_weight,
                      s.last_status,
                      s.stt_booked_at,
                      s.stt_pod_date                                                        AS pod_date,
                      CURRENT_TIMESTAMP::date                                               AS now,
                      s.fwd_area_origin,
                      s.fwd_area_dest,
                      s.origin,
                      s.destination,
                      s.origin || '-' || s.destination                                      AS result_string,
                      CASE WHEN d.sla_origin IS NULL THEN 0 ELSE d.sla_origin END           AS sla_origin,
                      CASE WHEN x.sla_destination IS NULL THEN 0 ELSE x.sla_destination END AS sla_destination,
                      CASE
                          WHEN SUBSTRING(e.estimate_sla, 3, 1) = '' THEN NULL
                          ELSE SUBSTRING(e.estimate_sla, 3, 1)
                          END                                                               AS estimate_sla,
                      rr.Old_Route as route_normal_old,
                      rr.Old_Route_Moda as transport_normal_old,
                      rr.New_Route as route_implementasi_new,
                      rr.New_Route_Moda as transport_implementasi_new,
                      r.sla_july_old,
                      r.sla_october_new,
                      r.keterangan
      FROM (SELECT *
            FROM lp_data_temp.data_elexys
            WHERE created_name NOT ILIKE '%testing%') S
               LEFT JOIN genesis.district d
                         ON s.fwd_area_origin = d.name
               LEFT JOIN genesis.district x
                         ON s.fwd_area_dest = x.name
               LEFT JOIN genesis.estimate_sla e
                         ON s.origin = e.estimate_sla_origin AND
                            s.destination = e.estimate_sla_destination AND
  							e.estimate_sla_type = 'pos' AND
                            (CASE WHEN s.product = 'LANDPACK' THEN 'JAGOPACK' ELSE s.product END =
                             e.estimate_sla_product)
               LEFT JOIN lp_dw.routing r
                         ON r.route_code = s.origin || '-' || s.destination AND
                            ( s.product = r.product)
  			   LEFT JOIN genesis.network_routing rr
                         ON rr.route = s.origin || '-' || s.destination AND
                            ( s.product = rr.product)
     ) A
WHERE stt_booked_at::DATE BETWEEN ((CURRENT_TIMESTAMP + INTERVAL '7 Hours')::date - INTERVAL '30 DAY') AND (CURRENT_TIMESTAMP + INTERVAL '7 Hours')::date
          --   WHERE stt_booked_at::DATE BETWEEN '2021-05-01' AND CURRENT_DATE
      -- where pod_month_year >= '2021-09' or pod_month_year = '2021-04'
    );
--XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
--DROP TABLE IF EXISTS dmt.sla;
DROP TABLE IF EXISTS lp_data_temp.dmt_sla;
create TABLE lp_data_temp.dmt_sla 
--create TABLE dmt.sla 
  DISTSTYLE KEY
  DISTKEY (stt_no) 
  SORTKEY (origin,destination,stt_booked_at,pod_date)
  AS ( 
WITH data_dmt AS (SELECT CASE
                             WHEN mapping_dmt LIKE '%(P)%' THEN REPLACE(mapping_dmt, '(P)', ''
                                 )
                             WHEN mapping_dmt LIKE '%(PL)%' THEN REPLACE(mapping_dmt, '(PL)', ''
                                 )
                             WHEN mapping_dmt LIKE '%(V)%' THEN REPLACE(mapping_dmt, '(V)', ''
                                 )
                             ELSE mapping_dmt
                             END AS mapping_dmt,
                         destination,
                         CASE
                             WHEN end_point LIKE '%(P)%' THEN REPLACE(end_point, '(P)', ''
                                 )
                             WHEN end_point LIKE '%(PL)%' THEN REPLACE(end_point, '(PL)', ''
                                 )
                             WHEN end_point LIKE '%(V)%' THEN REPLACE(end_point, '(V)', ''
                                 )
                             ELSE end_point
                             END AS end_end,
                         fwd_area_dest2
                  FROM (SELECT DISTINCT SPLIT_PART(fwd_area_dest, ',', 1
                                            ) || ',' || SPLIT_PART(fwd_area_dest, ',', 2
                                            )         AS mapping_dmt,
                                        destination,
                                        fwd_area_dest AS fwd_area_dest2,
                                        SPLIT_PART(fwd_area_dest, ',', 3
                                            )         AS end_point
                        FROM lp_data_temp.data_a
                       )
),

     data_temp AS (SELECT DISTINCT SPLIT_PART(mapping_city, ',', 1
                                       ) || ', ' || SPLIT_PART(mapping_city, ',', 2
                                       ) AS mapping,
                                   threelc,
                                   kab_kota,
                                   update_ket_oktober,
                                   update_zona_oktober
                   FROM lp_data_temp.bang_sla_temp
     ),

     data_temp0 AS (SELECT A.*,
                           B.*
                    FROM data_dmt A
                             LEFT JOIN
                         data_temp B ON A.mapping_dmt = B.mapping
                             AND A.destination = b.threelc
                             AND TRIM(a.end_end
                                     ) = TRIM(b.kab_kota
                                     )
     ),

     data_temp2 AS (SELECT DISTINCT SPLIT_PART(mapping_city, ',', 2
                                        ) || ', ' || SPLIT_PART(mapping_city, ',', 3
                                        )              AS mapping2,
                                    threelc            AS threelc2,
                                    update_ket_oktober AS update_ket_oktober2,
                                    MAX(update_zona_oktober
                                        )              AS update_zona_oktober2
                    FROM lp_data_temp.bang_sla_temp
                    GROUP BY 1, 2, 3
     ),

     data_pre AS (SELECT A.*,
                         c.*
                  FROM data_temp0 A
                           LEFT JOIN
                       data_temp2 C ON TRIM(A.mapping_dmt
                                           ) = TRIM(C.mapping2
                                           )
                           AND TRIM(A.destination
                                   ) = TRIM(C.threelc2
                                   )
                           AND A.end_end = ''
     ),
     data_final AS (SELECT fwd_area_dest2,
                           CASE
                               WHEN threelc IS NULL THEN threelc2
                               ELSE threelc
                               END AS threelc_final,
                           CASE
                               WHEN update_ket_oktober IS NULL THEN update_ket_oktober2
                               ELSE update_ket_oktober
                               END AS update_ket_oktober_final,
                           CASE
                               WHEN update_zona_oktober IS NULL THEN update_zona_oktober2
                               ELSE update_zona_oktober
                               END AS update_zona_oktober_final
                    FROM data_pre
     )

SELECT *,
       datediff(days, bkd, sti)      AS First_Mile,
       datediff(days, sti, sti_dest) AS Middle_Mile,
       datediff(days, sti_dest, pod) AS Last_Mile
FROM (SELECT A.*,
             CASE
                 WHEN A.source IN ('BUKALAPAK', 'TOKOPEDIA') THEN 'MARKETPLACE'
                 WHEN A.source = 'CORPORATE' THEN 'CORPORATE'
                 ELSE 'RETAIL'
                 END                                                                                             AS GROUPING_SOURCE,
             T.mother_account,
             CASE
                 WHEN B.update_zona_oktober_final IS NULL THEN 'Undefined'
                 ELSE B.update_zona_oktober_final END                                                            AS update_zona_oktober_final
              ,
             B.update_ket_oktober_final,
             dateadd(days, sla_max, A.stt_booked_at)                                                             AS ETA_SLA,
             CASE
                 WHEN pod_date IS NOT NULL THEN datediff(days, A.stt_booked_at, pod_date)
                 WHEN pod_date IS NULL AND last_status IN ('POD', 'CODREJ')
                     THEN 0 END                                                                                  AS act_sla,
             CASE
                 WHEN pod_date IS NOT NULL THEN datediff(days, A.stt_booked_at, pod_date)
                 ELSE datediff(days, now, ETA_SLA) END                                                           AS diff_sla,
             CASE
                 WHEN last_status IN ('CNX', 'STT REMOVE', 'SCRAP', 'CANX') THEN 'Closed'
                 WHEN last_status IN ('POX', 'SPOD') THEN 'Forced Closed'
                 WHEN last_status IN ('POD', 'CODREJ') AND datediff(days, A.stt_booked_at, pod_date) <= sla_max AND
                      pod_date IS NOT NULL THEN 'Meet SLA'
                 WHEN last_status IN ('POD', 'CODREJ') AND datediff(days, A.stt_booked_at, pod_date) > sla_max AND
                      pod_date IS NOT NULL THEN 'Late SLA'
                 WHEN last_status NOT IN ('POD', 'CODREJ') AND datediff(days, A.stt_booked_at, now) >= sla_max AND
                      pod_date IS NULL THEN 'ON PROCESS Late SLA'
                 WHEN last_status NOT IN ('POD', 'CODREJ') AND datediff(days, A.stt_booked_at, now) < sla_max AND
                      pod_date IS NULL THEN 'ON PROCESS Meet SLA'
                 ELSE 'Undefined' END                                                                            AS On_Process,
             K.bkd,
             K.pup,
             K.sti,
             K.sti_sc,
             K.hnd,
             K.cons,
             K.bagging,
             K.bag,
             K.rts,
             K.cargo_train,
             K.cargo_truck,
             K.cargo_plane,
             K.transit,
             K.mis_route,
             K.shortland,
             K.sti_dest,
             K.sti_dest_sc,
             K.del,
             K.hal,
             K.oda,
             K.dex,
             K.sdex,
             K.codrej,
             K.pod,
             K.spod,
             K.rejected,
             K.stt_adjusted,
             K.stt_remove,
             K.scrap,
             K.cnx,
             CASE
                 WHEN A.origin = A.destination THEN 'INTRA-CITY'
                 WHEN BG.pulau = BC.pulau THEN 'INTRA-ISLAND'
                 WHEN BG.pulau <> BC.pulau THEN 'INTER-ISLAND'
                 WHEN A.product = 'INTERPACK' THEN 'INTERNATIONAL'
                 ELSE 'Undefined' END                                                                            AS route_type,
             G.first,
             G.last,
             G.first_cargo_created,
             G.first_cargo_type,
             G.last_cargo_arr,
             G.last_cargo_type,
             G.lag_moda,
             G.lag_route
      FROM lp_data_temp.data_a A
               LEFT JOIN data_final B
                         ON A.destination = B.threelc_final AND A.fwd_area_dest = B.fwd_area_dest2
               LEFT JOIN lp_dw.corporate_master T
                         ON A.client_code = T.customer_branch_code
               LEFT JOIN dmt.stt_shipment K
                         ON A.stt_no = K.stt_no
               LEFT JOIN (SELECT A.stt_no, B.*
                          FROM dmt.stt_cargo B
                                   LEFT JOIN genesis.stt A ON A.id = B.stt_id) G ON A.stt_no = G.stt_no
               LEFT JOIN lp_data_temp.initial_route_type Bg ON Bg.lc = A.origin
               LEFT JOIN lp_data_temp.initial_route_type BC ON BC.lc = A.destination)
    );
DELETE from dmt.sla where (stt_no) in (select stt_no from lp_data_temp.dmt_sla); 
INSERT into dmt.sla (select * from lp_data_temp.dmt_sla);
--XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
END;
$$


-- stuck status calculation

CREATE OR REPLACE PROCEDURE lp_dw.salesforce_v1(jobname character varying(100))
 LANGUAGE plpgsql
AS $$
BEGIN



--truncate table lp_dw.STT_Compare;
--
DROP TABLE IF EXISTS salesforce_compare;


create temp table salesforce_compare as
(  
  
   select A.*, 
	CASE 
  	WHEN stt_last_status_id = 'CARGO TRUCK' THEN 'TRUCK' 
  	WHEN stt_last_status_id IN ('CARGO TRAIN', 'CARGO PLANE') THEN 'E-CARGO'
    else stt_last_status_id 
  	END AS STATUS_SYSTEM,
 	CASE 
    WHEN STATUS_SYSTEM in ('BKD','PUP','STT ADJUSTED','BAGGING', 'CONS','STI-SC','STI','STT REMOVE') THEN 'First Mile'
    WHEN STATUS_SYSTEM in ('E-CARGO','CARGO TRUCK', 'TRUCK', 'CARGO TRAIN','CARGO PLANE', 'SHORTLAND','TRANSIT','MIS-ROUTE') THEN 'Linehaul'
    WHEN STATUS_SYSTEM in ('STI-DEST','STI DEST-SC', 'HND','DEL','DEX','HAL','ODA','REJECTED') THEN 'Last Mile'
    ELSE 'Finished'
    END AS GROUPING,
    Case 
    when product != 'ONEPACK' AND diff_status <=-1 THEN 'FALSE' 
  	when product = 'ONEPACK' AND diff_status <=0 THEN 'FALSE'
      ELSE 'TRUE' 
      END AS valid_status,
    Case 
    when product = 'ONEPACK' AND diff_sla <=0 THEN 'FALSE' 
    when product != 'ONEPACK' AND diff_sla <=1 and grouping in ('Linehaul', 'First Mile') THEN 'FALSE' 
    when product != 'ONEPACK' AND diff_sla <=0 and grouping = 'Last Mile' THEN 'FALSE' ELSE 'TRUE'
    END AS valid_sla,
    CASE 
    WHEN PRODUCT = 'ONEPACK' AND VALID_STATUS = 'FALSE' THEN 'FALSE'
    WHEN PRODUCT != 'ONEPACK' AND grouping in ('Linehaul', 'First Mile') AND VALID_SLA = 'FALSE' THEN 'FALSE'
    WHEN PRODUCT != 'ONEPACK' and grouping = 'Last Mile' AND VALID_STATUS = 'FALSE' AND VALID_SLA = 'FALSE' THEN 'FALSE'
    ELSE 'TRUE'
    END AS VALID_FINAL
    from (
    select A.*, datediff(hours,now, ETA_status) AS diff_status, datediff(days,now, ETA_SLA) AS diff_sla
    from (
    select a.stt_no,  
      CASE
                                   WHEN a.stt_no LIKE '09%' OR a.stt_no LIKE '10%' OR a.stt_no LIKE '11%' THEN 'POS'
                                   WHEN (a.stt_no LIKE '76%' OR a.stt_no LIKE '77%' OR a.stt_no LIKE '78%' OR
                                         a.stt_no LIKE '97%' OR
                                         a.stt_no LIKE '98%'
                                       OR a.stt_no LIKE '99%' OR a.stt_no LIKE '95%' OR a.stt_no LIKE '96%')
                                       OR (a.stt_no LIKE '19%' AND stt_booked_by_type = 'internal')
                                       THEN 'CORPORATE'
                                   WHEN a.stt_no LIKE '88%' AND
                                        stt_shipment_id LIKE 'B1%' OR stt_shipment_id LIKE 'B2%' OR
                                        stt_shipment_id LIKE ' B2%'
                                       OR stt_shipment_id LIKE '  B2%' OR stt_shipment_id LIKE '   B2%' OR
                                        stt_shipment_id LIKE '    B2%' OR
                                        stt_shipment_id LIKE '     B2%'
                                       OR stt_shipment_id LIKE ' B%' OR stt_shipment_id LIKE '  B%' OR
                                        stt_shipment_id LIKE '   B%'
                                       THEN 'BUKALAPAK'
                                   WHEN a.stt_no LIKE '88%' AND
                                        stt_shipment_id LIKE 'TK%' OR stt_shipment_id LIKE 'T1%' OR
                                        stt_shipment_id LIKE ' T%'
                                       OR stt_shipment_id LIKE '  T%' OR stt_shipment_id LIKE '   T%' OR
                                        stt_shipment_id LIKE '%T1%'
                                       THEN 'TOKOPEDIA'
                                   WHEN a.stt_no LIKE '88%' OR
                                        a.stt_no LIKE '81%' AND
                                        stt_shipment_id LIKE 'AG%' OR stt_shipment_id LIKE ' AG%' OR
                                        stt_shipment_id LIKE 'AD%'
                                       OR stt_shipment_id LIKE ' AD%' OR stt_shipment_id LIKE 'AS%' OR
                                        stt_shipment_id LIKE ' AS%' OR
                                        stt_shipment_id LIKE 'AP%'
                                       OR stt_shipment_id LIKE ' AP%' THEN 'CUST APP'
                                   WHEN a.stt_no LIKE '88%' AND stt_shipment_id LIKE 'AW%' THEN 'WHATS APP'
                                   WHEN a.stt_no LIKE '19%' AND stt_booked_by_type = 'pos' THEN 'CBP'
                                   ELSE 'OTHER'
                                   END               AS source,
      a.stt_product_type as PRODUCT, a.stt_last_status_id, a.stt_updated_at,
      case when stt_product_type = 'ONEPACK' THEN dateadd(hours,8,a.stt_updated_at)
      else dateadd(hours,24,a.stt_updated_at) 
      END as ETA_status, 
      case when stt_product_type = 'ONEPACK' THEN 8 
              WHEN stt_product_type != 'ONEPACK' THEN 24 
              END AS status_params,
      case when a.stt_product_type = 'ONEPACK' THEN 1 ELSE b.sla_max END as stt_sla_max,
      a.stt_booked_at as stt_date,
      case when a.stt_product_type = 'ONEPACK' THEN dateadd(days,1,a.stt_booked_at)
      ELSE dateadd(days,b.sla_max,a.stt_booked_at) end as ETA_SLA,
      current_timestamp::timestamp + interval '7 hour' AS now
    from  genesis.stt a
      left join ( select distinct stt_no,CASE WHEN sla_origin IS NULL THEN 0 ELSE sla_origin::int END + CASE WHEN sla_destination IS NULL THEN 0 ELSE sla_destination::int END +
             CASE WHEN estimate_sla IS NULL THEN 0 ELSE estimate_sla::int END AS sla_max from 
(select S.stt_no,
  CASE WHEN d.sla_origin IS NULL THEN 0 ELSE d.sla_origin END            AS sla_origin,
  CASE WHEN x.sla_destination IS NULL THEN 0 ELSE x.sla_destination END            AS sla_destination,
   CASE WHEN SUBSTRING(e.estimate_sla, 3, 1) = '' then null 
  	else 	SUBSTRING(e.estimate_sla, 3, 1)
  	end                                    AS estimate_sla
	
from genesis.stt s
                     LEFT JOIN genesis.district d
                               ON s.stt_origin_district_name = d.name
                     LEFT JOIN genesis.district x
                               ON s.stt_destination_district_name = x.name
                     LEFT JOIN genesis.estimate_sla e
                               ON s.stt_origin_city_id = e.estimate_sla_origin AND
                                  s.stt_destination_city_id = e.estimate_sla_destination AND
                                  (CASE WHEN s.stt_product_type = 'LANDPACK' THEN 'JAGOPACK' ELSE s.stt_product_type END =
                                  e.estimate_sla_product)
                                  )) b
      on a.stt_no = b.stt_no
        WHERE a.stt_last_status_id not in ('POD','CNX','POX','CANX','SCRAP','POX','RTS', 'CODREJ')
      ) A
     ) A
     where stt_date::DATE BETWEEN '2021-10-17' AND CURRENT_DATE 
);

delete from lp_dw.sf_stt_compare
where (stt_no) in (select stt_no from salesforce_compare);

insert into lp_dw.sf_stt_compare (
  select * from salesforce_compare);
   
   
call lp_dw.salesforce ('fs');

    
--call salesforce.update_flag ('s');
call salesforce.mitra_phone_new ('d');
call salesforce.recipient_phone_new ('d');
call salesforce.sender_phone_new ('d');

--


--

    
    
call salesforce.update_sla_max ('s');

--
--delete from lp_dw.stt_validation 
--where flag = 1 and (stt_no,grouping) in (select stt_no, grouping from salesforce.close_ticket);
--
--delete from lp_dw.stt_compare 
--where valid_final = 'FALSE' and (stt_no,grouping) in (select stt_no, grouping from salesforce.close_ticket);
--


call lp_dw.salesforce_open_ticket('ds');


  unload (' select * from lp_dw.sf_STT_Validation where flag = 1 ') 
  to 's3://lp-s3-salesforce/pos_master/process/' 
  iam_role 'arn:aws:iam::312533407275:role/lp-role-redshift-customized-dev' 
  csv header ALLOWOVERWRITE delimiter ';' parallel off;

END;
$$


------ cleansing phone number

CREATE OR REPLACE PROCEDURE salesforce.mitra_phone_new(jobname character varying(100))
 LANGUAGE plpgsql
AS $$
BEGIN 

DROP TABLE IF EXISTS clean_mitra_phone;
create temp table clean_mitra_phone as (
select mitra_phone as old, valid_2 as new_mitra_phone, phone_valid
from
(select distinct *, CASE WHEN SUBSTRING(valid_2, 1, 2) = '08' AND LENGTH(valid_2) BETWEEN 10 AND 13 
                    AND SUBSTRING(valid_2, 3, 20) NOT LIKE '00%'
                    AND SUBSTRING(valid_2, 3, 20) NOT LIKE '111111%'
                    AND SUBSTRING(valid_2, 3, 20) NOT LIKE '222222%'
                    AND SUBSTRING(valid_2, 3, 20) NOT LIKE '444444%'
                    AND SUBSTRING(valid_2, 3, 20) NOT LIKE '555555%'
                    AND SUBSTRING(valid_2, 3, 20) NOT LIKE '666666%'
                    AND SUBSTRING(valid_2, 3, 20) NOT LIKE '777777%'
                    AND SUBSTRING(valid_2, 3, 20) NOT LIKE '888888%'
                    AND SUBSTRING(valid_2, 3, 20) NOT LIKE '999999%'
                    THEN 'TRUE' ELSE 'FALSE' END AS phone_valid
from
(select *, CASE 
            WHEN SUBSTRING(valid_1, 1, 2) = '62' THEN replace(SUBSTRING(valid_1, 1, 2), '62', CONCAT('0',SUBSTRING(valid_1, 3, 20)))
            WHEN SUBSTRING(valid_1, 1, 2) = '65' THEN replace(SUBSTRING(valid_1, 1, 2), '65', CONCAT('0',SUBSTRING(valid_1, 3, 20)))
            else valid_1 end as valid_2
from
(SELECT mitra_phone,
        CASE 
            WHEN SUBSTRING(mitra_phone, 1, 5) = '62808' THEN replace(SUBSTRING(mitra_phone, 1, 5), '62808', CONCAT('',SUBSTRING(mitra_phone, 4, 20)))
            WHEN SUBSTRING(mitra_phone, 1, 4) = '6208' THEN replace(SUBSTRING(mitra_phone, 1, 4), '6208', CONCAT('',SUBSTRING(mitra_phone, 3, 20)))
            WHEN SUBSTRING(mitra_phone, 1, 4) = '6262' THEN replace(SUBSTRING(mitra_phone, 1, 4), '6262', CONCAT('0',SUBSTRING(mitra_phone, 5, 20)))
            WHEN SUBSTRING(mitra_phone, 1, 4) = '6228' THEN replace(SUBSTRING(mitra_phone, 1, 4), '6228', CONCAT('0',SUBSTRING(mitra_phone, 4, 20)))
            WHEN SUBSTRING(mitra_phone, 1, 1) = '8' THEN replace(SUBSTRING(mitra_phone, 1, 1), '8', CONCAT('0',SUBSTRING(mitra_phone, 1, 20)))
            WHEN SUBSTRING(mitra_phone, 1, 1) = '2' THEN replace(SUBSTRING(mitra_phone, 1, 1), '2', CONCAT('0',SUBSTRING(mitra_phone, 2, 20)))
            WHEN SUBSTRING(mitra_phone, 1, 2) = '00' THEN replace(SUBSTRING(mitra_phone, 1, 2), '00', CONCAT('',SUBSTRING(mitra_phone, 2, 20)))
            WHEN mitra_phone LIKE '%-%'                                        THEN replace(mitra_phone, '-', '')
            WHEN SUBSTRING(mitra_phone, 1, 1) NOT IN ('1', '2', '3', '4', '5', '6', '7', '8', '9', '0') THEN NULL
            ELSE mitra_phone END AS valid_1
from lp_dw.sf_stt_validation
))));	

update lp_dw.sf_stt_validation n
set mitra_phone = a.new_mitra_phone
from clean_mitra_phone a
where mitra_phone = a.old;
   
END;

$$




