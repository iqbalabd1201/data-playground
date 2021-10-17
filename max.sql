CREATE OR REPLACE PROCEDURE genesis_temp.payment_pivot_temp(jobname character varying(100))
 LANGUAGE plpgsql
AS $$
BEGIN
  
  
  CREATE TEMP TABLE pivot_1	
        DISTSTYLE KEY
        DISTKEY (pg_trx_stt_no)
      AS(
          SELECT *
      FROM genesis.payment_gateway_transaction where pg_trx_stt_no in (select distinct pg_trx_stt_no from genesis_temp.payment_gateway_transaction_temp) 
  );
      DELETE FROM genesis_temp.payment_pivot_temp WHERE pg_trx_stt_no IN (SELECT pg_trx_stt_no FROM pivot_1);
              insert into genesis_temp.payment_pivot_temp(
                            SELECT
                                pgt.pg_trx_stt_no ,
                                pgt.pg_trx_type,
                                pgt.pg_trx_amount ,
                                pgt.pg_trx_activity ,
                                a.max_date
                            FROM
                                pivot_1 pgt
                            INNER JOIN 
                            (
                                SELECT
                                    pg_trx_stt_no,
                                    pg_trx_type ,
                                    MAX(pg_trx_created_at) as max_date
                                FROM
                                    pivot_1
                                GROUP BY
                                    pg_trx_stt_no,
                                    pg_trx_type)a
                            on
                                pgt.pg_trx_stt_no = a.pg_trx_stt_no
                                and a.max_date = pgt.pg_trx_created_at
                                and a.pg_trx_type = pgt.pg_trx_type

);

    unload ('
    SELECT A.*
    FROM (
        select * from genesis_temp.payment_pivot_temp 
    ) A
            ')
    to  's3://lp-s3-genesis/payment_gateway_transaction/output/input_pivot/temp'
    iam_role 'arn:aws:iam::312533407275:role/lp-role-redshift-customized-dev'
    CSV header
    ALLOWOVERWRITE
    DELIMITER ';'                                                                        
    parallel off;
    
END;
$$
