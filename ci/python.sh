SCRIPT_PATH=${BASH_SOURCE-$0}
SCRIPT_PATH=$(dirname "$SCRIPT_PATH")
SCRIPT_PATH=$(realpath "$SCRIPT_PATH")

function qa_prepare_all {
    pip install ruff
}

function qa_check {
    ruff check --config "$SCRIPT_PATH/ruff.toml" "$1"
}

function qa_fix {
    ruff check --config "$SCRIPT_PATH/ruff.toml" --fix "$1"
}

function qa_examples_check {
    qa_check examples/
}

function qa_examples_fix {
    qa_fix examples/
}

function qa_firmware_check {
    qa_check firmware/
}

function qa_firmware_fix {
    qa_fix firmware/
}

function qa_modules_check {
    qa_check modules/
}

function qa_modules_fix {
    qa_fix modules/
}