CREATE OR REPLACE
PROCEDURE genesis_pivot_payment(jobname character varying(100))
    LANGUAGE plpgsql AS
$$
BEGIN   
    CREATE TEMP TABLE genesis_payment
        DISTKEY (pg_trx_stt_no)
        SORTKEY (pg_trx_stt_no,
pg_trx_created_at)
    AS (
select
	pg_trx_stt_no,
	pg_trx_type,
	CASE
		WHEN
                       pg_trx_activity = 'debit'
                       THEN pg_trx_amount
		WHEN pg_trx_activity = 'credit'
                       THEN -1 * pg_trx_amount
		ELSE 0
	END AS pg_trx_amount,
	pg_trx_activity,
	pg_trx_created_at
from
	genesis_temp.payment_pivot_temp);

DELETE
FROM
	genesis.payment_gateway_transaction_v1
WHERE
	pg_trx_stt_no IN (
	SELECT
		pg_trx_stt_no
	from
		genesis_payment);

INSERT
	INTO
	genesis.payment_gateway_transaction_v1 (
	SELECT
		*
	FROM
		(
		SELECT
			pg_trx_stt_no AS pg_trx_stt_no,
			TO_TIMESTAMP(pg_trx_created_at,
			'yyyy-mm-dd HH24:MI:SS') AS pg_trx_created_at,
			CASE
				WHEN pg_trx_type = 'booking' THEN pg_trx_amount
				ELSE 0
			END AS booking,
			CASE
				WHEN pg_trx_type = 'booking_cancel' THEN pg_trx_amount
				ELSE 0
			END AS booking_cancel,
			CASE
				WHEN pg_trx_type = 'booking_commission' THEN pg_trx_amount
				ELSE 0
			END AS booking_commission,
			CASE
				WHEN pg_trx_type = 'booking_commission_cancel' THEN pg_trx_amount
				ELSE 0
			END AS booking_commission_cancel,
			CASE
				WHEN pg_trx_type = 'cod_fee' THEN pg_trx_amount
				ELSE 0
			END AS cod_fee,
			CASE
				WHEN pg_trx_type = 'insurance_booking_cancel' THEN pg_trx_amount
				ELSE 0
			END AS insurance_booking_cancel,
			CASE
				WHEN pg_trx_type = 'insurance_commission' THEN pg_trx_amount
				ELSE 0
			END AS insurance_commission,
			CASE
				WHEN pg_trx_type = 'insurance_commission_cancel' THEN pg_trx_amount
				ELSE 0
			END AS insurance_commission_cancel,
			CASE
				WHEN pg_trx_type = 'booking_adjustment' THEN pg_trx_amount
				ELSE 0
			END AS booking_adjustment,
			CASE
				WHEN pg_trx_type = 'booking_adjustment_penalty' THEN pg_trx_amount
				ELSE 0
			END AS booking_adjustment_penalty,
			CASE
				WHEN pg_trx_type = 'booking_cancel_penalty' THEN pg_trx_amount
				ELSE 0
			END AS booking_cancel_penalty,
			CASE
				WHEN pg_trx_type = 'booking_comission' THEN pg_trx_amount
				ELSE 0
			END AS booking_comission,
			CASE
				WHEN pg_trx_type = 'booking_comission_adjustment' THEN pg_trx_amount
				ELSE 0
			END AS booking_comission_adjustment,
			CASE
				WHEN pg_trx_type = 'booking_comission_cancel' THEN pg_trx_amount
				ELSE 0
			END AS booking_comission_cancel,
			CASE
				WHEN pg_trx_type = 'booking_comission_revert' THEN pg_trx_amount
				ELSE 0
			END AS booking_comission_revert,
			CASE
				WHEN pg_trx_type = 'booking_revert' THEN pg_trx_amount
				ELSE 0
			END AS booking_revert,
			CASE
				WHEN pg_trx_type = 'cod_earning' THEN pg_trx_amount
				ELSE 0
			END AS cod_earning,
			CASE
				WHEN pg_trx_type = 'discount_booking_shipment_favourite' THEN pg_trx_amount
				ELSE 0
			END AS discount_booking_shipment_favourite,
			CASE
				WHEN pg_trx_type = 'insurance_comission' THEN pg_trx_amount
				ELSE 0
			END AS insurance_comission,
			CASE
				WHEN pg_trx_type = 'insurance_comission_adjustment' THEN pg_trx_amount
				ELSE 0
			END AS insurance_comission_adjustment,
			CASE
				WHEN pg_trx_type = 'insurance_comission_cancel' THEN pg_trx_amount
				ELSE 0
			END AS insurance_comission_cancel,
			CASE
				WHEN pg_trx_type = 'insurance_comission_revert' THEN pg_trx_amount
				ELSE 0
			END AS insurance_comission_revert,
			CASE
				WHEN pg_trx_type = 'stt_add_adjustment_saldo' THEN pg_trx_amount
				ELSE 0
			END AS stt_add_adjustment_saldo,
			CASE
				WHEN pg_trx_type = 'stt_deduct_adjustment_saldo' THEN pg_trx_amount
				ELSE 0
			END AS stt_deduct_adjustment_saldo,
			CASE
				WHEN pg_trx_type = 'top_up_manual' THEN pg_trx_amount
				ELSE 0
			END AS top_up_manual,
			CASE
				WHEN pg_trx_type = 'top_up_shipment_favourite' THEN pg_trx_amount
				ELSE 0
			END AS top_up_shipment_favourite,
			CASE
				WHEN pg_trx_type = 'withdraw' THEN pg_trx_amount
				ELSE 0
			END AS withdraw
		FROM
			genesis_payment
    )
  );
END;

$$
