from datetime import date, timedelta

#method to fill in info for today-container in dashboard.html
def calculate_cycle_predictions(user):
    settings=user.cycle_settings
    logs=user.period_log

    #if no data on account
    if not settings or not logs:
        return{"period": "No cycle data", "ovulation": "No cycle data"}

    #retrieve most recent cycle
    latest_log = sorted(logs, key=lambda x: x.period_start or date.min, reverse=True)[0]
    last_start = latest_log.period_start

    if not last_start:
        return {"period": "No period recorded", "ovulation": "No prediction available"}

    today = date.today()
    cycle_length = settings.avg_cycle_length
    period_length = settings.avg_period_length

    #predictions
    next_period = last_start + timedelta(days=cycle_length)
    days_until_period = (next_period - today).days

    ovulation_day = last_start + timedelta(cycle_length // 2)
    days_until_ovulation = (ovulation_day - today).days

    # fill text
    if days_until_period > 0:
        period_text = f"Next period: {days_until_period} days"
    elif days_until_period==0 or abs(days_until_period) < period_length:
        day_num = abs(days_until_period) + 1
        period_text = f"Period day {day_num}"
    else: period_text="Null"

    if days_until_ovulation > 0:
        ovulation_text = f"Next ovulation: {days_until_ovulation} days"
    elif days_until_ovulation == 0:
        ovulation_text = "Ovulation day"
    elif -2 <= days_until_ovulation <= 2:
        ovulation_text = "High fertility today"
    else: ovulation_text="Null"

    return {"period": period_text, "ovulation": ovulation_text}

