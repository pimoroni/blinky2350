add_library(usermod_blinky INTERFACE)

get_filename_component(REPO_ROOT "${CMAKE_CURRENT_LIST_DIR}/../../" ABSOLUTE)

target_sources(usermod_blinky INTERFACE
    ${CMAKE_CURRENT_LIST_DIR}/blinky.c
    ${CMAKE_CURRENT_LIST_DIR}/blinky.cpp
    ${CMAKE_CURRENT_LIST_DIR}/driver/blinky.cpp
)

target_include_directories(usermod_${MOD_NAME} INTERFACE
    ${REPO_ROOT}
    ${PIMORONI_PICO_PATH}
    ${CMAKE_CURRENT_LIST_DIR}
    ${PIMORONI_PICO_PATH}/libraries/pico_graphics/
)

set_source_files_properties(
    ${CMAKE_CURRENT_LIST_DIR}/blinky.c
    PROPERTIES COMPILE_FLAGS
    "-Wno-discarded-qualifiers -Wno-implicit-int"
)

pico_generate_pio_header(usermod_blinky ${CMAKE_CURRENT_LIST_DIR}/driver/blinky.pio)

set_source_files_properties(${CMAKE_CURRENT_LIST_DIR}/driver/blinky.cpp PROPERTIES COMPILE_OPTIONS "-O2;-fgcse-after-reload;-floop-interchange;-fpeel-loops;-fpredictive-commoning;-fsplit-paths;-ftree-loop-distribute-patterns;-ftree-loop-distribution;-ftree-vectorize;-ftree-partial-pre;-funswitch-loops")

target_link_libraries(usermod INTERFACE usermod_blinky)