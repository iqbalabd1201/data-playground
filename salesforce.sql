CREATE OR REPLACE PROCEDURE salesforce.pos_master_reports_v5(jobname character varying(100))
    LANGUAGE plpgsql AS
$$
BEGIN


CREATE TEMP TABLE stt_reports_v14	
      DISTSTYLE KEY
      DISTKEY (stt_number)
    AS(
        SELECT *
    FROM (
							select
                              a_stt_id as stt_number,
                              a_source as channel,
                              a_last_status as status,
                              d_product as product,
                              e_cnt_weight as chargeable_weight,
                              a_cust_name as origin_name,
      						  case 
                                            when SUBSTRING( a_customer_phone, 1, 1 ) = 8 THEN CONCAT('08',SUBSTRING(a_customer_phone, 2, 20)) 
                                            when SUBSTRING( a_customer_phone, 1, 2 ) = 62 THEN CONCAT('08',SUBSTRING(a_customer_phone, 3, 20))
                                            when SUBSTRING( a_customer_phone, 1, 3 ) = '+62' THEN CONCAT('0',SUBSTRING(a_customer_phone, 4, 20))
                                            else a_customer_phone 
                                            end as origin_phone,
                              c_origin as origin,
                              c_destination as destination,
                              a_consignee_name as destination_name,
      						  case 
                                            when SUBSTRING( a_consignee_phone, 1, 1 ) = 8 THEN CONCAT('08',SUBSTRING(a_consignee_phone, 2, 20)) 
                                            when SUBSTRING( a_consignee_phone, 1, 2 ) = 62 THEN CONCAT('08',SUBSTRING(a_consignee_phone, 3, 20))
                                            when SUBSTRING( a_consignee_phone, 1, 3 ) = '+62' THEN CONCAT('0',SUBSTRING(a_consignee_phone, 4, 20))
                                            else a_consignee_phone 
                                            end as destination_phone,
                              d_code_id as pos_code,
                              d_code_name as pos_name,
                              a_booked_by as a_booked_by,
                              a_source as a_source,
                              b_sla_max as sla_max,
                              DATE_TRUNC('minute', b_stt_date::timestamp) as stt_created_date,
                              CURRENT_DATE::timestamp -  interval '1 day' as da_batchdate,      
                              CASE
                                                      WHEN status = 'CANX' or status = 'CNX' OR status = 'STT REMOVE' THEN '1'
                                                      WHEN status != 'CANX' or status != 'CNX' OR status != 'STT REMOVE' OR status != 'BKD' THEN '2'
                                                      WHEN status = 'POD' THEN '3'
                                                      ELSE '0'
                                                      END AS flag
							FROM dmt.customer_hist_trx_new
      ) A 
      WHERE 
          (stt_created_date::date between current_date - interval '1 days' and current_date) 
      
);
	DELETE FROM salesforce.stt_reports_test WHERE stt_number IN (SELECT stt_number FROM stt_reports_v14);
            insert into salesforce.stt_reports_test(
							select
                            stt_number,
                            channel,
                            status,
                            product,
                            chargeable_weight,
                            origin_name,
      						origin_phone,
                            origin,
                            destination,
                            destination_name,
      						destination_phone,
                            pos_code,
                            pos_name,
                            a_booked_by,
                            a_source,
                            sla_max,
                            stt_created_date,
                            da_batchdate,      
                                                          CASE
                                                      WHEN da_batchdate::date not between current_date - interval '1 days' and current_date THEN '0'
                                                      ELSE flag
                                                      END AS flag ,
              				'0' as pos_phone
                            from  stt_reports_v14 
                
  );     
update salesforce.stt_reports_test t
set pos_phone = t2.new_contact
from lp_dwh.pos_master t2 
where t.pos_code = t2.poscode;

unload ('
SELECT A.*,A.da_batchdate::date AS stt_date
FROM (
    select * from salesforce.stt_reports_test 
) A
        ')
to 's3://lp-s3-salesforce/pos_master' 
iam_role 'arn:aws:iam::312533407275:role/lp-role-redshift-customized-dev'
PARTITION BY (stt_date)
CSV header
ALLOWOVERWRITE
DELIMITER ';'                                                                        
parallel off;
  

END;
$$
call salesforce.pos_master_reports_v5 ('sd')
