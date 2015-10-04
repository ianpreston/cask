#define _GNU_SOURCE
#include <unistd.h>
#include <stdio.h>
#include <string.h>
#include "network.h"

int setup_network(char *hostname)
{
    if (sethostname(hostname, strlen(hostname)) < 0)
    {
        printf("setup_network(): Failed to set hostname\n");
        return -1;
    }

    return 0;
}
