#!/usr/bin/env bash
# Python dependency helpers (uv).
#
# Placement: put this file at <app>/scripts/deps.sh, where <app>/ is the **application root** — the
# directory that naturally holds this service's requirements.txt, requirements.lock.txt, and
# runtime.txt. That is often the git repo root, but for monorepos or multi-app repos it may be a
# subfolder (e.g. infrastructure/, src/, papertrail/, app/test-lambda/).
#
# APP_ROOT is always the parent of scripts/ (one level up from this file).
#
# Python version: first non-comment line of runtime.txt (Heroku-style, e.g. python-3.12.0).
# Defaults: requirements.txt -> requirements.lock.txt. Override with REQUIREMENTS_FILE / LOCK_FILE.
#
# Lock resolution (lock / check / upgrade-*) uses --python-platform for Linux x86_64 by default so
# macOS developers and CI agree with production containers. Override: LOCK_PYTHON_PLATFORM=... ;
# opt out (host-only lock): export LOCK_PYTHON_PLATFORM=
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
APP_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

REQUIREMENTS_FILE="${REQUIREMENTS_FILE:-requirements.txt}"
LOCK_FILE="${LOCK_FILE:-requirements.lock.txt}"
UV_COMPILE_EXTRA_ARGS="${UV_COMPILE_EXTRA_ARGS:-}"
# Default Linux amd64 when unset; empty LOCK_PYTHON_PLATFORM disables platform pinning.
LOCK_PYTHON_PLATFORM="${LOCK_PYTHON_PLATFORM-x86_64-manylinux_2_28}"
if [[ -n "${LOCK_PYTHON_PLATFORM}" ]]; then
  UV_COMPILE_EXTRA_ARGS="--python-platform ${LOCK_PYTHON_PLATFORM} ${UV_COMPILE_EXTRA_ARGS}"
fi

python_version_from_runtime() {
  local rt="${APP_ROOT}/runtime.txt"
  if [[ ! -f "${rt}" ]]; then
    echo "error: ${rt} not found (add runtime.txt with e.g. python-3.12.0)" >&2
    exit 1
  fi
  local line
  line="$(grep -vE '^\s*(#|$)' "${rt}" | head -1 | tr -d '[:space:]')"
  if [[ -z "${line}" ]]; then
    echo "error: ${rt} has no version line" >&2
    exit 1
  fi
  line="${line#python-}"
  echo "${line}" | awk -F. '{print $1 "." $2}'
}

PYTHON_VERSION="$(python_version_from_runtime)"

usage() {
  echo "Usage: $0 {lock|check|sync|sync-system|upgrade-safe|upgrade-fresh}" >&2
  echo "  App root: ${APP_ROOT} (parent of scripts/)" >&2
  echo "  Python version: first non-comment line of runtime.txt (e.g. python-3.12.0)" >&2
  echo "  lock             Compile ${REQUIREMENTS_FILE} -> ${LOCK_FILE}" >&2
  echo "  check            Fail if lockfile is stale" >&2
  echo "  sync             uv pip sync into active environment" >&2
  echo "  sync-system      uv pip sync --system (containers)" >&2
  echo "  upgrade-safe     --upgrade with 1 week dependency cooldown" >&2
  echo "  upgrade-fresh    --upgrade without cooldown (security fixes)" >&2
  echo "  Lock platform: ${LOCK_PYTHON_PLATFORM:-'(none)'}" >&2
  exit 1
}

req_path="${APP_ROOT}/${REQUIREMENTS_FILE}"
lock_path="${APP_ROOT}/${LOCK_FILE}"

cd "${APP_ROOT}"

uv_base() {
  uv --directory "${APP_ROOT}" "$@"
}

# shellcheck disable=SC2086
_compile() {
  local out="$1"
  local out_dir tmp
  out_dir="$(dirname "${out}")"
  tmp="$(mktemp "${out_dir}/.lock-compile.XXXXXX")"
  if uv_base pip compile "${req_path}" -o "${tmp}" -p "${PYTHON_VERSION}" --no-header ${UV_COMPILE_EXTRA_ARGS}; then
    mv -f "${tmp}" "${out}"
  else
    rm -f "${tmp}"
    return 1
  fi
}

case "${1:-}" in
  lock)
    _compile "${lock_path}"
    ;;
  check)
    tmp="$(mktemp)"
    _compile "${tmp}"
    if ! diff -q "${lock_path}" "${tmp}" >/dev/null 2>&1; then
      echo "Lockfile out of date: ${LOCK_FILE}" >&2
      echo "Re-run from this app root: ${0} lock" >&2
      diff -u "${lock_path}" "${tmp}" || true
      rm -f "${tmp}"
      exit 1
    fi
    rm -f "${tmp}"
    ;;
  sync)
    uv_base pip sync "${lock_path}" -p "${PYTHON_VERSION}"
    ;;
  sync-system)
    uv_base pip sync "${lock_path}" -p "${PYTHON_VERSION}" --system --break-system-packages
    ;;
  upgrade-safe)
    # shellcheck disable=SC2086
    uv_base pip compile "${req_path}" -o "${lock_path}" -p "${PYTHON_VERSION}" --no-header \
      --upgrade --exclude-newer "1 week" ${UV_COMPILE_EXTRA_ARGS}
    ;;
  upgrade-fresh)
    # shellcheck disable=SC2086
    uv_base pip compile "${req_path}" -o "${lock_path}" -p "${PYTHON_VERSION}" --no-header \
      --upgrade ${UV_COMPILE_EXTRA_ARGS}
    ;;
  *)
    usage
    ;;
esac
