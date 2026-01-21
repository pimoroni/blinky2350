#include <cstdlib>
#include <limits>
#include <new>
#include <iostream>
#include <cstdint>

#ifndef MPTALLOCATOR_H
#define MPTALLOCATOR_H

extern "C" {
    extern uint64_t mp_allocator_allocs;
    extern bool debug_show_individual_allocs;
#include "py/runtime.h"
    extern void *m_tracked_calloc(size_t nmemb, size_t size);
    extern void m_tracked_free(void *ptr_in);
}

template<class T>
struct MPAllocator
{
    typedef T value_type;

    MPAllocator() = default;

    template<class U>
    constexpr MPAllocator(const MPAllocator <U>&) noexcept {}

    [[nodiscard]] T* allocate(std::size_t n)
    {
        //if (n > std::numeric_limits<std::size_t>::max() / sizeof(T))
        //    throw std::bad_array_new_length();

        //if (auto p = static_cast<T*>(std::malloc(n * sizeof(T))))
        //if (auto p = static_cast<T*>(m_tracked_calloc(n, sizeof(T))))
        if (auto p = static_cast<T*>(m_malloc(n * sizeof(T))))
        {
            mp_allocator_allocs++;
            report(p, n);
            return p;
        }
        // TODO: Handle failed allocations gracefully here, somehow.
        // Right now we will just keep on rollin' causing further issues,
        // but at least printing out the failure stops things from melting
        //printf("MPAllocator: Failed to allocate %lu bytes!\n", n);
        mp_raise_msg_varg(&mp_type_RuntimeError, MP_ERROR_TEXT("Failed to allocate %lu bytes!"), n);
        return NULL;

        //throw std::bad_alloc();
    }

    void deallocate(T* p, std::size_t n) noexcept
    {
        report(p, n, 0);
        //std::free(p);
        //m_tracked_free(p);
#if MICROPY_MALLOC_USES_ALLOCATED_SIZE
        m_free(p, n);
#else
        m_free(p);
#endif
    }

private:
    void report(T* p, std::size_t n, bool alloc = true) const
    {
        if(!debug_show_individual_allocs) {
            return;
        }
        std::cout << (alloc ? "Alloc: " : "Dealloc: ") << sizeof(T) * n
                  << " bytes at " << std::hex << std::showbase
                  << reinterpret_cast<void*>(p) << std::dec << std::endl;
    }
};

template<class T, class U>
bool operator==(const MPAllocator <T>&, const MPAllocator <U>&) { return true; }

template<class T, class U>
bool operator!=(const MPAllocator <T>&, const MPAllocator <U>&) { return false; }

#endif // MPTALLOCATOR_H
