CREATE OR REPLACE
PROCEDURE sp_genesis_stt_piece_v7(jobname character varying(100)) LANGUAGE plpgsql AS $$ BEGIN DROP TABLE IF EXISTS sp_genesis_stt_piece_v5;

CREATE TEMP TABLE genesis_stt_piece DISTSTYLE KEY DISTKEY (stt_piece_id) AS (
select
	stt_piece_id::bigint as stt_piece_id,
	stt_id::bigint as stt_id,
	stt_piece_no::bigint as stt_piece_no,
	history_id::bigint as history_id,
	history_actor_id::bigint as history_actor_id,
	history_created_by::bigint as history_created_by,
	history_reff_id::bigint as history_reff_id,
	stt_piece_length::float as stt_piece_length,
	stt_piece_width::float as stt_piece_width,
	stt_piece_height::float as stt_piece_height,
	stt_piece_gross_weight::float as stt_piece_gross_weight,
	stt_piece_volume_weight::float as stt_piece_volume_weight,
	stt_piece_last_status_id as stt_piece_last_status_id,
	history_status as history_status,
	history_location as history_location,
	history_meta as history_meta,
	history_actor_name as history_actor_name,
	history_actor_role as history_actor_role,
	history_remarks as history_remarks,
	history_receiver_name as history_receiver_name,
	history_reason as history_reason,
	history_attachment as history_attachment,
	history_created_name as history_created_name,
	TO_TIMESTAMP(history_created_at,
	'yyyy-mm-dd HH24:MI:SS') AS history_created_at,
	TO_TIMESTAMP(history_action_created_at,
	'yyyy-mm-dd HH24:MI:SS') AS history_action_created_at,
	TO_TIMESTAMP(process_created,
	'yyyy-mm-dd HH24:MI:SS') AS process_created,
	TO_TIMESTAMP(process_finished,
	'yyyy-mm-dd HH24:MI:SS') AS process_finished,
	user_process as user_process,
	validation as validation
FROM
	genesis_temp.stt_piece_temp3 );

DELETE
FROM
	genesis.stt_piece
WHERE
	history_id IN (
	SELECT
		history_id
	from
		genesis_stt_piece);

INSERT
	INTO
	genesis.stt_piece (
	SELECT
		*
	FROM
		genesis_stt_piece);
END;

$$
