#include <stdio.h>
#include "init.h"

int main(int argc, char **argv)
{
    if (argc < 2)
    {
        printf("usage: %s <root>\n", argv[0]);
    }

    char *root = argv[1];
    if (spawn_init_proc(root) < 0)
    {
        printf("spawn_init_proc() failed\n");
        return 1;
    }

    return 0;
}
