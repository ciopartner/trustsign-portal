from django.forms import CharField, ModelForm
from oscar.apps.payment.forms import BankcardNumberField, BankcardCCVField, BankcardExpiryMonthField
from oscar.core.loading import get_class

Bankcard = get_class('payment.models', 'Bankcard')


class BankcardForm(ModelForm):
    name = CharField(label='Titular')
    number = BankcardNumberField()
    ccv = BankcardCCVField()
    expiry_month = BankcardExpiryMonthField()

    class Meta:
        model = Bankcard
        fields = ('name', 'number', 'expiry_month', 'ccv')

    def save(self, *args, **kwargs):
        # It doesn't really make sense to save directly from the form as saving
        # will obfuscate some of the card details which you normally need to
        # pass to a payment gateway.  Better to use the bankcard property below
        # to get the cleaned up data, then once you've used the sensitive
        # details, you can save.
        raise RuntimeError("Don't save bankcards directly from form")

    @property
    def bankcard(self):
        """
        Return an instance of the Bankcard model (unsaved)
        """
        return Bankcard(number=self.cleaned_data['number'],
                        expiry_date=self.cleaned_data['expiry_month'],
                        name=self.cleaned_data['name'],
                        ccv=self.cleaned_data['ccv'])