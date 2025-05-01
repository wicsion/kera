from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Payment
import requests  # Для API платежных систем


@login_required
def process_payment(request):
    if request.method == 'POST':
        amount = request.POST.get('amount')
        payment = Payment.objects.create(
            user=request.user,
            amount=amount,
            status='pending'
        )

        # Пример для ЮKassa (Яндекс.Касса)
        response = requests.post(
            'https://api.yookassa.ru/v3/payments',
            auth=('shop_id', 'secret_key'),
            json={
                "amount": {"value": amount, "currency": "RUB"},
                "confirmation": {"type": "redirect", "return_url": "http://your-site.com/payments/callback/"},
                "description": f"Payment #{payment.id}"
            }
        )

        if response.status_code == 200:
            payment.transaction_id = response.json()['id']
            payment.save()
            return redirect(response.json()['confirmation']['confirmation_url'])

    return render(request, 'payments/process.html')


def payment_callback(request):
    payment_id = request.GET.get('payment_id')
    payment = Payment.objects.get(transaction_id=payment_id)

    # Проверяем статус в платежной системе
    response = requests.get(
        f'https://api.yookassa.ru/v3/payments/{payment_id}',
        auth=('shop_id', 'secret_key')
    )

    if response.json()['status'] == 'succeeded':
        payment.status = 'completed'
        payment.save()
        # Дополнительная логика (начисление услуг и т.д.)

    return render(request, 'payments/callback.html')


class CreatePaymentView(LoginRequiredMixin, View):
    def post(self, request):
        contact_request = get_object_or_404(ContactRequest, pk=request.POST.get('request_id'))

        # Имитация платежа
        payment = Payment.objects.create(
            user=request.user,
            amount=contact_request.payment_amount,
            status='success'
        )

        contact_request.status = 'paid'
        contact_request.transaction_id = payment.id
        contact_request.save()

        return redirect('contact-details', pk=contact_request.pk)