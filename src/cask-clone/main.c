#include <stdio.h>
#include "init.h"

int main(int argc, char **argv)
{
    if (argc < 4)
    {
        printf("usage: %s <root> <pidfile> <entry point> [<argument>...]\n", argv[0]);
        return 1;
    }

    char *root = argv[1];
    char *pid_path = argv[2];
    char *entry_point = argv[3];

    char **entry_point_argv = NULL;
    if (argc >= 5)
    {
        entry_point_argv = &argv[4];
    }

    if (spawn_init_proc(root, pid_path, entry_point, entry_point_argv) < 0)
    {
        printf("spawn_init_proc() failed\n");
        return 1;
    }

    return 0;
}
