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
