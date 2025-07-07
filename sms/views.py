import logging
from pyexpat.errors import messages
from time import timezone
import time
from venv import logger
from django.http import Http404, HttpResponse
from django.shortcuts import redirect, render
from django.contrib import messages
from sms.models import SMS, Client, SMSDelivery
from utils.forms import SmsSendForm
from utils.smpp_client.smpp_client import SmppClient, is_valid_phone
import io
import pandas as pd
from django.shortcuts import render, redirect


# Create your views here.

# def send_sms_safely(destinations, message):
#     smpp_client = SmppClient()
#     try:
#         smpp_client.send_sms(destinations, message)
#     finally:
#         smpp_client.disconnect()
        
def home(request):
    """
    Render the home page for the SMS application.
    """
    return render(request, 'sms/home.html')

from django.shortcuts import render

def home(request):
    return render(request, 'sms/home.html')

def send_sms(request):
    return render(request, 'sms/send_sms.html',{'form': SmsSendForm()})

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

                # ===== Fichier reçu via le formulaire =====
                if fichier:
                    ext = fichier.name.lower().split('.')[-1]

                    if ext in ['csv', 'txt']:
                        file_data = fichier.read().decode('utf-8-sig')
                        reader = csv.reader(io.StringIO(file_data))
                        for row in reader:
                            if not row:
                                continue
                            raw_number = row[0]
                            number = raw_number.split(':')[0].strip()
                            normalized = is_valid_phone(number)
                            if normalized:
                                cleaned_numbers.add(normalized)
                            else:
                                logger.warning(f"Numéro invalide ignoré : {number}")

                    elif ext in ['xls', 'xlsx']:
                        df = pd.read_excel(fichier)
                        for val in df.iloc[:, 0]:
                            number = str(val).split(':')[0].strip()
                            normalized = is_valid_phone(number)
                            if normalized:
                                cleaned_numbers.add(normalized)
                            else:
                                logger.warning(f"Numéro invalide ignoré : {number}")
                    else:
                        messages.error(request, "Format de fichier non pris en charge.")
                        return redirect('send_sms')

                # ===== Ou numéro unique =====
                elif numero_raw:
                    numero = is_valid_phone(numero_raw)
                    if numero:
                        cleaned_numbers.add(numero)
                    else:
                        form.add_error('numero', "Le numéro saisi n'est pas valide.")
                        return render(request, 'send_sms.html', {'form': form})

                else:
                    form.add_error(None, "Veuillez saisir un numéro ou importer un fichier.")
                    return render(request, 'send_sms.html', {'form': form})

                # ===== Envoi =====
                if cleaned_numbers:
                    logging.info(f"[START BULK] Envoi de {len(cleaned_numbers)} SMS avec TPS={TPS}/sec")

                    for idx, numero in enumerate(cleaned_numbers, 1):
                        try:
                            # DB
                            client_obj, _ = Client.objects.get_or_create(numero=numero)
                            sms_obj, _ = SMS.objects.get_or_create(contenu=message_text)
                            delivery = SMSDelivery.objects.create(
                                sms=sms_obj,
                                client=client_obj,
                                statut='EN ATTENTE',
                                date_envoi=None,
                                date_dlr=None,
                                tentatives=0
                            )

                            smpp_client.send_sms(numero, message_text)

                            delivery.statut = 'ENVOYÉ'
                            delivery.date_envoi = timezone.now()
                            delivery.message_id = f"sim-{delivery.id}"
                            delivery.save()
                            logger.info(f"[SENT {idx}/{len(cleaned_numbers)}] ➤ {numero}")
                        except Exception as e:
                            logger.error(f"[ERROR] Échec d’envoi vers {numero} : {e}")
                            delivery.statut = 'ERREUR'
                            delivery.erreur = str(e)[:255]
                            delivery.save()

                        time.sleep(delay)

                    messages.success(request, f"{len(cleaned_numbers)} SMS envoyés avec succès.")
                    return redirect('send_sms')

                else:
                    messages.warning(request, "Aucun numéro valide trouvé.")
                    return redirect('send_sms')

            except Exception as e:
                logger.exception(f"[GLOBAL ERROR] {e}")
                messages.error(request, "Une erreur est survenue lors de l’envoi.")
            finally:
                smpp_client.disconnect()

    else:
        form = SmsSendForm()

    return render(request, 'send_sms.html', {'form': form})