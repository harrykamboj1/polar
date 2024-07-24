"""Revamp PersonalAccessToken

Revision ID: 8e40457497a3
Revises: 5a92c17b033d
Create Date: 2024-06-18 09:22:33.706790

"""

import sqlalchemy as sa
from alembic import op

# Polar Custom Imports
from polar.auth.service import AuthService
from polar.config import settings
from polar.kit import jwt
from polar.kit.crypto import get_token_hash

# revision identifiers, used by Alembic.
revision = "8e40457497a3"
down_revision = "5a92c17b033d"
branch_labels: tuple[str] | None = None
depends_on: tuple[str] | None = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "personal_access_tokens",
        sa.Column("token", sa.String(length=255), nullable=True),
    )
    op.add_column(
        "personal_access_tokens", sa.Column("scope", sa.Text(), nullable=True)
    )
    op.create_unique_constraint(
        op.f("personal_access_tokens_token_key"), "personal_access_tokens", ["token"]
    )

    # Select and iterate over all personal access tokens
    # and set the token and scope fields
    connection = op.get_bind()
    result = connection.execute(
        sa.text("SELECT id, comment, expires_at FROM personal_access_tokens")
    )
    for id, comment, expires_at in result:
        if "RSS" in comment:
            scopes = ["articles:read", "organizations:read"]
        else:
            scopes = ["web_default"]

        jwt_token = jwt.encode(
            data={
                "pat_id": str(id),
                "scopes": ",".join(scopes),
            },
            secret=settings.SECRET,
            expires_at=expires_at,
            type="auth",
        )
        hashed_token = get_token_hash(jwt_token, secret=settings.SECRET)
        connection.execute(
            sa.text(
                "UPDATE personal_access_tokens SET token = :token, scope = :scope WHERE id = :id"
            ),
            {"id": id, "token": hashed_token, "scope": " ".join(scopes)},
        )

    op.alter_column(
        "personal_access_tokens",
        "token",
        existing_type=sa.VARCHAR(length=255),
        nullable=False,
        existing_nullable=True,
    )
    op.alter_column(
        "personal_access_tokens",
        "scope",
        existing_type=sa.TEXT(),
        nullable=False,
        existing_nullable=True,
    )

    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(
        op.f("personal_access_tokens_token_key"),
        "personal_access_tokens",
        type_="unique",
    )
    op.drop_column("personal_access_tokens", "scope")
    op.drop_column("personal_access_tokens", "token")
    # ### end Alembic commands ###
