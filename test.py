from datetime import datetime

date_str = "26.09 14:21"
current_year = datetime.now().year
date_with_year = f"{date_str} {current_year}"
date_obj = datetime.strptime(date_with_year, "%d.%m %H:%M %Y")

now = datetime.now()
difference = now - date_obj

total_seconds = int(difference.total_seconds())
hours = total_seconds // 3600
minutes = (total_seconds % 3600) // 60

print(f"{hours:02}:{minutes:02}")
