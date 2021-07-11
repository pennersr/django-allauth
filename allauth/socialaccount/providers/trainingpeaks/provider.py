from allauth.socialaccount.providers.base import ProviderAccount
from allauth.socialaccount.providers.oauth2.provider import OAuth2Provider


class TrainingPeaksAccount(ProviderAccount):
    def get_profile_url(self):
        return "https://app.trainingpeaks.com"

    def get_avatar_url(self):
        return None

    def to_str(self):
        name = (
            self.account.extra_data.get("FirstName")
            + " "
            + self.account.extra_data.get("LastName")
        )
        if name != " ":
            return name
        return super(TrainingPeaksAccount, self).to_str()


class TrainingPeaksProvider(OAuth2Provider):
    id = "trainingpeaks"
    name = "TrainingPeaks"
    account_class = TrainingPeaksAccount

    def extract_uid(self, data):
        return data.get("Id")

    def extract_common_fields(self, data):
        extra_common = super(TrainingPeaksProvider, self).extract_common_fields(data)
        firstname = data.get("FirstName")
        lastname = data.get("LastName")
        # fallback username as there is actually no Username in response
        username = firstname.strip().lower() + "." + lastname.strip().lower()
        name = " ".join(part for part in (firstname, lastname) if part)
        extra_common.update(
            username=data.get("username", username),
            email=data.get("Email"),
            first_name=firstname,
            last_name=lastname,
            name=name.strip(),
        )
        return extra_common

    def get_default_scope(self):
        return ["athlete:profile"]


provider_classes = [TrainingPeaksProvider]
