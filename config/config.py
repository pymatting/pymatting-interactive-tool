# Copyright (C) 2020-2021  Burak Martin (see 'AUTHOR' for full notice)


"""
Enable/disable parallelism, caching and nogil. The program needs to be restarted to take effect since these options
only effect numba functions which need to be recompiled.
"""

parallel = True
cache = True
nogil = True
