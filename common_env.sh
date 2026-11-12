#!/usr/bin/env bash
# ==============================================================================
# Shared environment resolver for the VANET simulation projects.
#
# Sourced by vanet_aodv/run_cmd.sh, vanet_aodv/run_gui.sh,
# vanet_gpsr/run_cmd.sh and vanet_gpsr/run_gui.sh.
#
# It only *locates* an existing toolchain; it never builds or installs anything.
# Resolution order for every framework is:
#   1. a compiled copy inside this repository (VANET-LAB/inet, /veins, /veins_inet)
#   2. the standalone installation referenced by ~/vanet-setup/vanet_env.sh
#      (INET_ROOT / VEINS_ROOT) or the usual ~/inet4.5, ~/veins-5.3.1 locations
#
# Exports after sourcing:
#   INET_DIR, VEINS_DIR, VEINS_INET_DIR
#   OPP_LIBS     -> array of "-l <lib prefix>" arguments
#   OPP_NED_PATH -> NED search path (colon separated)
# ==============================================================================

# --- OMNeT++ ------------------------------------------------------------------
if ! command -v opp_run >/dev/null 2>&1; then
    for _setenv in "$HOME/omnetpp-6.1/setenv" "$HOME/omnetpp-6.4.0/setenv" \
                   "$HOME/omnetpp-6.0/setenv" "$HOME/omnetpp-5.7/setenv"; do
        if [ -f "$_setenv" ]; then
            . "$_setenv" >/dev/null 2>&1
            break
        fi
    done
    unset _setenv
fi

# --- SUMO ---------------------------------------------------------------------
# The committed .net.xml files use vehicle classes (container, aircraft, ...)
# that were introduced after SUMO 1.18, so a recent SUMO must win over /usr/bin.
for _sumo_bin in "$HOME/sumo-venv/bin" "$HOME/sumo/bin" "$SUMO_HOME/bin"; do
    if [ -x "$_sumo_bin/sumo" ]; then
        case ":$PATH:" in
            *":$_sumo_bin:"*) ;;
            *) PATH="$_sumo_bin:$PATH" ;;
        esac
        export PATH
        break
    fi
done
unset _sumo_bin

# --- Framework libraries ------------------------------------------------------
# Print the root directory of a framework that already contains
# <root>/src/lib<NAME>.so. Candidates are tried in order.
_vanet_pick_framework() {
    local name="$1"; shift
    local dir
    for dir in "$@"; do
        [ -n "$dir" ] || continue
        [ -f "$dir/src/lib${name}.so" ] || continue
        printf "%s\n" "$dir"
        return 0
    done
    return 1
}

INET_DIR=$(_vanet_pick_framework INET \
    "$VANET_ROOT/inet" "${INET_ROOT:-}" "$HOME/inet4.5" "$VANET_ROOT/../inet4.5") || {
    echo "ERROR: no compiled INET framework found (looked for src/libINET.so)." >&2
    echo "       Build VANET-LAB/inet, or install INET to ~/inet4.5." >&2
    return 1 2>/dev/null || exit 1
}

VEINS_DIR=$(_vanet_pick_framework veins \
    "$VANET_ROOT/veins" "${VEINS_ROOT:-}" "$HOME/veins-5.3.1" "$VANET_ROOT/../veins-5.3.1") || {
    echo "ERROR: no compiled Veins found (looked for src/libveins.so)." >&2
    return 1 2>/dev/null || exit 1
}

VEINS_INET_DIR=$(_vanet_pick_framework veins_inet \
    "$VANET_ROOT/veins_inet" "${VEINS_ROOT:-}/subprojects/veins_inet" \
    "$HOME/veins-5.3.1/subprojects/veins_inet" \
    "$VANET_ROOT/../veins-5.3.1/subprojects/veins_inet") || {
    echo "ERROR: no compiled veins_inet found (looked for src/libveins_inet.so)." >&2
    return 1 2>/dev/null || exit 1
}

export INET_DIR VEINS_DIR VEINS_INET_DIR

OPP_LIBS=(
    -l "$VEINS_DIR/src/veins"
    -l "$INET_DIR/src/INET"
    -l "$VEINS_INET_DIR/src/veins_inet"
)

OPP_NED_PATH=".:$VEINS_INET_DIR/src/veins_inet:$VEINS_DIR/src/veins:$INET_DIR/src"
OPP_NED_EXCLUSIONS="$INET_DIR/.nedexclusions"
