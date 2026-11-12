from typing import cast

from rest_framework.generics import RetrieveAPIView

from .models import User
from .serializers import UserSerializer


class MeView(RetrieveAPIView[User]):
    serializer_class = UserSerializer

    def get_object(self) -> User:
        return cast(User, self.request.user)
