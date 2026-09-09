#!/usr/bin/env bash
# ==============================================================================
# ats-audit.sh — Deterministic ATS & Resume Quality Auditor (MarkForge Engine)
# ==============================================================================
# Evaluates CV markdown files against ATS parsing heuristics using MarkForge AST:
# - Standard section structure detection (Summary, Experience, Education, Skills, Projects)
# - High-impact power action verbs extraction
# - Quantifiable accomplishment metrics density (#s, %s, currency, multipliers)
# - Word count, readability, formatting warnings, and optimization suggestions
#
# Usage:
#   # Audit single CV
#   scripts/ats-audit.sh path/to/cv-data-analyst-en.md
#
#   # Audit all CVs in candidate run directory with minimum score threshold
#   scripts/ats-audit.sh output/candidates/rafli-arraafi/2026-06-01-data-analyst --min-score 90
#
#   # Output machine-readable JSON for agent consumption (e.g. Agent 09 Delta Verifier)
#   scripts/ats-audit.sh path/to/cv-data-analyst-en.md --json
# ==============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"

# ANSI formatting
BOLD='\033[1m'
CYAN='\033[0;36m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
DIM='\033[0;2m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
NC='\033[0m'

usage() {
  cat <<EOF
${BOLD}Usage:${NC}
  $(basename "$0") <cv-file.md | candidate-directory> [options]

${BOLD}Options:${NC}
  --json               Output audit results as structured JSON
  --min-score <N>      Assert minimum acceptable ATS score (0-100). Exits 1 if failed.
  --en-only            Audit only English CVs (*-en.md)
  --id-only            Audit only Indonesian CVs (*-id.md)
  -q, --quiet          Only print score summary and failures
  -h, --help           Show this help message

${BOLD}Examples:${NC}
  $(basename "$0") output/candidates/rafli-arraafi/2026-06-01-data-analyst/cv/data-analyst/cv-rafli_arraafi-data-analyst-en.md
  $(basename "$0") output/candidates/rafli-arraafi/2026-06-01-data-analyst/cv --min-score 85
  $(basename "$0") output/candidates/rafli-arraafi/2026-06-01-data-analyst --json
EOF
}

# Resolve MarkForge runner
resolve_runner() {
  if [[ -n "${MARKFORGE_BIN:-}" && -x "${MARKFORGE_BIN}" ]]; then
    RUNNER=("${MARKFORGE_BIN}")
    return 0
  fi

  if command -v markforge >/dev/null 2>&1; then
    RUNNER=("markforge")
    return 0
  fi

  local bun_bin=""
  if command -v bun >/dev/null 2>&1; then
    bun_bin="$(command -v bun)"
  elif [[ -x "${HOME}/.bun/bin/bun" ]]; then
    bun_bin="${HOME}/.bun/bin/bun"
  elif [[ -x "/usr/local/bin/bun" ]]; then
    bun_bin="/usr/local/bin/bun"
  elif [[ -x "/usr/bin/bun" ]]; then
    bun_bin="/usr/bin/bun"
  fi

  local mf_dir=""
  if [[ -n "${MARKFORGE_DIR:-}" && -d "${MARKFORGE_DIR}" ]]; then
    mf_dir="${MARKFORGE_DIR}"
  elif [[ -d "/home/archy/Projects/markforge" ]]; then
    mf_dir="/home/archy/Projects/markforge"
  elif [[ -d "${ROOT_DIR}/../markforge" ]]; then
    mf_dir="$(cd "${ROOT_DIR}/../markforge" && pwd)"
  fi

  if [[ -n "${bun_bin}" && -n "${mf_dir}" && -f "${mf_dir}/packages/cli/src/index.ts" ]]; then
    RUNNER=("${bun_bin}" "run" "${mf_dir}/packages/cli/src/index.ts")
    return 0
  fi

  # Fallback to python bridge
  if command -v python3 >/dev/null 2>&1 && [[ -f "${SCRIPT_DIR}/markforge_bridge.py" ]]; then
    RUNNER=("python3" "${SCRIPT_DIR}/markforge_bridge.py" "analyze")
    return 0
  fi

  echo -e "${RED}✖ Error: Neither Bun + MarkForge nor Python bridge could be resolved.${NC}" >&2
  exit 1
}

target=""
json_out=false
min_score=0
quiet=false
en_only=false
id_only=false

if [[ $# -eq 0 ]]; then
  usage
  exit 0
fi

while [[ $# -gt 0 ]]; do
  case "$1" in
    --json)
      json_out=true
      shift
      ;;
    --min-score)
      min_score="${2:-0}"
      shift 2
      ;;
    --en-only)
      en_only=true
      shift
      ;;
    --id-only)
      id_only=true
      shift
      ;;
    -q|--quiet)
      quiet=true
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    -*)
      echo -e "${RED}Unknown option: $1${NC}" >&2
      usage
      exit 2
      ;;
    *)
      if [[ -z "$target" ]]; then
        target="$1"
      else
        echo -e "${RED}Unexpected argument: $1${NC}" >&2
        exit 2
      fi
      shift
      ;;
  esac
done

if [[ -z "$target" || ! -e "$target" ]]; then
  echo -e "${RED}Error: Target does not exist: ${target:-<none>}${NC}" >&2
  exit 1
fi

resolve_runner

# Collect files to audit
files_to_audit=()
if [[ -d "$target" ]]; then
  # Directory mode: find all cv-*.md or resume markdown files
  while IFS= read -r f; do
    files_to_audit+=("$f")
  done < <(/usr/bin/find "$target" -type f \( -name "cv-*.md" -o -name "cv.md" -o -path "*/cv/*.md" \) ! -path "*/scratch/*" ! -path "*/input/*" | sort)

  if [[ ${#files_to_audit[@]} -eq 0 ]]; then
    # Fallback to all md files in folder
    while IFS= read -r f; do
      files_to_audit+=("$f")
    done < <(/usr/bin/find "$target" -maxdepth 2 -type f -name "*.md" ! -path "*/scratch/*" ! -path "*/input/*" | sort)
  fi
else
  files_to_audit=("$target")
fi

# Apply language filters if specified
if [[ "$en_only" == true ]]; then
  filtered=()
  for f in "${files_to_audit[@]}"; do
    if [[ "$f" == *-en.md || "$f" == *-en.* ]]; then
      filtered+=("$f")
    fi
  done
  files_to_audit=("${filtered[@]}")
elif [[ "$id_only" == true ]]; then
  filtered=()
  for f in "${files_to_audit[@]}"; do
    if [[ "$f" == *-id.md || "$f" == *-id.* ]]; then
      filtered+=("$f")
    fi
  done
  files_to_audit=("${filtered[@]}")
fi

if [[ ${#files_to_audit[@]} -eq 0 ]]; then
  echo -e "${YELLOW}No CV markdown documents found to audit in $target${NC}" >&2
  exit 1
fi

all_passed=true

if [[ "$json_out" == true ]]; then
  # JSON mode: aggregate into an array
  results="["
  first=true
  for file in "${files_to_audit[@]}"; do
    audit_json="$("${RUNNER[@]}" analyze "$file" --json 2>/dev/null || echo "{}")"
    score="$(echo "$audit_json" | grep -o '"score": *[0-9]*' | head -1 | awk '{print $2}' || echo "0")"
    if [[ "$score" =~ ^[0-9]+$ ]] && [[ "$min_score" -gt 0 ]] && [[ "$score" -lt "$min_score" ]]; then
      all_passed=false
    fi

    item="{\"file\": \"$file\", \"audit\": $audit_json}"
    if [[ "$first" == true ]]; then
      results+="$item"
      first=false
    else
      results+=",$item"
    fi
  done
  results+="]"
  echo "$results"
  if [[ "$all_passed" == false ]]; then
    exit 1
  fi
  exit 0
fi

# Visual formatted mode
if [[ ${#files_to_audit[@]} -gt 1 ]]; then
  echo -e "\n${BOLD}${CYAN}╔═════════════════════════════════════════════════════════════════════════════════╗${NC}"
  echo -e "${BOLD}${CYAN}║                    MARKFORGE ATS AUDIT SCOREBOARD                               ║${NC}"
  echo -e "${BOLD}${CYAN}╚═════════════════════════════════════════════════════════════════════════════════╝${NC}\n"

  printf "${BOLD}%-42s %-10s %-8s %-10s %-10s %-8s${NC}\n" "CV Document" "ATS Score" "Grade" "Verbs" "Metrics" "Status"
  printf "${DIM}%-42s %-10s %-8s %-10s %-10s %-8s${NC}\n" "------------------------------------------" "----------" "-------" "----------" "----------" "-------"

  for file in "${files_to_audit[@]}"; do
    fname="$(basename "$file")"
    if [[ ${#fname} -gt 40 ]]; then
      display_name="${fname:0:37}..."
    else
      display_name="$fname"
    fi

    audit_json="$("${RUNNER[@]}" analyze "$file" --json 2>/dev/null || echo "{}")"
    score="$(echo "$audit_json" | grep -o '"score": *[0-9]*' | head -1 | awk '{print $2}' || echo "0")"
    grade="$(echo "$audit_json" | grep -o '"grade": *"[^"]*"' | head -1 | cut -d'"' -f4 || echo "N/A")"
    verbs="$(echo "$audit_json" | grep -o '"actionVerbsCount": *[0-9]*' | head -1 | awk '{print $2}' || echo "0")"
    metrics="$(echo "$audit_json" | grep -o '"quantifiedMetricsCount": *[0-9]*' | head -1 | awk '{print $2}' || echo "0")"

    status="${GREEN}PASS${NC}"
    if [[ "$score" =~ ^[0-9]+$ ]] && [[ "$min_score" -gt 0 ]] && [[ "$score" -lt "$min_score" ]]; then
      status="${RED}FAIL${NC}"
      all_passed=false
    elif [[ "$grade" == "D" || "$score" -lt 60 ]]; then
      status="${RED}POOR${NC}"
      all_passed=false
    fi

    # Grade coloring
    grade_colored="${GREEN}${grade}${NC}"
    if [[ "$grade" == "B" ]]; then grade_colored="${CYAN}${grade}${NC}"; fi
    if [[ "$grade" == "C" ]]; then grade_colored="${YELLOW}${grade}${NC}"; fi
    if [[ "$grade" == "D" ]]; then grade_colored="${RED}${grade}${NC}"; fi

    printf "%-42s ${BOLD}%3s/100${NC}    %-16b %-10s %-10s %-8b\n" "$display_name" "$score" "$grade_colored" "$verbs" "$metrics" "$status"
  done

  echo -e "\n${DIM}Total documents audited: ${#files_to_audit[@]}${NC}"
  if [[ "$min_score" -gt 0 ]]; then
    echo -e "${DIM}Enforced minimum ATS threshold: ${min_score}/100${NC}"
  fi

  if [[ "$all_passed" == false ]]; then
    echo -e "\n${RED}✖ One or more CVs did not meet the required ATS quality threshold.${NC}"
    exit 1
  else
    echo -e "\n${GREEN}✔ All CVs passed ATS quality audit successfully!${NC}"
    exit 0
  fi
fi

# Single file detailed audit
single_file="${files_to_audit[0]}"
"${RUNNER[@]}" analyze "$single_file"

if [[ "$min_score" -gt 0 ]]; then
  audit_json="$("${RUNNER[@]}" analyze "$single_file" --json 2>/dev/null || echo "{}")"
  score="$(echo "$audit_json" | grep -o '"score": *[0-9]*' | head -1 | awk '{print $2}' || echo "0")"
  if [[ "$score" =~ ^[0-9]+$ ]] && [[ "$score" -lt "$min_score" ]]; then
    echo -e "${RED}✖ Failed: ATS score ${score}/100 is below required threshold (${min_score}).${NC}" >&2
    exit 1
  else
    echo -e "${GREEN}✔ Passed: ATS score ${score}/100 meets required threshold (${min_score}).${NC}"
  fi
fi
