----------------------------------------------------------------------------------------------------------------
-- Overall Credit Usage
select warehouse_name,sum(credits_used) as total_credits_used 
from snowflake.account_usage.warehouse_metering_history 
where warehouse_name in ('COMPUTE_WH', 'DBT_WH', 'STREAMLIT_WH') 
group by 1 
order by 2 desc limit 10;


----------------------------------------------------------------------------------------------------------------
-- Credits Billed per Month
select date_trunc('MONTH', usage_date) as Usage_Month, 
        sum(CREDITS_BILLED) 
from snowflake.account_usage.metering_daily_history 
group by Usage_Month


----------------------------------------------------------------------------------------------------------------
-- Credit Usage Over Time
select start_time::date as usage_date, 
        warehouse_name, 
        sum(credits_used) as total_credits_used 
from snowflake.account_usage.warehouse_metering_history 
where warehouse_name in ('COMPUTE_WH', 'DBT_WH', 'STREAMLIT_WH') 
group by 1,2 
order by 2,1;