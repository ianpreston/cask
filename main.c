#include <stdio.h>
#include "init.h"

int main(int argc, char **argv)
{
    if (argc < 3)
    {
        printf("usage: %s <root> <entry point> [<argument>...]\n", argv[0]);
        return 1;
    }

    char *root = argv[1];
    char *entry_point = argv[2];

    char **entry_point_argv = NULL;
    if (argc >= 4)
    {
        entry_point_argv = &argv[3];
    }

    if (spawn_init_proc(root, entry_point, entry_point_argv) < 0)
    {
        printf("spawn_init_proc() failed\n");
        return 1;
    }

    return 0;
}
