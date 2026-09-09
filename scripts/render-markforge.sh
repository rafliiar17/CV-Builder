#!/usr/bin/env bash
# ==============================================================================
# render-markforge.sh — MarkForge Document Compiler for CV-Brainstormer
# ==============================================================================
# Compiles CV-Brainstormer markdown outputs to high-fidelity PDF and DOCX
# using MarkForge with deterministic template presets.
#
# Usage:
#   # Single file (template auto-detected)
#   scripts/render-markforge.sh path/to/cv-data-analyst-en.md
#
#   # Entire candidate run directory
#   scripts/render-markforge.sh output/candidates/rafli-arraafi/2026-06-01-data-analyst-application-support
#
#   # Custom template or format
#   scripts/render-markforge.sh path/to/report.md --template tech-spec --format pdf
#
# Template Mapping:
#   - cv-*.md                      -> ats-classic (100% ATS compliant, single-column)
#   - final-report-bilingual.md   -> tech-spec   (Technical RFC/benchmark styling)
#   - salary-market-*.md          -> tech-spec   (Salary tables & market callouts)
#   - star-*.md                   -> tech-spec   (STAR interview structured guide)
#   - projects-from-list.md       -> modern-accent (Portfolio with modern styling)
# ==============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"

# Color helpers
BOLD='\033[1m'
CYAN='\033[0;36m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
DIM='\033[0;2m'
NC='\033[0m'

usage() {
  cat <<EOF
${BOLD}Usage:${NC}
  $(basename "$0") <file.md | candidate-run-directory> [options]

${BOLD}Options:${NC}
  -t, --template <name>    Override template (ats-classic, tech-spec, modern-accent, academic, executive)
  -f, --format <format>    Output format: both, pdf, docx, html, all (default: both)
  -o, --outdir <dir>       Target output directory (default: same directory as input file)
  -q, --quiet              Suppress non-essential output
  -w, --watch              Watch input file and auto-rebuild on change
      --telemetry          Display compilation execution metrics & timings
      --json               Output machine-readable JSON summary
  -h, --help               Show this help message

${BOLD}Examples:${NC}
  $(basename "$0") output/candidates/rafli-arraafi/2026-06-01-data-analyst/cv/data-analyst/cv-rafli_arraafi-data-analyst-en.md
  $(basename "$0") output/candidates/rafli-arraafi/2026-06-01-data-analyst/
  $(basename "$0") output/candidates/rafli-arraafi/2026-06-01-data-analyst/reports/final-report-bilingual.md -t tech-spec -f both
EOF
}

# Resolve Bun & MarkForge CLI
resolve_markforge_cmd() {
  if [[ -n "${MARKFORGE_BIN:-}" && -x "${MARKFORGE_BIN}" ]]; then
    MARKFORGE_RUN=("${MARKFORGE_BIN}")
    return 0
  fi

  if command -v markforge >/dev/null 2>&1; then
    MARKFORGE_RUN=("markforge")
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

  if [[ -z "${bun_bin}" ]]; then
    echo -e "${RED}✖ Error: Bun runtime not found.${NC} Please install Bun (curl -fsSL https://bun.sh/install | bash) or add it to PATH." >&2
    exit 1
  fi

  local mf_dir=""
  if [[ -n "${MARKFORGE_DIR:-}" && -d "${MARKFORGE_DIR}" ]]; then
    mf_dir="${MARKFORGE_DIR}"
  elif [[ -d "/home/archy/Projects/markforge" ]]; then
    mf_dir="/home/archy/Projects/markforge"
  elif [[ -d "${ROOT_DIR}/../markforge" ]]; then
    mf_dir="$(cd "${ROOT_DIR}/../markforge" && pwd)"
  elif [[ -d "${ROOT_DIR}/markforge" ]]; then
    mf_dir="$(cd "${ROOT_DIR}/markforge" && pwd)"
  fi

  if [[ -z "${mf_dir}" || ! -f "${mf_dir}/packages/cli/src/index.ts" ]]; then
    echo -e "${RED}✖ Error: MarkForge codebase could not be found.${NC}" >&2
    echo "  Searched /home/archy/Projects/markforge and sibling directories." >&2
    echo "  Set MARKFORGE_DIR=/path/to/markforge to configure manually." >&2
    exit 1
  fi

  MARKFORGE_RUN=("${bun_bin}" "run" "${mf_dir}/packages/cli/src/index.ts")
}

detect_template() {
  local target="$1"
  local base
  base="$(basename "$target" | tr '[:upper:]' '[:lower:]')"
  local full
  full="$(cd "$(dirname "$target")" && pwd)/${base}"
  full="$(echo "$full" | tr '[:upper:]' '[:lower:]')"

  # 1. Portfolios
  if [[ "$base" == *"projects-from-list"* || "$full" == *"/portfolio/"* ]]; then
    echo "modern-accent"
    return
  fi

  # 2. CVs
  if [[ "$base" == cv-* || "$base" == "cv.md" || "$full" == *"/cv/"* ]]; then
    echo "ats-classic"
    return
  fi

  # 3. Reports & Benchmarks
  if [[ "$base" == *"final-report"* || "$base" == *"verification-report"* || "$base" == *"salary-market"* || "$base" == star-* || "$full" == *"/reports/"* || "$full" == *"/salary/"* || "$full" == *"/interview/"* ]]; then
    echo "tech-spec"
    return
  fi

  # 4. Applications & Platforms
  if [[ "$base" == cover-letter* ]]; then
    echo "ats-classic"
    return
  fi

  if [[ "$base" == email-* || "$base" == "glints.md" || "$base" == "linkedin.md" || "$base" == "upwork.md" ]]; then
    echo "tech-spec"
    return
  fi

  # Default
  echo "tech-spec"
}

# Parse options
target=""
override_template=""
format="both"
outdir=""
quiet=false
watch=false
telemetry=false
json_out=false

if [[ $# -eq 0 ]]; then
  usage
  exit 0
fi

while [[ $# -gt 0 ]]; do
  case "$1" in
    -t|--template)
      override_template="${2:-}"
      shift 2
      ;;
    -f|--format)
      format="${2:-both}"
      shift 2
      ;;
    -o|--outdir)
      outdir="${2:-}"
      shift 2
      ;;
    -q|--quiet)
      quiet=true
      shift
      ;;
    -w|--watch)
      watch=true
      shift
      ;;
    --telemetry)
      telemetry=true
      shift
      ;;
    --json)
      json_out=true
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

if [[ -z "$target" ]]; then
  echo -e "${RED}Error: Missing target file or directory.${NC}" >&2
  usage
  exit 1
fi

if [[ ! -e "$target" ]]; then
  echo -e "${RED}Error: Target does not exist: $target${NC}" >&2
  exit 1
fi

resolve_markforge_cmd

compile_file() {
  local file="$1"
  local tpl="$2"
  local target_out="${outdir:-$(dirname "$file")}"

  local build_args=("build" "$file" "-t" "$tpl" "-f" "$format" "-o" "$target_out")
  if [[ "$quiet" == true ]]; then
    build_args+=("-q")
  fi
  if [[ "$watch" == true ]]; then
    build_args+=("-w")
  fi
  if [[ "$telemetry" == true ]]; then
    build_args+=("--telemetry")
  fi
  if [[ "$json_out" == true ]]; then
    build_args+=("--json")
  fi

  "${MARKFORGE_RUN[@]}" "${build_args[@]}"
}

if [[ -d "$target" ]]; then
  # Batch directory mode
  run_dir="$(cd "$target" && pwd)"
  if [[ "$quiet" != true && "$json_out" != true ]]; then
    echo -e "${CYAN}${BOLD}⚡ MarkForge Batch Compiler${NC} for run: ${BOLD}$(basename "$run_dir")${NC}"
  fi

  # Discover files (excluding scratch and input directories)
  mapfile -t md_files < <(
    /usr/bin/find "$run_dir" -type f -name "*.md" \
      ! -path "*/scratch/*" \
      ! -path "*/input/*" \
      ! -path "*/.git/*" \
      | sort
  )

  if [[ ${#md_files[@]} -eq 0 ]]; then
    echo -e "${YELLOW}No candidate output markdown files found in $run_dir${NC}"
    exit 0
  fi

  if [[ "$quiet" != true && "$json_out" != true ]]; then
    echo -e "Found ${BOLD}${#md_files[@]}${NC} document(s) to compile.\n"
  fi

  compiled_count=0
  for f in "${md_files[@]}"; do
    tpl="${override_template:-$(detect_template "$f")}"
    if [[ "$quiet" != true && "$json_out" != true ]]; then
      rel_path="${f#$run_dir/}"
      echo -e "${DIM}→ Compiling [${tpl}]: ${rel_path}${NC}"
    fi
    compile_file "$f" "$tpl"
    compiled_count=$((compiled_count + 1))
  done

  if [[ "$quiet" != true && "$json_out" != true ]]; then
    echo -e "\n${GREEN}✔ Batch compilation finished: ${compiled_count} document(s) processed.${NC}"
  fi

else
  # Single file mode
  resolved_file="$(cd "$(dirname "$target")" && pwd)/$(basename "$target")"
  tpl="${override_template:-$(detect_template "$resolved_file")}"
  compile_file "$resolved_file" "$tpl"
fi
