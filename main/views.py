@login_required
def readings(request):
    user = request.user
    current_month = datetime.now().strftime('%m.%Y')
    existing_readings = MeterReading.objects.filter(user=user, month=current_month)
    
    if request.method == 'POST':
        form = MeterReadingForm(request.POST, user=user)
        if form.is_valid():
            reading = form.save(commit=False)
            reading.user = user
            reading.month = current_month
            reading.save()
            
            # ========== АВТОМАТИЧЕСКИЙ РАСЧЕТ ПЛАТЕЖА ==========
            # Рассчитываем сумму: показание × тариф услуги
            amount = reading.value * float(reading.service.price)
            
            # Создаем платеж за текущий месяц
            payment, created = Payment.objects.get_or_create(
                user=user,
                month=current_month,
                defaults={
                    'amount': amount,
                    'is_paid': False,
                    'paid_at': None
                }
            )
            
            # Если платеж уже был, обновляем сумму
            if not created and payment.amount != amount:
                payment.amount = amount
                payment.save()
            
            # Отправляем уведомление жильцу
            create_notification(
                user,
                f'💰 Начислено за {current_month}: {amount:.2f} руб. за {reading.service.name}',
                '/payments/'
            )
            # ========== КОНЕЦ АВТОРАСЧЕТА ==========
            
            messages.success(request, f'Показания переданы! Начислено {amount:.2f} руб. за {reading.service.name}')
            return redirect('readings')
    else:
        form = MeterReadingForm(user=user)
    
    readings_history = MeterReading.objects.filter(user=user).order_by('-date_submitted')[:20]
    
    context = {
        'form': form,
        'existing_readings': existing_readings,
        'readings_history': readings_history,
        'current_month': current_month,
    }
    return render(request, 'main/readings.html', context)
