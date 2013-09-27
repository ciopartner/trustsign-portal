from django.contrib.auth import get_user_model
from django.forms import HiddenInput, CharField, ModelForm
from mezzanine.accounts import get_profile_model
from mezzanine.accounts.forms import ProfileForm as ProfileFormMezzanine
from django.utils.translation import ugettext as _

User = get_user_model()
Profile = get_profile_model()


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