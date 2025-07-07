import re
from django.core.exceptions import ValidationError
from django.db import models
from utils.model_utils import ModelMixin


# Create your models here.

def validate_numero(value):
    """
    Valide les numéros au format :
    - +243 suivi de 9 chiffres commençant par 84, 85 ou 89
    - ou local 9 chiffres débutant par 84, 85 ou 89
    """
    pattern = r'^(\+243(84|85|89)\d{7}|(84|85|89)\d{7})$'
    if not re.match(pattern, value):
        raise ValidationError(
            "Numéro invalide. Le numéro doit commencer par +24384, +24385, +24389 ou localement 84, 85, 89 suivi de 7 chiffres."
        )
    
class SMS(ModelMixin):
    contenu = models.TextField(max_length=480)

    def __str__(self):
        return self.contenu[:50] + ("..." if len(self.contenu) > 50 else "")

class Client(ModelMixin):
    numero = models.CharField(max_length=20, unique=True, validators=[validate_numero])

    def __str__(self):
        return self.numero
    
class SMSDelivery(models.Model):
    STATUT_CHOICES = [
        ('EN ATTENTE', 'En attente'),
        ('ENVOYÉ', 'Envoyé'),
        ('ERREUR', 'Erreur'),
        ('DELIVRÉ', 'Délivré'),
    ]
    sms = models.ForeignKey(SMS, on_delete=models.CASCADE, related_name='deliveries')
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='sms_deliveries')
    
    # Champ pour stocker l'ID message SMPP (pour faire le lien avec les DLR)
    message_id = models.CharField(max_length=100, blank=True, null=True)

    # Statut de livraison (ex: ENVOYÉ, DELIVRÉ, ÉCHEC, EN ATTENTE, etc.)
    statut = models.CharField(max_length=50,choices=STATUT_CHOICES, default='EN ATTENTE')

    # Code d’erreur retourné par SMPP (ex: '000' pour succès)
    erreur = models.CharField(max_length=10, blank=True, null=True)

    # Date d’envoi effective (lorsque le SMS est envoyé)
    date_envoi = models.DateTimeField(blank=True, null=True)

    # Date de réception du DLR (delivery report)
    date_dlr = models.DateTimeField(blank=True, null=True)

    # Optionnel : nombre de tentatives d’envoi
    tentatives = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"SMSDelivery to {self.client.numero} - statut {self.statut}"
