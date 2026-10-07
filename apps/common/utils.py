"""Umumiy yordamchi funksiyalar (barcha ilovalar uchun)."""


def pul(qiymat):
    """Pulni $ va 2 kasr bilan ko'rsatadi: 0.15 -> $0.15, 50000 -> $50,000.00"""
    try:
        return f'${float(qiymat):,.2f}'
    except (TypeError, ValueError):
        return f'${qiymat}'
