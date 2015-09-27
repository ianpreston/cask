#define _GNU_SOURCE
#include <stdlib.h>
#include <stdint.h>
#include <stdio.h>
#include <unistd.h>
#include <errno.h>
#include <sched.h>
#include <string.h>
#include <sys/wait.h>
#include <sys/stat.h>
#include "init.h"
#include "filesystem.h"
#include "network.h"

#define stack_size 1024 * 1024
#define clone_flags CLONE_NEWPID
#define unshare_flags (CLONE_NEWIPC | CLONE_NEWNET | CLONE_NEWNS | CLONE_NEWUTS)

int init_proc(void *root)
{
    // Build the path that will contain the filesystem pivot and
    // ensure it exists on disk
    char *pivot = "/.pivot";
    char *pivot_abs = calloc(strlen(root) + strlen(pivot) + 1, 1);
    if (pivot_abs == NULL)
    {
        printf("setup_filesystem(): calloc(): %d\n", errno);
        return 1;
    }
    strcat(pivot_abs, root);
    strcat(pivot_abs, pivot);

    if (mkdir(pivot_abs, S_IRWXU | S_IRWXG) < 0)
    {
        if (errno != EEXIST)
        {
            printf("init_proc(): mkdir(): %d\n", errno);
            return 1;
        }
    }

    // Create and enter new namespaces
    if (unshare(unshare_flags) < 0)
    {
        printf("init_proc(): unshare(): %d\n", errno);
        return 1;
    }

    if (setup_network("sub") < 0)
    {
        printf("init_proc(): setup_network() failed\n");
        return 1;
    }

    if (setup_filesystem(root, pivot, pivot_abs) < 0)
    {
        printf("init_proc(): setup_filesystem() failed\n");
        return 1;
    }

    return run_entry_point();
}

int run_entry_point()
{
    char *busybox_argv[] = { "sh", NULL };
    execvp("/busybox", busybox_argv);

    printf("run_entry_point(): execvp(): %d\n", errno);
    return -1;
}

int spawn_init_proc(char *root)
{
    void *stack = malloc(stack_size);
    if (stack == 0)
    {
        printf("spawn_init_proc(): malloc(): %d\n", errno);
        return -1;
    }
    void *stack_base = (void*)((uint64_t)stack + (uint64_t)stack_size); 

    pid_t pid = clone(init_proc, stack_base, CLONE_NEWPID | SIGCHLD, root);
    if (pid < 0)
    {
        printf("spawn_init_proc(): clone(): %d\n", errno);
        return -1;
    }

    waitpid(pid, NULL, 0);
    return 0;
}
