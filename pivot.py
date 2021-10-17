import pandas as pd
import numpy as np
df = pd.read_csv('temp000.csv',sep=';')
df['pg_trx_amount'] = np.where(df['pg_trx_activity'] == 'debit',
                                           df['pg_trx_amount'] * 1,
                                           df['pg_trx_amount'] * -1)
df = df.drop(columns='pg_trx_activity')
dfp=pd.pivot_table(df,index=['pg_trx_stt_no'],columns='pg_trx_type',values='pg_trx_amount',fill_value=0)
cols = ["booking","booking_adjustment","booking_adjustment_penalty","booking_cancel","booking_cancel_penalty","booking_comission","booking_comission_adjustment","booking_comission_cancel","booking_comission_revert","booking_revert","cod_earning","cod_fee","discount_booking_shipment_favourite","insurance_booking_cancel",
        "insurance_comission","insurance_comission_adjustment","insurance_comission_cancel","insurance_comission_revert","stt_add_adjustment_saldo","stt_deduct_adjustment_saldo","top_up_manual","top_up_shipment_favourite","withdraw"]

dfp = dfp.assign(**{col : 0 for col in np.setdiff1d(cols,dfp.columns.values)})
dfp['pg_trx_stt_no'] = dfp.index
cols = list(dfp.columns)
cols = [cols[-1]] + cols[:-1]
dfp = dfp[cols]
dfp.to_csv('temp.csv', sep=';',index=False)
