import os
import requests

from dotenv import load_dotenv

load_dotenv()


APITXT_OTP_URL = os.getenv(
    "APITXT_OTP_URL",
    "https://apitxt.com/api/sendOTP"
)


def send_otp_sms(phone, otp):
    authkey = os.getenv("APITXT_AUTHKEY")

    if not authkey:
        raise ValueError(
            "APITXT_AUTHKEY is not configured."
        )

    params = {
        "authkey": authkey,
        "mobile": phone,
        "otp": otp,
        "channel": "sms",
        "country": "91",
    }

    response = requests.get(
        APITXT_OTP_URL,
        params=params,
        timeout=15,
    )

    print("APITxT Status:", response.status_code)
    print("APITxT Response:", response.text)

    response.raise_for_status()

    data = response.json()

    if data.get("status") != "success":
        raise ValueError(
            data.get(
                "message",
                "Failed to send OTP."
            )
        )

    return data