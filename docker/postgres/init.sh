#!/bin/sh
set -eu

IDENTITY_PASSWORD="$(cat /run/secrets/identity_password)"
BUSINESS_PASSWORD="$(cat /run/secrets/business_password)"

export IDENTITY_PASSWORD
export BUSINESS_PASSWORD

psql \
  --username "$POSTGRES_USER" \
  --dbname "$POSTGRES_DB" \
  --set=ON_ERROR_STOP=1 <<'SQL'

\getenv identity_password IDENTITY_PASSWORD
\getenv business_password BUSINESS_PASSWORD

CREATE ROLE identity_user LOGIN PASSWORD :'identity_password';
CREATE ROLE business_user LOGIN PASSWORD :'business_password';

CREATE DATABASE kora_identity OWNER identity_user;
CREATE DATABASE kora_business OWNER business_user;

REVOKE CONNECT ON DATABASE kora_identity FROM PUBLIC;
REVOKE CONNECT ON DATABASE kora_business FROM PUBLIC;

GRANT CONNECT ON DATABASE kora_identity TO identity_user;
GRANT CONNECT ON DATABASE kora_business TO business_user;

SQL

unset IDENTITY_PASSWORD BUSINESS_PASSWORD
