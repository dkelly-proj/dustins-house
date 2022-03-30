from datetime import datetime, timedelta

# Current Temp
current_temp = '''
SELECT *
FROM "dkelly-proj/cbus_temps"."temp_log"
WHERE date = (
    SELECT max(date)
    FROM "dkelly-proj/cbus_temps"."temp_log");
'''

# Daily Averages
daily = '''
WITH avg_temp_tbl AS (
  SELECT date_trunc('day', date) "date", avg(temp) "temp"
  FROM "dkelly-proj/cbus_temps"."temp_log"
  GROUP BY 1
  ORDER BY 1)
SELECT
  date, temp,
  avg(temp)
  over(order by date rows between 9 preceding and current row)
  as moving_avg
FROM avg_temp_tbl;
'''

# Record Low
low = '''
SELECT date, temp
FROM "dkelly-proj/cbus_temps"."temp_log"
WHERE temp = (
    SELECT min(temp)
    FROM "dkelly-proj/cbus_temps"."temp_log");
'''

# Record High
high = '''
SELECT date, temp
FROM "dkelly-proj/cbus_temps"."temp_log"
WHERE temp = (
    SELECT max(temp)
    FROM "dkelly-proj/cbus_temps"."temp_log");
'''

# Daily Highs and Lows
daily_hl = '''
Select date_trunc('day', date) "date", max(temp) "max", min(temp) "min"
from "dkelly-proj/cbus_temps"."temp_log"
group by 1
order by 1;
'''

# Last Week
weekly = '''
Select date, temp
from "dkelly-proj/cbus_temps"."temp_log"
where "date" >= date('{}')
order by 1;
'''.format((datetime.today() - timedelta(days = 7)).strftime('%Y-%m-%d'))

# Humidity Clustering
hum_cluster = '''
SELECT * FROM "dkelly-proj/cbus_temps"."humidity-temps";
'''
