add_library(blinky INTERFACE)

target_sources(blinky INTERFACE
    ${CMAKE_CURRENT_LIST_DIR}/blinky.cpp)

pico_generate_pio_header(blinky ${CMAKE_CURRENT_LIST_DIR}/blinky.pio)

target_include_directories(blinky INTERFACE ${CMAKE_CURRENT_LIST_DIR})

# Pull in pico libraries that we need
target_link_libraries(blinky INTERFACE pico_stdlib hardware_pio hardware_dma pico_graphics)
