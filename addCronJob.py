from crontab import CronTab

## For LINUX based systems
cron = CronTab(True)

print('Adding a new cron job')

## Change the command accordingly to use the correct file path
job = cron.new(command='cd /Users/Chinmay/Documents/UNI/Summer/Mechanical\ Project/SRS-made2020/Engine && /Users/Chinmay/.pyenv/shims/python sendMachineStatus.py')
job.minute.every(1)

print('Available Jobs:')
for item in cron:
    print(item)

cron.write()
print('Completed')

## For WINDOWS based systems
## Change the command accordingly to use the correct file path
# file_cron = CronTab(tab="""
#     * * * * * cd /Users/Chinmay/Documents/UNI/Summer/Mechanical\ Project/SRS-made2020/Engine && /Users/Chinmay/.pyenv/shims/python sendMachineStatus.py
# """)
# file_cron.write()

