#!/usr/bin/env python3

import os
import logging
import smpplib.client
import smpplib.consts
import smpplib.gsm
import csv
import time
from dotenv import load_dotenv

# Configuration logging
logging.basicConfig(level=logging.INFO)

# Charger les variables d'environnement
load_dotenv()

class SmppClient:
    def __init__(self):
        self.host = os.getenv('SMPP_HOST')
        self.port = int(os.getenv('SMPP_PORT'))
        self.system_id = os.getenv('SMPP_USERNAME')
        self.password = os.getenv('SMPP_PASSWORD')

        self.client = smpplib.client.Client(self.host, self.port)

        # Log quand un message est envoyé avec succès
        self.client.set_message_sent_handler(
            lambda pdu: logging.info(f"[SUBMIT_RESP] seq={pdu.sequence} msgid={pdu.message_id}")
        )

        # Log quand un message est reçu (DLR / MO)
        self.client.set_message_received_handler(self.handle_deliver_sm)

        # Connexion et bind
        self.client.connect()
        self.client.bind_transceiver(system_id=self.system_id, password=self.password)

        logging.info(f"[CONNECTED] Bound to SMPP {self.host}:{self.port} as {self.system_id}")

    def send_sms(self, destinations, message):
        if isinstance(destinations, str):
            destinations = [destinations]

        parts, encoding_flag, msg_type_flag = smpplib.gsm.make_parts(message)

        for dest in destinations:
            for part in parts:
                pdu = self.client.send_message(
                    source_addr_ton=smpplib.consts.SMPP_TON_ALNUM,
                    source_addr_npi=smpplib.consts.SMPP_NPI_UNK,
                    source_addr=os.getenv('app_user', 'PKM-Shop'),

                    dest_addr_ton=smpplib.consts.SMPP_TON_INTL,
                    dest_addr_npi=smpplib.consts.SMPP_NPI_ISDN,
                    destination_addr=dest,

                    short_message=part,
                    data_coding=encoding_flag,
                    esm_class=msg_type_flag,
                    registered_delivery=True
                )
                logging.info(f"[SEND] ➤ Dest={dest} | Seq={pdu.sequence} | Status={pdu.status}")

    def handle_deliver_sm(self, pdu):
        try:
            # Récupérer le champ short_message en toute sécurité
            short_message = pdu.params.get('short_message', b'')
            if isinstance(short_message, bytes):
                dlr_text = short_message.decode('utf-8', errors='ignore')
            else:
                dlr_text = str(short_message)

            logging.info(f"[DLR RECEIVED] {dlr_text}")

            # Initialiser les valeurs extraites
            statut = None
            message_id = None
            erreur = None

            # Exemple de DLR : "id:123456 stat:DELIVRD err:000"
            parts = dlr_text.strip().split()
            for part in parts:
                if part.startswith('stat:'):
                    statut = part[5:]
                elif part.startswith('id:'):
                    message_id = part[3:]
                elif part.startswith('err:'):
                    erreur = part[4:]

            logging.info(f"[DLR PARSED] message_id={message_id}, statut={statut}, erreur={erreur}")

            # Partie base de données ici (si tu veux la réintégrer plus tard)

        except Exception as e:
            logging.exception(f"[DLR ERROR] Erreur lors du traitement du DLR: {e}")

    def listen(self):
        try:
            logging.info("[LISTENING] Waiting for DLRs...")
            self.client.listen()
        except KeyboardInterrupt:
            logging.info("[STOPPED] Interrupted by user.")
        finally:
            self.disconnect()

    def disconnect(self):
        try:
            self.client.unbind()
            self.client.disconnect()
            logging.info("[DISCONNECTED] SMPP session closed.")
        except Exception as e:
            logging.warning(f"[DISCONNECT ERROR] {e}")


def is_valid_phone(number):
    number = number.strip().replace(' ', '').replace('-', '')
    if number.startswith('+'):
        number = number[1:]
    if number.startswith('243') and len(number) == 12:
        return number
    if len(number) == 9 or not number.startswith('0'):
        return '243' + number
    return None


if __name__ == '__main__':
    smpp_client = SmppClient()
    try:
        csv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../../7.csv')
        csv_path = os.path.abspath(csv_path)

        cleaned_numbers = set()

        with open(csv_path, newline='', encoding='utf-8-sig') as f:
            reader = csv.reader(f)
            for row in reader:
                if not row:
                    continue
                raw_number = row[0]
                number = raw_number.split(':')[0].strip()
                normalized = is_valid_phone(number)
                if normalized:
                    cleaned_numbers.add(normalized)
                else:
                    logging.warning(f"Numéro invalide ignoré : {number}")

        if cleaned_numbers:
            TPS = 10  # messages par seconde
            delay_between_msgs = 1.0 / TPS
            # message = "Cherchez-vous un Smartphone, Powerbank,chargeur, ordinateur aux meilleurs prix ? Rdv chez PKM-SHOP. Av. Colonel Mondjiba 04 ,Ref.rond-point magasin kitambo."
            # message="Profitez de 20 % de réduction sur tout le magasin jusqu'à dimanche ! Présentez ce SMS en caisse. PKM-INVEST/SHOP, avenue Colonel Monjiba, 04  ,réf. Rond-point magasin kitambo, voir arrêt taxybus boulevard et zando . Ont tient à vous !"
            message="Besoin de remplacer l’ecran de votre smartphone ou de votre tablette ?  Retrouvez les ecrans des : iPhone, Samsung, Tecno, infinix, itel chez PKM-INVEST/SHOP sis avenue Colonel Mondjiba, 04  , ref. Rond-point magasin kitambo  voir arret taxybus Boulevard et Zando"
            recipients = list(cleaned_numbers)

            logging.info(f"[START BULK] Envoi de {len(recipients)} SMS avec TPS={TPS}/sec")

            for idx, number in enumerate(recipients, 1):
                try:
                    smpp_client.send_sms(number, message)
                    logging.info(f"[SENT {idx}/{len(recipients)}] ➤ {number}")
                except Exception as e:
                    logging.error(f"[ERROR] Échec d’envoi vers {number} : {e}")
                time.sleep(delay_between_msgs)

            smpp_client.listen()
        else:
            logging.warning("Aucun numéro valide trouvé dans le fichier CSV.")
    finally:
        smpp_client.disconnect()
