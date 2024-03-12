from flask import Flask, request, jsonify
import phonenumbers
from phonenumbers import geocoder, carrier
import re
from multiprocessing import Pool

NumVerify = Flask(__name__)

def check_number(data):
    phone_number, country_guess = data
    phone_number = re.sub("[^\d]", "", phone_number)

    try:
        if not phone_number.startswith("00") and not phone_number.startswith("+") and country_guess:
            phone_number_full = phonenumbers.parse(phone_number, country_guess)
            if phonenumbers.is_valid_number(phone_number_full):
                # Форматируем номер в международном формате E164
                phone_number_formatted = phonenumbers.format_number(phone_number_full, phonenumbers.PhoneNumberFormat.E164)
            else:
                return {"phone": f"{phone_number}", "valid": False}
        else:
            # Если номер уже содержит код страны, используем его как есть
            phone_number_full = phonenumbers.parse(phone_number, None)
            phone_number_formatted = phonenumbers.format_number(phone_number_full, phonenumbers.PhoneNumberFormat.E164)

        valid = phonenumbers.is_valid_number(phone_number_full)
        country = geocoder.description_for_number(phone_number_full, 'en')
        operator = carrier.name_for_number(phone_number_full, 'en')

        # Возвращаем отформатированный номер в ответе
        return {"valid": valid, "country": country, "operator": operator, "phone": phone_number_formatted}
    except Exception as e:
        return {"phone": f"{phone_number}", "valid": False, "error": str(e)}

def process_numbers(numbers_with_countries):
    with Pool(processes=10) as pool:
        results = pool.map(check_number, numbers_with_countries)
        pool.close()
        pool.join()
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
