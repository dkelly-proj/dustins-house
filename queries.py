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
