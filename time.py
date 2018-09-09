from datetime import datetime, timedelta

d = datetime.today() - timedelta(days=30)

print(d.strftime("%d.%m.%Y"))