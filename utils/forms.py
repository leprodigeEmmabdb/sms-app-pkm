from django import forms

class SmsSendForm(forms.Form):
    numero = forms.CharField(
        required=False,
        label="Numéro",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ex: +2438xxxxxxxx ou 8xxxxxxxx'
        })
    )

    fichier = forms.FileField(
        required=False,
        label="Fichier CSV ou Excel",
        help_text="Un fichier .csv ou .xlsx contenant un numéro par ligne.",
        widget=forms.ClearableFileInput(attrs={
            'class': 'form-control'
        })
    )

    message = forms.CharField(
        label="Message",
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 4,
            'placeholder': 'Contenu du message à envoyer'
        })
    )

    def clean(self):
        cleaned_data = super().clean()
        numero = cleaned_data.get("numero")
        fichier = cleaned_data.get("fichier")

        if not numero and not fichier:
            raise forms.ValidationError(
                "Veuillez renseigner un numéro ou importer un fichier CSV ou Excel."
            )

        if fichier:
            ext = fichier.name.split('.')[-1].lower()
            if ext not in ['csv', 'xlsx']:
                raise forms.ValidationError("Le fichier doit être au format .csv ou .xlsx")

        return cleaned_data
