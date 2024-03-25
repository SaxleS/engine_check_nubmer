from flask import Flask, request, jsonify
import phonenumbers
from phonenumbers import geocoder, carrier, PhoneNumberType
import re
from concurrent.futures import ThreadPoolExecutor
NumVerify = Flask("NumVerify")


def check_number(data):
    phone_number, country_guess = data
    phone_number_copy= phone_number
    phone_number = re.sub( "[^\d]", "", phone_number)
    try:
        if not phone_number.startswith("00") and not phone_number.startswith("+") and country_guess:
            phone_number_full = phonenumbers.parse(phone_number, country_guess)
        else:
            phone_number_full = phonenumbers.parse(phone_number, None)

        if phonenumbers.is_valid_number(phone_number_full):
            phone_number_formatted = phonenumbers.format_number(phone_number_full, phonenumbers.PhoneNumberFormat.INTERNATIONAL)
            country = geocoder.description_for_number(phone_number_full, 'en')
            operator = carrier.name_for_number(phone_number_full, 'en')
            number_type = phonenumbers.number_type(phone_number_full)

            type_code = "M" if number_type == PhoneNumberType.MOBILE else "L"

            return {"valid": True, "country": country, "operator": operator, "phone": phone_number_formatted, "type_code": type_code}
        else:
            return {"phone": phone_number, "valid": False}
    except Exception as e:
        return {"phone": phone_number_copy,"type_code": "X", "valid": False,}

def process_numbers(numbers_with_countries):
    with ThreadPoolExecutor(max_workers=10) as executor:
        results = list(executor.map(check_number, numbers_with_countries))
    return results


@NumVerify.route('/check_numbers_NumVerify', methods=['POST'])
def check_numbers():
    if request.is_json:
        data = request.get_json()
        print("Input: ",data)
        numbers_with_countries = [(item[0], item[1]) for item in data]
        results = process_numbers(numbers_with_countries)
        print("Output: ", results)
        return jsonify(results)
    else:
        print("Error: 400")
        return jsonify({"error": "Request must be JSON"}), 400

if __name__ == '__main__':
    NumVerify.run(host='0.0.0.0', port=8070, debug=True)
    # NumVerify.run(debug=True)
