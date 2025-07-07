import logging
import csv
import io
import time
import pandas as pd

from django.http import JsonResponse
from django.shortcuts import render
from django.utils import timezone
from sms.models import SMS, Client, SMSDelivery
from utils.forms import SmsSendForm
from utils.smpp_client.smpp_client import SmppClient, is_valid_phone


def home(request):
    return render(request, 'sms/home.html')


def send_sms(request):
    return render(request, 'sms/send_sms.html', {'form': SmsSendForm()})


def history(request):
    return render(request, 'sms/history.html')


def contact(request):
    return render(request, 'sms/contact.html')


def settings(request):
    return render(request, 'sms/settings.html')


def send_sms_view(request):
    if request.method == 'POST':
        form = SmsSendForm(request.POST, request.FILES)

        if form.is_valid():
            message_text = form.cleaned_data['message']
            fichier = form.cleaned_data.get('fichier')
            numero_raw = form.cleaned_data.get('numero')

            cleaned_numbers = set()
            TPS = 30
            delay = 1.0 / TPS

            try:
                smpp_client = SmppClient()

                # Traitement fichier
                if fichier:
                    ext = fichier.name.lower().split('.')[-1]
                    if ext in ['csv', 'txt']:
                        file_data = fichier.read().decode('utf-8-sig')
                        reader = csv.reader(io.StringIO(file_data))
                        for row in reader:
                            if not row:
                                continue
                            number = row[0].split(':')[0].strip()
                            normalized = is_valid_phone(number)
                            if normalized:
                                cleaned_numbers.add(normalized)
                    elif ext in ['xls', 'xlsx']:
                        df = pd.read_excel(fichier)
                        for val in df.iloc[:, 0]:
                            number = str(val).split(':')[0].strip()
                            normalized = is_valid_phone(number)
                            if normalized:
                                cleaned_numbers.add(normalized)
                    else:
                        return JsonResponse({'success': False, 'error': "Format de fichier non pris en charge."})

                # Traitement numéro direct
                elif numero_raw:
                    numero = is_valid_phone(numero_raw)
                    if numero:
                        cleaned_numbers.add(numero)
                    else:
                        return JsonResponse({'success': False, 'error': "Numéro invalide."})

                else:
                    return JsonResponse({'success': False, 'error': "Veuillez fournir un numéro ou un fichier."})

                # Envoi SMS
                if cleaned_numbers:
                    for idx, numero in enumerate(cleaned_numbers, 1):
                        try:
                            client_obj, _ = Client.objects.get_or_create(numero=numero)
                            sms_obj, _ = SMS.objects.get_or_create(contenu=message_text)
                            delivery = SMSDelivery.objects.create(
                                sms=sms_obj,
                                client=client_obj,
                                statut='EN ATTENTE'
                            )

                            smpp_client.send_sms(numero, message_text)

                            delivery.statut = 'ENVOYÉ'
                            delivery.date_envoi = timezone.now()
                            delivery.message_id = f"sim-{delivery.id}"
                            delivery.save()
                        except Exception as e:
                            delivery.statut = 'ERREUR'
                            delivery.erreur = str(e)[:255]
                            delivery.save()

                        time.sleep(delay)

                    return JsonResponse({
                        'success': True,
                        'message': f"{len(cleaned_numbers)} SMS envoyés avec succès."
                    })
                else:
                    return JsonResponse({'success': False, 'error': "Aucun numéro valide trouvé."})

            except Exception as e:
                logging.exception("Erreur lors de l'envoi SMS")
                return JsonResponse({'success': False, 'error': str(e)})

            finally:
                smpp_client.disconnect()

        return JsonResponse({'success': False, 'error': "Formulaire invalide."})

    # GET
    return render(request, 'sms/send_sms.html', {'form': SmsSendForm()})
