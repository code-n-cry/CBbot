from exceptions import WrongPhoneLength, PhoneNotRussian, SomeTextInThePhone


def checking_phone(phone: str):
    """Проверяем номер телефона на валидность"""
    if not phone.startswith('+7'):
        raise PhoneNotRussian
    if len(phone) != 12:
        raise WrongPhoneLength
    if not phone[1:].isdigit():
        raise SomeTextInThePhone
    return True
