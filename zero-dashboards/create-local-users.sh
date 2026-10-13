#!/bin/sh
set -u

USERS_DIR="${LOCAL_USERS_DIR:-/etc/grafana-local-users}"
BASE_URL="http://127.0.0.1:${GF_SERVER_HTTP_PORT:-3000}"
WAIT_SECONDS="${LOCAL_USERS_WAIT_SECONDS:-300}"

log() { echo "local-users: $*" >&2; }

json_escape() { printf '%s' "$1" | sed -e 's/\\/\\\\/g' -e 's/"/\\"/g'; }

wait_for_grafana() {
  waited=0
  until curl -fsS -o /dev/null "$BASE_URL/api/health" 2>/dev/null; do
    waited=$((waited + 1))
    if [ "$waited" -ge "$WAIT_SECONDS" ]; then
      return 1
    fi
    sleep 1
  done
}

api() {
  method="$1"
  path="$2"
  shift 2
  curl -sS -o /dev/null -w '%{http_code}' -K "$WORK/auth" -X "$method" "$@" "$BASE_URL$path"
}

create_user() {
  login="$1"
  password="$2"
  status="$(api GET "/api/users/lookup?loginOrEmail=$login")"
  case "$status" in
    200) log "user '$login' already exists"; return 0 ;;
    404) ;;
    *) log "lookup of '$login' failed with HTTP $status"; return 1 ;;
  esac
  printf '{"name":"%s","login":"%s","password":"%s"}' \
    "$(json_escape "$login")" "$(json_escape "$login")" "$(json_escape "$password")" > "$WORK/body"
  status="$(api POST /api/admin/users -H 'Content-Type: application/json' --data-binary "@$WORK/body")"
  case "$status" in
    200) log "created user '$login'" ;;
    *) log "creating '$login' failed with HTTP $status"; return 1 ;;
  esac
}

main() {
  [ -d "$USERS_DIR" ] || { log "no $USERS_DIR, skipping"; return 0; }
  admin_user="${GF_SECURITY_ADMIN_USER:-}"
  admin_password="${GF_SECURITY_ADMIN_PASSWORD:-}"
  if [ -z "$admin_user" ] || [ -z "$admin_password" ]; then
    log "GF_SECURITY_ADMIN_USER/GF_SECURITY_ADMIN_PASSWORD not set, skipping"
    return 0
  fi

  umask 077
  WORK="$(mktemp -d)"
  trap 'rm -rf "$WORK"' EXIT
  printf 'user = "%s:%s"\n' "$(json_escape "$admin_user")" "$(json_escape "$admin_password")" > "$WORK/auth"

  wait_for_grafana || { log "grafana not healthy after ${WAIT_SECONDS}s, giving up"; return 1; }

  newline="$(printf '\n_')"
  newline="${newline%_}"
  for file in "$USERS_DIR"/* "$USERS_DIR"/.[!.]*; do
    [ -f "$file" ] || continue
    name="$(basename "$file")"
    password="$(cat "$file")"
    [ -n "$password" ] || { log "empty password for '$name', skipping"; continue; }
    case "$password" in
      *"$newline"*) log "password for '$name' contains a newline, skipping"; continue ;;
    esac
    if printf '%s' "$password" | LC_ALL=C grep -q '[[:cntrl:]]'; then
      log "password for '$name' contains control characters, skipping"
      continue
    fi
    create_user "$name" "$password" || true
  done
}

main
