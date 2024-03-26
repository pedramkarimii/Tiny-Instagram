from kavenegar import *

"""
Defines a function to send OTP code via Kavenegar API.
Uses the provided phone number and code to compose the message.
Handles exceptions for API and HTTP errors.
"""


def send_otp_code(phone_number, code):
    try:
        api = KavenegarAPI('2B4C4A2F65544177616E2F6F675956505A4B59542F71796A4849347267642F7A6E69574753564679685A513D')
        params = {
            'sender': '1000689696',
            'receptor': phone_number,
            'message': f"کد تایید شما "
                       f"{code}"
        }

        response = api.sms_send(params)
        print(response)
    except APIException as e:
        print(f'Error API: The identification code is not valid <<{KavenegarAPI}>> - {e}')
    except HTTPException as e:
        print(f'Error HTTP: {e}')
