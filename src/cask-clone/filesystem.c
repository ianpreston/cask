#define _GNU_SOURCE
#include <stdlib.h>
#include <stdio.h>
#include <unistd.h>
#include <errno.h>
#include <sys/mount.h>
#include <sys/syscall.h>
#include "filesystem.h"

int setup_filesystem(char *root, char *pivot, char *pivot_abs)
{
    // Mark the root mount as private, so changes in this namespace are not
    // propagated up to the parent namespace
    if (mount("", "/", NULL, MS_PRIVATE|MS_REC, NULL) < 0)
    {
        printf("setup_filesystem(): Failed to mark root as private\n");
        return -1;
    }

    // Bind root to itself so we can mount it like a filesystem
    if (mount(root, root, NULL, MS_BIND|MS_REC, NULL) < 0)
    {
        printf("setup_filesystem(): Failed to bind pivot root directory\n");
        return -1;
    }

    // Use pivot_root to mount `root` as the root filesystem (/) within
    // this namespace.
    if (syscall(SYS_pivot_root, root, pivot_abs) < 0) {
        printf("setup_filesystem(): pivot_root failed: %d\n", errno);
        return -1;
    }

    if (chdir("/") < 0) {
        printf("setup_filesystem(): chdir failed\n");
        return -1;
    }

    // Unmount the pivot point (i.e. make the host's root unreachable from
    // within the container)
    if (umount2(pivot, MNT_DETACH) < 0)
    {
        printf("setup_filesystem(): umount2(): %d\n", errno);
        return -1;
    }

    return 0;
}
