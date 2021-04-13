import royalnet.royaltyping as t
import pydantic as p


class AuthModel(p.BaseModel):
    secret: p.types.SecretStr
