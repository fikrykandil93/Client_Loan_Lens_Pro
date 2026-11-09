"""Form options, dependent fields and validation limits for New Application."""

GENDERS = {"Female": "F", "Male": "M"}
FAMILY_STATUS = ["Married", "Single / not married", "Civil marriage", "Separated", "Widow"]
MARRIED = {"Married", "Civil marriage"}
EDUCATION = ["Lower secondary", "Secondary / secondary special", "Incomplete higher",
             "Higher education", "Academic degree"]
INCOME_TYPES = ["Working", "Commercial associate", "State servant", "Pensioner", "Businessman",
                "Student", "Maternity leave", "Unemployed"]
NOT_WORKING = {"Pensioner", "Unemployed"}
OCCUPATIONS = ["Laborers", "Sales staff", "Core staff", "Managers", "Drivers", "High skill tech staff",
               "Accountants", "Medicine staff", "Security staff", "Cooking staff", "Cleaning staff",
               "Private service staff", "Low-skill Laborers", "Waiters/barmen staff", "Secretaries",
               "Realty agents", "HR staff", "IT staff", "Other"]
ORGANIZATIONS = ["Business Entity", "Self-employed", "Trade", "Industry", "Medicine", "Government",
                 "Transport", "School", "Kindergarten", "Construction", "Security", "Housing", "Military",
                 "Bank", "Police", "Agriculture", "Postal", "Security Ministries", "Restaurant", "Services",
                 "University", "Electricity", "Hotel", "Insurance", "Telecom", "Emergency", "Advertising",
                 "Realtor", "Culture", "Mobile", "Legal Services", "Cleaning", "Religion", "Other"]
HOUSING = ["House / apartment", "With parents", "Municipal apartment", "Rented apartment",
           "Office apartment", "Co-op apartment"]
CONTRACT_TYPES = ["Cash loans", "Consumer loans", "Revolving loans"]
CLIENT_TYPES = ["New", "Refreshed", "Repeater"]
TERMS = [4, 6, 8, 10, 12, 18, 24, 30, 36, 48, 60]
MAIN_DOCS = [3, 5, 6, 8]
OTHER_DOCS = [d for d in range(2, 22) if d not in MAIN_DOCS]

# Model's training range (beyond it the result is less reliable → warning, not an error)
WARN = {"age": 68, "children": 4, "income": 900_000, "amount": 2_250_000, "car_age": 30}
LEGAL_AGE, MAX_AGE, MAX_CAR_AGE, MAX_BUREAU = 21, 105, 60, 15


def family_members(status: str, children: int) -> int:
    """Rule found in the data (100% of clients): children + 2 if married, + 1 otherwise."""
    return children + (2 if status in MARRIED else 1)


# Each validator returns None, ("error", message) or ("warning", message)
def v_age(age):
    if age < LEGAL_AGE:
        return "error", f"The client is under the legal age ({LEGAL_AGE})."
    if age > MAX_AGE:
        return "error", f"Enter an age up to {MAX_AGE}."
    if age > WARN["age"]:
        return "warning", "Older than any client the model learned from; the result may be less accurate."


def v_children(children):
    if children > WARN["children"]:
        return "warning", "More children than almost all clients in the data."


def v_income(income):
    if income <= 0:
        return "error", "Enter the client's yearly income."
    if income > WARN["income"]:
        return "warning", "Higher than almost all clients in the data; the result may be less accurate."


def v_months(months, age):
    if months > max(age - 18, 0) * 12:
        return "error", "Employment can't start before age 18. Check the age or the months."


def v_car_age(car_age):
    if car_age > MAX_CAR_AGE:
        return "error", f"Enter a car age up to {MAX_CAR_AGE} years."
    if car_age > WARN["car_age"]:
        return "warning", "Older car than almost all clients in the data."


def v_bureau(req):
    if req > MAX_BUREAU:
        return "error", f"Enter up to {MAX_BUREAU} inquiries."


def v_amount(amount):
    if amount < 10_000:
        return "error", "The minimum loan amount is $10,000."
    if amount > WARN["amount"]:
        return "warning", "Larger than almost all requests in the data; the result may be less accurate."


def v_down(down, amount):
    if amount > 0 and down >= amount:
        return "error", "The down payment must be less than the loan amount."


def v_national_id(nid):
    if nid and (not nid.isdigit() or len(nid) != 14):
        return "error", "The national ID must be 14 digits."


def age_from_dob(dob, today=None):
    """Full years between the date of birth and today."""
    from datetime import date

    today = today or date.today()
    return today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
