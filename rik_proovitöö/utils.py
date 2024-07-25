from datetime import date


def calculate_personal_check_digit(personal_code: int) -> int:
    personal_code = str(personal_code)
    first_tier_weights = [1, 2, 3, 4, 5, 6, 7, 8, 9, 1]
    second_tier_weights = [3, 4, 5, 6, 7, 8, 9, 1, 2, 3]
    first_tier_weight_sum = sum(
        [
            int(x) * first_tier_weights[i]
            for i, x in enumerate(personal_code[:10])
        ]
    )
    possible_check_digit = first_tier_weight_sum % 11
    if possible_check_digit != 10:
        return possible_check_digit
    else:
        second_tier_weight_sum = sum(
            [
                int(x) * second_tier_weights[i]
                for i, x in enumerate(personal_code[:10])
            ]
        )
        possible_check_digit = second_tier_weight_sum % 11
        if possible_check_digit != 10:
            return possible_check_digit
        else:
            return 0


def calculate_birth_year(personal_code: int) -> int:
    personal_code = str(personal_code)
    if personal_code[0] in ["1", "2"]:
        year_digits = "18"
    elif personal_code[0] in ["3", "4"]:
        year_digits = "19"
    else:
        year_digits = "20"

    return int(f"{year_digits}{personal_code[1:3]}")


def convert_to_birthdate(personal_code: int) -> date:
    birth_year = calculate_birth_year(personal_code)
    personal_code = str(personal_code)
    birth_month = int(personal_code[3:5])
    birth_day = int(personal_code[5:7])

    return date(year=birth_year, month=birth_month, day=birth_day)
