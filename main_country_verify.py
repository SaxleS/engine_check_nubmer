from flask import Flask, request, jsonify
import phonenumbers
from phonenumbers import PhoneNumberFormat, region_code_for_number, parse
import logging

app = Flask("NumCountryVerify")

# This function is now async. In a real async application, it would perform async I/O.
async def check_number_country(phone_number, country_iso):
    if phone_number is None:
        logging.error("Received a None phone_number")
        return False

    if not phone_number.startswith("+"):
        logging.info(f"Skipping number without international code: {phone_number}")
        return False

    try:
        phone_number_parsed = parse(phone_number, None)
        country_code_for_number = region_code_for_number(phone_number_parsed).upper()
        is_correct_country = country_code_for_number == country_iso.upper()
        is_valid_number = phonenumbers.is_valid_number(phone_number_parsed)

        logging.info(f"Parsed number: {phonenumbers.format_number(phone_number_parsed, PhoneNumberFormat.INTERNATIONAL)}")
        logging.info(f"Country code from number: {country_code_for_number}, Expected: {country_iso.upper()}")
        logging.info(f"Is correct country: {is_correct_country}, Is valid number: {is_valid_number}")

        return is_valid_number and is_correct_country
    except phonenumbers.NumberParseException as e:
        logging.error(f"Error parsing number {phone_number}: {e}")
        return False

# This route handler is now async.
@app.route('/check_number_country_verify', methods=['POST'])
async def check_numbers():
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400

    data = request.get_json()
    print(data)
    # Ensure that data contains only two elements: phone number and country ISO code
    if isinstance(data, list) and len(data) == 2:
        phone_number, country_iso = data
        result = await check_number_country(phone_number, country_iso)  # Awaiting the async function if necessary
        print(result)
        return jsonify(country_check=result)
    else:
        return jsonify({"error": "Invalid data format. Expected [phone_number, country_iso]"}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8040, debug=True)
