import hashlib
import secrets
from datetime import time, timedelta

from django.utils import timezone
from django.db import transaction
from django.conf import settings
from .models import MartyCoinWallet, MartyCoinTransaction, PhoneOTP, Profile


def generate_otp():
    return f"{secrets.randbelow(1000000):06d}"

def hash_otp(otp):
    return hashlib.sha256(otp.encode()).hexdigest()

def create_phone_otp(phone):

    now = timezone.now()

    existing_otp = PhoneOTP.objects.filter(
        phone=phone,
        verified_at__isnull=True
    ).order_by("-created_at").first()

    if existing_otp:
        cooldown = (now - existing_otp.last_sent_at).total_seconds()

        if cooldown < 60:

            raise ValueError(
                "Please wait before requesting a another OTP."
            )

    otp = generate_otp()

    PhoneOTP.objects.create(
        phone=phone,
        otp_hash=hash_otp(otp),
        expires_at=now + timedelta(minutes=5)
    )

    return otp

def verify_phone_otp(phone, otp):

    otp_record = (
        PhoneOTP.objects.filter(
            phone=phone,
            verified_at__isnull=True
        )
        .order_by("-created_at")
        .first()
    )

    if not otp_record:
        return False, "OTP not found."

    if timezone.now() > otp_record.expires_at:
        return False, "OTP has expired."

    if otp_record.attempts >= 5:
        return False, "Too many failed attempts."

    otp_record.attempts += 1
    otp_record.save(
        update_fields=["attempts"]

    )

    if not secrets.compare_digest(
        otp_record.otp_hash,
        hash_otp(otp)
    ): 
        return False, "Invalid OTP."

    otp_record.verified_at = timezone.now()
    otp_record.save(update_fields=["verified_at"])

    profile = Profile.objects.filter(phone=phone).first()

    if not profile:
        return False, "NO Account found."

    profile.phone_verified = True
    profile.save(update_fields=["phone_verified"])
    return True, "OTP verified successfully."


@transaction.atomic
def add_martycoins(
    user,
    amount,
    description,
    reference=None,
):
    if amount <= 0:
        raise ValueError("Amount must be greater than 0.")

    wallet, _ = MartyCoinWallet.objects.select_for_update().get_or_create(user=user)

    wallet.balance += amount
    wallet.save(update_fields=["balance", "updated_at"])

    MartyCoinTransaction.objects.create(
        wallet=wallet,
        transaction_type="earned",
        amount=amount,
        description=description,
        reference=reference
    )

    return wallet

@transaction.atomic
def spend_martycoin(
    user,
    amount,
    description,
    reference=None
):
    if amount <= 0:
        raise ValueError("Amount must be greater than 0.")

    wallet = MartyCoinWallet.objects.select_for_update().get(user=user)

    if wallet.balance < amount:
        raise ValueError("Insufficient balance.")

    wallet.balance -= amount
    wallet.save(update_fields=["balance", "updated_at"])

    MartyCoinTransaction.objects.create(
        wallet=wallet,
        transaction_type="spent",
        amount=amount,
        description=description,
        reference=reference
    )

    return wallet

@transaction.atomic
def process_referral_reward(new_user, referrer_user):

    reward = settings.REFERRAL_REWARD_COINS

    referral_reference = (
        f"REFERRAL_{new_user.id}_{referrer_user.id}"
    )

    #dublicate protection
    if MartyCoinTransaction.objects.filter(
        reference=referral_reference,
        reference_type="referral"
    ).exists():
        return False

    referrer_wallet, _ = (
        MartyCoinWallet.objects
        .select_for_update()
        .get_or_create(user=referrer_user)
    )

    new_user_wallet, _ = (
        MartyCoinWallet.objects
        .select_for_update()
        .get_or_create(user=new_user)
    )

    #jo referrer ko milega
    referrer_wallet.balance += reward
    referrer_wallet.save(
        update_fields=["balance", "updated_at"]
    )

    MartyCoinTransaction.objects.create(
        wallet=referrer_wallet,
        transaction_type="earned",
        amount=reward,
        description="Referral Reward",
        reference=referral_reference,
        reference_type="referral"
    )

    # naye user ko milega
    new_user_wallet.balance += reward
    new_user_wallet.save(
        update_fields=["balance", "updated_at"]
    )

    MartyCoinTransaction.objects.create(
        wallet=new_user_wallet,
        transaction_type="earned",
        amount=reward,
        description="Referral signup reward",
        reference=referral_reference,
        reference_type="referral"
    )

    return True
        
