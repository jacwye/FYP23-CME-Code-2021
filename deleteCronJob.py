from crontab import CronTab

## For LINUX based systems
cron = CronTab(True)
print('Removing all cron jobs')
cron.remove_all()
cron.write()
print('Completed')

## For WINDOWS based systems
# Provide a tab file containing the cron jobs
# file_cron = CronTab(tabfile="")
# file_cron.remove_all()


