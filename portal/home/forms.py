from django.contrib.auth import get_user_model, authenticate
from django.core.exceptions import ValidationError
from django.forms import HiddenInput, CharField, ModelForm, PasswordInput, Form, TextInput
from mezzanine.accounts import get_profile_model
from mezzanine.accounts.forms import ProfileForm as ProfileFormMezzanine
from django.utils.translation import ugettext as _
from mezzanine.core.forms import Html5Mixin
import re
from ecommerce.website.utils import limpa_cnpj

User = get_user_model()
Profile = get_profile_model()

cnpj_pattern = re.compile(r'\d{2}(\.\d{3}){2}/\d{4}-\d{2}')


class LoginForm(Html5Mixin, Form):
    """
    Fields for login.
    """
    username = CharField(label='CNPJ', widget=TextInput(attrs={'class': 'mask-cnpj'}))
    password = CharField(label=_("Password"), widget=PasswordInput(render_value=False))

    def clean(self):
        """
        Authenticate the given username/email and password. If the fields
        are valid, store the authenticated user for returning via save().
        """
        username = self.cleaned_data.get("username")

        if not username:
            return username

        if re.match(cnpj_pattern, username):
            username = limpa_cnpj(username)
        password = self.cleaned_data.get("password")
        self._user = authenticate(username=username, password=password)
        if self._user is None:
            raise ValidationError(_("Invalid username/email and password"))
        elif not self._user.is_active:
            raise ValidationError(_("Your account is inactive"))
        return self.cleaned_data

    def save(self):
        """
        Just return the authenticated user - used for logging in.
        """
        return getattr(self, "_user", None)


if Profile is not None:
    class ProfileFieldsForm(ModelForm):
        class Meta:
            model = Profile
            fields = ('cliente_cidade', 'cliente_uf')


class ProfileForm(ProfileFormMezzanine):
    cliente_cidade = CharField(widget=HiddenInput)

    def __init__(self, *args, **kwargs):
        super(ProfileFormMezzanine, self).__init__(*args, **kwargs)
        self._signup = self.instance.id is None
        user_fields = User._meta.get_all_field_names()
        try:
            self.fields["username"].help_text = _(
                "Only letters, numbers, dashes or underscores please")
        except KeyError:
            pass
        for field in self.fields:
            # Make user fields required.
            if field in user_fields:
                self.fields[field].required = True
                # Disable auto-complete for password fields.
            # Password isn't required for profile update.
            if field.startswith("password"):
                self.fields[field].widget.attrs["autocomplete"] = "off"
                self.fields[field].widget.attrs.pop("required", "")
                if not self._signup:
                    self.fields[field].required = False
                    if field == "password1":
                        self.fields[field].help_text = _(
                            "Leave blank unless you want to change your password")
            # Add any profile fields to the form.
        self._has_profile = Profile is not None
        if self._has_profile:
            profile_fields = ProfileFieldsForm().fields
            self.fields.update(profile_fields)
            if not self._signup:
                for field in profile_fields:
                    value = getattr(self.instance.get_profile(), field)
                    self.initial[field] = value