# Current Temp
current_temp = '''
SELECT *
FROM "dkelly-proj/cbus_temps"."temp_log"
WHERE date = (
    SELECT max(date)
    FROM "dkelly-proj/cbus_temps"."temp_log");
'''

# Earliest Data
min_date = '''
SELECT min(date)
FROM "dkelly-proj/cbus_temps"."temp_log";
'''

# Daily Averages
daily = '''
Select date_trunc('day', date) "date", avg(temp) "temp"
from "dkelly-proj/cbus_temps"."temp_log"
group by 1
order by 1;
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
