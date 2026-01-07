def assess_severity(humidity, temperature):
    if humidity > 75 and temperature > 30:
        return "High"
    elif humidity > 60:
        return "Medium"
    return "Low"


def pesticide_optimization(severity):
    if severity == "High":
        return "Targeted chemical treatment required"
    elif severity == "Medium":
        return "Organic treatment with limited chemical use"
    return "Preventive organic measures only"
